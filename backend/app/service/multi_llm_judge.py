from datetime import datetime
import json
import dspy
from typing import Iterable, Literal, List, Dict, Any
from minio import Minio
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
import os
from app.middleware.log import logger as log
from app.dao.result_dao import ResultQueryDao, ResultOperateDao
from app.dao.models.sqlite_gen import MultiResult

client = Minio(
    endpoint="183.66.251.10:39000",
    access_key="qHGNbLRWtJcfJsDkl3LK",
    secret_key="qmkA57ujunxw2cEpmPCVfsHKtXdbRAfv0SYvtdQC",
    secure=False,
)

def put_file(file, bucket_name, level1_dir, level2_dir, level3_dir):
    """
    上传文件到指定的 MinIO bucket
    """
    file_name = os.path.basename(file)  # 获取文件名
    found = client.bucket_exists(bucket_name)  # 检查 bucket 是否存在
    if not found:
        client.make_bucket(bucket_name)  # 创建 bucket

    # 生成包含两级目录的路径
    object_name = f"{level1_dir}/{level2_dir}/{level3_dir}/{file_name}"

    # 上传文件到指定路径
    client.fput_object(
        bucket_name=bucket_name,
        object_name=object_name,
        file_path=file
    )
    return f"{bucket_name}/{object_name}"

class SingleTurnEvalSignature(dspy.Signature):
    """评估智慧座舱大模型在单轮对话中的指令遵循能力。

    详细分析每轮对话中:

    1、语音回复的准确性和相关性，确保系统回答符合用户需求，信息完整且与用户问题紧密相关。

    2、界面操作的执行效果，检查系统是否能够正确地完成界面操作，并符合用户预期。

    3、用户意图的理解程度，评估系统对用户指令或问题的理解是否准确，无明显误解或偏离。

    4、交互的自然流畅度，判断系统的语音回复是否自然流畅，避免生硬或不连贯的表达。
    """

    dialogue_history: List[Dict[str, Any]] = dspy.InputField(desc="对话历史记录")
    user_command: str = dspy.InputField(desc="用户的指令或问题")
    system_response: str = dspy.InputField(desc="系统的语音回复，用于评估回复的准确性和相关性")
    image_uses: List[dspy.Image] = dspy.InputField(
        desc="执行指令后的界面截图，用于分析界面状态是否符合用户指令后的状态预期，支持多张截图"
    )
    expected_behavior: str = dspy.InputField(desc="预期的智慧座舱行为，包括语音回复内容和界面操作结果")

    eval_result: Literal["通过", "失败", "不确定"] = dspy.OutputField(
        desc="评估结果:通过(指令执行正确)/失败(执行错误)/不确定(无法判断)"
    )
    eval_reason: str = dspy.OutputField(desc="详细的评估理由，包含语音和界面分析")
    eval_confidence: float = dspy.OutputField(desc="评估结果的置信度(0-1)")


class DialogueSessionEvalSignature(dspy.Signature):
    """评估整个多轮（至少1轮）对话会话的质量。

        #  单轮对话：依据下面 认知操作步骤 以及 裁决规则 完成评定并详细输出分析原因
        ## 认知操作步骤
        1. 目标明确: 清晰定义目标或预期的常识性结果
        2. 问题分解: 将问题分解为关键组成部分和相关因素
        3. 信息过滤: 分析文本和图片,专注于最重要的常识要素,忽略无关细节
        4. 重新组织: 最终评判结果根据系统回应和图片对比这两点的结果综合分析。文本/图片有一个符合预期结果，可推测：车机已正确执行指令，可视最终结果为：通过。
        5. 模式识别: 识别与其他常识场景或先例的相似之处
        6. 抽象提取: 提取可应用于此情况的更广泛常识原则
        7. 归纳推广: 将识别的原则应用于当前场景和潜在的未来案例
        8. 整合总结: 将所有视角和原则整合为最终的常识性决定，并详细输出判断原因。

        ## 裁决规则:
        1. 避免位置偏差：独立评估每个回答，确保回答顺序不影响判断。
        2. 质量优先原则：注重回答的相关性和质量，不以回答长度为标准。一条有效回答应准确满足用户需求，而非单纯详尽。例如，系统回复“好的 ...”、“OK”等，应倾向于认为它已正确响应并在积极推动用户需求的实现，可视为合格响应。
        3. 最佳解释法则：如果系统的回答表明已识别用户问题或指令，则假设屏幕上展示了相关信息或操作结果，应该视为系统已完成工作，并遵循“最佳解释法则”。当车机前后截图无明显变化时，若车机回复符合预期描述，则可推测最终结果符合预期；若车机回复完全不符合预期描述，但是车机屏幕截图变化显示，车机正确响应了文本预料中的问题，则可推断最终结果符合预期。
        4. 容错与纠错：确认系统是否准确回应提问或正确执行指令。如有轻微误差，考察系统是否能通过后续互动快速弥补，例如在初次误解后及时调整，则视为合格。
        5. 情境适应性：判断系统是否能因应具体情境调整响应，尤其在复杂或多重指令下，确保具备合理应变能力。
        6. 公平审慎：对智驾系统的回应保持公平，避免草率或苛刻评价；在系统提供合理的引导时，倾向认为其已正确响应并在推动用户需求的实现。
        7. 图片分析准则：
            - **准确性**: 系统能否准确描述图片中的内容及其变化。
            - **一致性**: 描述的内容是否与图片一致，无明显错误。
            - **详细程度**: 系统提供的描述是否足够详细，能够帮助理解图片的变化。
            - **相关性**: 描述的内容是否与用户的问题或指令直接相关。
        8. 情感分析： 当用户问题无明确指令，为情感表达时，若车机前后截图无明显变化，为正常现象，结合情感语境给予积极回复即可倾向于车机已正确响应


        #多轮对话：在依据 认知操作步骤 和 裁决规则 的基础上多考虑多轮对话的合理性，遵从下方综合分析以及注意事项并详细输出分析原因
        ##综合分析:

        指令理解和执行的准确率，包括是否准确理解用户的需求和正确执行操作。

        多轮对话的连贯性，检查系统是否能够持续保持对话的上下文，理解用户的连续请求。

        系统响应的一致性，确保在不同轮次中系统的响应逻辑一致，尤其是同一主题下的连续对话。

        整体交互体验，评估对话的自然流畅程度，以及系统与用户的互动是否令人满意。

        ##注意事项:

        多轮对话中的指令遵循：多轮对话中的指令遵循准确率是否随着轮次的增加保持稳定，是否存在显著下降或偏差。

        多轮对话中的指令保持：后续轮次中是否能继续遵循前一轮成功执行的指令或主题，确保对话的连续性和一致性。

        多轮对话中的自我纠正：如果之前的回答中存在错误，系统是否能够在后续对话中主动进行自我纠正。

        用户意图的正确追踪：在多轮对话中，系统是否能够持续准确地追踪用户意图，避免误解或偏离。

        动态调整：系统在面对用户需求变化时，是否能够灵活调整响应策略并继续保持对话流畅。
    """

    single_turn_evals: List[Dict[str, Any]] = dspy.InputField(desc="各轮对话的评估结果")

    session_result: Literal["通过", "失败"] = dspy.OutputField(desc="会话整体评估结果")
    session_reason: str = dspy.OutputField(desc="总体评价理由")
    command_success_rate: float = dspy.OutputField(desc="成功执行指令的比率：成功执行的轮次/总轮次")

class CockpitAssistantEvaluator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.single_turn_eval = dspy.ChainOfThought(SingleTurnEvalSignature)
        self.session_eval = dspy.ChainOfThought(DialogueSessionEvalSignature)

    def forward(self, messages: Iterable[ChatCompletionMessageParam]):
        single_turn_evals = []

        # 逐轮评估
        for i in range(0, len(messages) - 1, 2):
            # 获取对话历史
            dialogue_history = messages[:i] if i > 0 else []

            # 获取当前轮次的用户和系统消息
            user_message = messages[i]
            assistant_message = messages[i + 1]

            try:
                # 提取文本内容
                user_text = next(
                    (item["text"] for item in user_message["content"] if item["type"] == "text"), "无文本内容"
                )
                assistant_text = next(
                    (item["text"] for item in assistant_message["content"] if item["type"] == "text"), "无文本内容"
                )

                # 提取界面截图URL
                image_urls = [
                    item["image_url"]["url"]
                    for item in assistant_message["content"]
                    if item["type"] == "image_url"
                ]

                if len(image_urls) < 2:
                    raise ValueError("缺少必要的两张界面截图")

                # 执行单轮评估
                eval_result = self.single_turn_eval(
                    dialogue_history=dialogue_history,
                    user_command=user_text,
                    system_response=assistant_text,
                    image_uses=[dspy.Image.from_url(url=url) for url in image_urls[:2]],
                    expected_behavior=user_message["content"][0].get("expected_result", ""),
                )
            except Exception as e:
                raise Exception(f"评估第{i // 2 + 1}轮对话时出错: {str(e)}")

            single_turn_evals.append(
                {
                    "turn_num": (i // 2) + 1,
                    "eval_result": eval_result.eval_result,
                    "eval_reason": eval_result.eval_reason,
                    "eval_confidence": eval_result.eval_confidence,
                }
            )

        # 会话整体评估
        session_eval_result = self.session_eval(single_turn_evals=single_turn_evals)

        save_evaluation_results(messages, single_turn_evals, session_eval_result)

        return single_turn_evals, session_eval_result


def save_evaluation_results(
    messages, single_turn_evals, session_eval_result, output_path=os.path.join(os.path.expanduser("~"), ".cache", "evaluation_results.jsonl")
):
    """保存评估结果到文件，以jsonl格式追加写入"""
    results = {
        "messages": messages,
        "single_turn_evaluations": single_turn_evals,
        "session_evaluation": {
            "result": session_eval_result.session_result,
            "reason": session_eval_result.session_reason,
            "success_rate": session_eval_result.command_success_rate,
        },
        "timestamp": datetime.now().isoformat(),
    }

    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(results, ensure_ascii=False) + "\n")

def print_evaluation_results(result_list, multi_result, single_turn_evals, session_eval_result):
    """格式化打印评估结果"""
    print("\n=== 智慧座舱大模型指令遵循能力评估 ===")

    print("\n--- 各轮对话评估 ---")
    num = 0
    for eval_result in single_turn_evals:
        # print(f"\n第 {eval_result['turn_num']} 轮:")
        # print(f"结果: {eval_result['eval_result']}")
        # print(f"理由: {eval_result['eval_reason']}")
        # print(f"置信度: {eval_result['eval_confidence']:.2f}")
        res = eval_result['eval_result']
        if res == "通过":
            update_data = {"result": "通过", "score": 10}
        elif res == "失败":
            update_data = {"result": "不通过", "score": 0}
        else:
            update_data = {"result": "不确定", "score": 5}
        ResultOperateDao.updateTestResult(result_list[num]["result_id"], update_data)
        num += 1
        log.info(f"\n第 {eval_result['turn_num']} 轮: 结果: {res} 理由: {eval_result['eval_reason']} 置信度: {eval_result['eval_confidence']:.2f}")

    log.info("\n--- 整体会话评估 ---")
    # print(f"最终结果: {session_eval_result.session_result}")
    # print(f"评估理由: {session_eval_result.session_reason}")
    # print(f"指令执行成功率: {session_eval_result.command_success_rate:.2%}")
    update_multi_res = {
        "result": session_eval_result.session_result,
        "reason": session_eval_result.session_reason,
        "success_rate": session_eval_result.command_success_rate
    }
    ResultOperateDao.updateMultiResult(multi_result.id, update_multi_res)
    
    log.info(f"最终结果: {session_eval_result.session_result} 评估理由: {session_eval_result.session_reason} 指令执行成功率: {session_eval_result.command_success_rate:.2%}")


def multi_llm_judge_result(result_list, multi_result):
    """  
    输入为结果列表
    [{},{}]
    """  

    lm = dspy.LM(
        "openai/WestGenesis-LLM",
        cache=False,
        api_key="4030cf3413434fbad5c7563005b73a",
        api_base="http://183.66.251.10:38000/v1",
    )
    dspy.configure(lm=lm)

    # 初始化评估器
    evaluator = CockpitAssistantEvaluator()

    messages = []
    for result in result_list:
        user_question = result["user_question"]
        expected_behavior = result["expected_behavior"]
        asr_response = result["asr_response"]
        pre_interaction_screenshot = result["pre_interaction_screenshot"]
        post_interaction_screenshot = result["post_interaction_screenshot"]
        project_id = result["project_id"]
        turn_id = result["turn_id"]
        corpus_id = result["corpus_id"]
        image_url1 = put_file(post_interaction_screenshot, "picture", project_id, turn_id, corpus_id)
        image_url2 = put_file(pre_interaction_screenshot, "picture", project_id, turn_id, corpus_id)
        log.info(f" 项目id={project_id} # 轮次={turn_id} # 语料文本/用户指令={user_question} TEXT send to llm : 车机回复={asr_response}, 期望结果={expected_behavior}, 图片路径={post_interaction_screenshot}")
        user = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_question,
                },
                {
                    "type": "text",
                    "text": expected_behavior,
                }
            ],
        }
        car = {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": asr_response,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"http://183.66.251.10:39000/{image_url1}",
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"http://183.66.251.10:39000/{image_url2}",
                    },
                }
            ],
        }
        messages.append(user)
        messages.append(car)

    # 执行评估
    single_turn_evals, session_eval_result = evaluator.forward(messages)

    # 输出结果
    print_evaluation_results(result_list, multi_result, single_turn_evals, session_eval_result)