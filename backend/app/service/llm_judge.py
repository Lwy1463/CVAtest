import os.path

from openai import OpenAI
import re
import base64
from app.middleware.log import logger as log
from app.config import globalAppSettings, LLMJudge_Queue, Queue_lock
import time
from app.dao.result_dao import ResultOperateDao
from app.dao.plan_dao import PlanQueryDao, PlanOperateDao
from app.dao.project_dao import ProjectQueryDao
from app.dao.result_dao import ResultQueryDao, ResultOperateDao
from app.dao.corpus_dao import CorpusQueryDao
from app.dao.play_config_dao import PlayConfigQueryDao
from app.dao.models.sqlite_gen import MultiResult
from .multi_llm_judge import multi_llm_judge_result
import dspy
from typing import Literal, Optional

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


class LLMJudge:
    llm_client = OpenAI(api_key=globalAppSettings.OPENAI_API_KEY, base_url=globalAppSettings.OPENAI_API_BASE)


    # 返回分数和分析原因 str, str
    def judge(self, user_content, image_link):
        # Ensure all input contents are strings to avoid errors
        user_content = str(user_content) if user_content else ""
        image_link = str(image_link) if image_link else ""

        if not os.path.exists(image_link):
            return "0", ""

        system_prompt = """你是一个公正、客观的裁判，你的任务是对user和image的匹配度进行评分。user代表乘客的指令，image代表车机针对乘客的指令进行操作后的图片。
            你能很好地判断user的指令，并结合image判断车机的操作是否符合命令。
            你应该从以下几个方面进行评分：1. 相关性；2. 准确性。
            分数的范围在1到10之间。
            当image显示的操作与user的命令相匹配时，给出10分。
            当image显示的操作与user的命令完全不匹配时，给出1分。
            若你无法判断image和user指令之间的相关性，给出0分。

            **请注意， 你的综合评分只有10和0这两个分数，不可给出其他的分数值!**

            ```EXAMPLE
            示例1：
                user: '打开车窗'
                image: '此处的图片显示车窗是打开状态'
            打分：
                综合评分: '10'
                分析理由: '车机正确地执行了用户指令，且图片显示车窗为打开状态，虽然回复简单，但完全符合用户期望。符合相关性、准确性。'

            示例2:
                user: '关闭车窗'
                image: '此处的图片显示车窗是打开状态'
            打分：
                综合评分: '1'
                分析理由: '用户的指令是关闭车窗，但图片显示车窗为打开状态，完全偏离了用户的期望。不符合相关性、准确性。'

            示例3:
                user: '导航到附近停车场'
                image: '此处的图片显示车机界面为导航应用中，并且展示了几个附近可选的停车场'
            打分：
                综合评分: '10'
                分析理由: '用户的指令是导航到附近停车场，而车机正确的识别并响应了该指令，在导航应用中搜索了附近可用的停车场'
            ```

            最后请必须按照以下格式返回数据：「综合评分:'此次用分数替代' 分析理由:'此次用分析理由替代'」
            """

        base64_image = encode_image(image_link)

        chat_response = self.llm_client.chat.completions.create(
            model="WestGenesis-LLM",
            messages=[
                {
                    "role": "user",
                    "content": f"System Prompt: {system_prompt}\n"
                },
                {
                    "role": "user",
                    "content": f"user: {user_content}\n"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "low"
                            }
                        }
                    ]
                },
            ],
            temperature=0,
            seed = 200
        )

        choice = chat_response.choices[0] if chat_response.choices else None

        if choice:
            content = choice.message.content
            print(f'{content = }')
            # Extract score and analysis reason from content
            pattern = r"综合评分[：:]\s*['\"]?(\d+?)['\"]?(?:\s*分)?\s*分析理由[：:]\s*['\"]?(.*)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                score = match.group(1)
                analysis_reason = match.group(2)
                return score, analysis_reason
        return "0", ""


    def judge_by_text(self, user_content, car_content):
        # Ensure all input contents are strings to avoid errors
        user_content = str(user_content) if user_content else ""
        car_content = str(car_content) if car_content else ""

        chat_response = self.llm_client.chat.completions.create(
            model="WestGenesis-LLM",
            messages=[{"role": "system",
                       "content": """你是一个公正、客观的裁判，你的任务是对user和car的对话进行评分。
                        user代表乘客的问题，car代表车机的回答。你能很好地判断user给car的指令，并判断car的回复是否正确。你应该从以下几个方面进行评分：1. 相关性；2. 准确性；3. 完整性；4. 简洁性。
                        分数的范围在1到10之间。
                        当car的回答对user对问题完全准确，且符合完整性和简洁性时，可以给出9到10分之间的分值。
                        当car针对user的问题给出正确的确答案，但较为啰嗦时，此时不符合简洁性，可以给出7分到8分之间的分值。
                        当car的回答与user问题相关时，但并没有直面回答，而是附加了一些细节或解释，则可以给出5到7分之间的分值。
                        如果car的回复完全偏离了用户的需求或不符合预期，则给出1到3分之间的分值。

                        ```EXAMPLE
                        示例1：
                            user: '打开车窗'
                            car: '车窗已打开'
                        打分：
                            综合评分: '10' 分析理由: '车机正确地执行了用户指令，虽然回复简单，但完全符合用户期望。符合相关性、准确性、完整性、简洁性。'

                        示例2:
                            user: '打开车窗'
                            car: '空调已打开'
                        打分：
                            综合评分: '1' 分析理由: '车机的回复偏离了用户的意图，没有执行用户要求的操作。不符合相关性、准确性、完整性、简洁性。'

                        示例3:
                            user: '成年人每天应饮用至少8杯水以保持身体水分平衡吗？'
                            car: '关于每天应该喝多少水，有一种普遍的建议是成年人每天应该饮用大约8杯水（约2升）。这个建议有时被称作“8x8规则”，即每天8次8盎司（约240毫升）的水。然而，这只是一个大致的指导原则，并不是每个人都需要严格遵守这个量。'
                        打分：
                            综合评分: '7' 分析理由: '车机回答了相关信息，符合评分标准的相关性，并且回答也肯定了用户输入的问题。但是回答较为啰嗦，并且没有直接回答用户的问题，可以适当扣分。'
                        ```

                        最后请按照以下格式返回数据「综合评分:'此次用分数替代' 分析理由:'此次用分析理由替代'」"""},
                      {"role": "user", "content": user_content},
                      {"role": "car", "content": car_content}],
            temperature=0,
            seed = 200
        )
        choice = chat_response.choices[0] if chat_response.choices else None

        if choice:
            content = choice.message.content
            print(f'{content = }')
            # Extract score and analysis reason from content
            pattern = r"综合评分[：:]\s*['\"]?(\d+?)['\"]?(?:\s*分)?\s*分析理由[：:]\s*['\"]?(.*)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                score = match.group(1)
                analysis_reason = match.group(2)
                return score, analysis_reason
        return "0", ""


    def judge_image2(self, user_content, image_link1, image_link2):
        # Ensure all input contents are strings to avoid errors
        user_content = str(user_content) if user_content else ""
        image_link1 = str(image_link1) if image_link1 else ""
        image_link2 = str(image_link2) if image_link2 else ""

        if not os.path.exists(image_link1) or not os.path.exists(image_link2):
            return "0", ""

        system_prompt = """
        你是一个公正、客观的裁判，你的任务是对user和image的匹配度进行评分。user代表乘客的指令，image代表车机针对乘客的指令进行操作后的图片。
        image有两张图片，你需要对两张图片都进行分析。
        你能很好地判断user的指令，并结合image判断车机的操作是否符合命令。
        你应该从以下几个方面进行评分：1. 相关性；2. 准确性。
        分数的取值为0分和10分。

        当**其中一张**image显示的操作与user的命令相匹配时，即可给出10分。
        只有当**两张image显示的操作与user的命令都完全不匹配时**，才给出0分。

        **请注意， 你的综合评分只有10和0这两个分数，不可给出其他的分数值!**

        ```EXAMPLE
        示例1：
            user: '打开车窗'
            image1: '此处的图片显示车窗是打开状态'
            image2: '此处的图片是车载屏幕'
        打分：
            综合评分: '10'
            分析理由: '车机正确地执行了用户指令，且其中一张图片显示车窗为打开状态。符合相关性、准确性。'

        示例2:
            user: '关闭车窗'
            image1: '此处的图片显示车窗是打开状态'
            image2: '此处的图片是车载屏幕'
        打分：
            综合评分: '0'
            分析理由: '用户的指令是关闭车窗，但图片显示车窗为打开状态和车载屏幕，完全偏离了用户的期望。不符合相关性、准确性。'

        示例3:
            user: '关闭车窗'
            image1: '此处的图片显示车载屏幕'
            image2: '此处的图片显示空调图片'
        打分：
            综合评分: '0'
            分析理由: '用户的指令是关闭车窗，但图片显示为车载屏幕和空调图片，完全偏离了用户的期望。不符合相关性、准确性。'
        ```

        最后请必须按照以下格式返回数据：「综合评分:'此次用分数替代' 分析理由:'此次用分析理由替代'」
    """

        base64_image1 = encode_image(image_link1)
        base64_image2 = encode_image(image_link2)

        chat_response = self.llm_client.chat.completions.create(
            model="WestGenesis-LLM",
            messages=[
                {
                    "role": "user", 
                    "content": f"System Prompt: {system_prompt}\n"
                },
                {
                    "role": "user",
                    "content": f"user: {user_content}\n"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image1}",
                                "detail": "low"
                            }
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image2}",
                                "detail": "low"
                            }
                        }
                    ]
                },
            ],
            temperature=0,
            seed = 200
        )

        choice = chat_response.choices[0] if chat_response.choices else None

        if choice:
            content = choice.message.content
            print(f'{content = }')
            # Extract score and analysis reason from content
            pattern = r"综合评分[：:]\s*['\"]?(\d+?)['\"]?(?:\s*分)?\s*分析理由[：:]\s*['\"]?(.*)"
            # pattern = r"Overall Score[：:]\s*['\"]?(\d+?)['\"]?\s*Reason[：:]\s*['\"]?(.*)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                score = match.group(1)
                analysis_reason = match.group(2)
                return score, analysis_reason
        return "0", ""

class EvaluateSmartCockpitSignature(dspy.Signature):
    """您是中国汽车技术研究中心的首席技术官，请作为一个公正的裁判，评估智能驾驶系统对用户提问或指令的回答质量。您应根据**裁决规则**，评估系统是否通过有效且高效的互动提供了正确的回答或响应。

    请遵循以下认知步骤，系统地评估智能驾驶系统对用户提问或指令的回答质量。在进入每个新步骤之前，请提供详细的推理和解释。

    ## 认知操作步骤
        1. 目标明确: 清晰定义目标或预期的常识性结果
        2. 问题分解: 将问题分解为关键组成部分和相关因素
        3. 信息过滤: 分析文本和图片,专注于最重要的常识要素,忽略无关细节
        4. 重新组织: 在最高视角，即最终评判结果=文本对比结果+图片分析结果，最终评判结果根据系统回应和图片对比这两点的结果综合分析
        5. 模式识别: 识别与其他常识场景或先例的相似之处
        6. 抽象提取: 提取可应用于此情况的更广泛常识原则
        7. 归纳推广: 将识别的原则应用于当前场景和潜在的未来案例
        8. 整合总结: 将所有视角和原则整合为最终的常识性决定

    ## 裁决规则:
        1. 避免位置偏差：独立评估每个回答，确保回答顺序不影响判断。
        2. 质量优先原则：注重回答的相关性和质量，不以回答长度为标准。一条有效回答应准确满足用户需求，而非单纯详尽。例如，系统回复“好的 ...”、“OK”等，应倾向于认为它已正确响应并在积极推动用户需求的实现，可视为合格响应。
        3. 最佳解释法则：如果系统的回答表明已识别用户问题或指令，则假设屏幕上展示了相关信息或操作结果，应该视为系统已完成工作，并遵循“最佳解释法则”。
        4. 容错与纠错：确认系统是否准确回应提问或正确执行指令。如有轻微误差，考察系统是否能通过后续互动快速弥补，例如在初次误解后及时调整，则视为合格。
        5. 情境适应性：判断系统是否能因应具体情境调整响应，尤其在复杂或多重指令下，确保具备合理应变能力。
        6. 公平审慎：对智驾系统的回应保持公平，避免草率或苛刻评价；在系统提供合理的引导时，倾向认为其已正确响应并在推动用户需求的实现。
        7. 图片分析准则：
            - **准确性**: 系统能否准确描述图片中的内容及其变化。
            - **一致性**: 描述的内容是否与图片一致，无明显错误。
            - **详细程度**: 系统提供的描述是否足够详细，能够帮助理解图片的变化。
            - **相关性**: 描述的内容是否与用户的问题或指令直接相关。
    """

    user_question: str = dspy.InputField(prefix="用户问题", desc="用户提问或指令或闲聊")

    expected_behavior: str = dspy.InputField(
        prefix="预期结果:", desc="预期的智驾系统行为或响应"
    )

    asr_response: str = dspy.InputField(
        prefix="车机回答", desc="ASR识别的智能驾驶系统语音回复"
    )

    pre_interaction_screenshot: Optional[dspy.Image] = dspy.InputField(
        desc="指令前屏幕截图"
    )
    post_interaction_screenshot: Optional[dspy.Image] = dspy.InputField(
        desc="指令后屏幕截图"
    )


    judgment: Literal["Correct", "Incorrect", "Uncertain"] = dspy.OutputField(
        prefix="判断", desc="系统响应的最终评定结果（正确、错误、不确定）"
    )

    reasoning: str = dspy.OutputField(
        prefix="解释", desc="对最终评定结果的解释说明"
    )


class EvaluateSmartCockpit(dspy.Module):
    def __init__(self):
        super().__init__()
        self.judgment = dspy.ChainOfThought(EvaluateSmartCockpitSignature)

    def forward(
            self,
            user_question,
            expected_behavior,
            asr_response,
            pre_interaction_screenshot=None,
            post_interaction_screenshot=None,
    ):
        judgment = self.judgment(
            user_question=user_question,
            expected_behavior=expected_behavior,
            asr_response=asr_response,
            pre_interaction_screenshot=pre_interaction_screenshot,
            post_interaction_screenshot=post_interaction_screenshot,
        )

        final_reasoning = f"{judgment.reasoning}"

        return dspy.Prediction(
            judgment=judgment.judgment,
            reasoning=final_reasoning,
        )

def llm_judge_result():
    client = OpenAI(api_key=globalAppSettings.OPENAI_API_KEY, base_url=globalAppSettings.OPENAI_API_BASE)
    models = client.models.list()
    model = models.data[0].id

    lm = dspy.LM(
        f"openai/{model}",
        cache=False,
        api_key=globalAppSettings.OPENAI_API_KEY,
        api_base=globalAppSettings.OPENAI_API_BASE,
        seed=200,
    )
    dspy.configure(lm=lm)

    evaluate_program = EvaluateSmartCockpit()

    current_plan = ""
    turn_id = -1
    project = {}
    project_excel = False
    while True:
        if not LLMJudge_Queue.empty():
            Queue_lock.acquire()
            test_result = LLMJudge_Queue.get()  # 从队列中取出 Data 对象
            Queue_lock.release()
            if isinstance(test_result, list):
                input_data = []
                for get_res in test_result[:-1]:
                    temp = {
                        "result_id": get_res.result_id,
                        "user_question": get_res.text,
                        "expected_behavior": get_res.expect_result,
                        "asr_response": get_res.asr_result,
                        "pre_interaction_screenshot": get_res.image,
                        "post_interaction_screenshot": get_res.image[:-10] + "1.jpg",
                        "project_id": get_res.project_id,
                        "turn_id": get_res.project_id,
                        "corpus_id": get_res.corpus_id
                    }
                    input_data.append(temp)
                if isinstance(test_result[-1], MultiResult):
                    multi_llm_judge_result(input_data, test_result[-1])

                LLMJudge_Queue.task_done()
                continue

            corpus =  CorpusQueryDao.findTestCorpusById(test_result.corpus_id)
            update_data = {}
            if corpus == None: # 没找到测试语料则判断为唤醒场景
                if test_result.asr_result != "":
                    update_data = {"result": "通过", "score": 10}
                else:
                    update_data = {"result": "未通过", "score": 0}
                ResultOperateDao.updateTestResult(test_result.result_id,update_data)
                # continue
            else:
                show_project = ProjectQueryDao.findTestProjectById(test_result.project_id)
                show_plan = PlanQueryDao.findProjectPlanById(test_result.plan_id)
                image1 = test_result.image
                image2 = image1[:-10] + "1.jpg"
                log.info(f" 项目名={show_project.project_name} # 方案名={show_plan.plan_name} # 轮次={test_result.turn_id} # 语料文本/用户指令={test_result.text} TEXT send to llm : 车机回复={test_result.asr_result}, 期望结果={corpus.expect_result}, 图片1路径={image1}, 图片2路径={image2}")
                judgment = evaluate_program.forward(
                    user_question=test_result.text,
                    expected_behavior=corpus.expect_result,
                    asr_response=test_result.asr_result,
                    pre_interaction_screenshot=image1,
                    post_interaction_screenshot=image2,
                )
                log.info(f" 项目名={show_project.project_name} # 方案名={show_plan.plan_name} # 轮次={test_result.turn_id} # 语料文本={test_result.text} TEXT llm result judge : {judgment}")
                
                res = judgment["judgment"]
                if res == "Correct":
                    update_data = {"result": "通过", "score": 10}
                elif res == "Incorrect":
                    update_data = {"result": "不通过", "score": 0}
                else:
                    update_data = {"result": "不确定", "score": 5}
                    
                ResultOperateDao.updateTestResult(test_result.result_id,update_data)

            LLMJudge_Queue.task_done()  # 标记任务已完成
            if current_plan != test_result.plan_id:
                current_plan = test_result.plan_id
                turn_id = test_result.turn_id
                project_excel = False
            time.sleep(1)
        elif LLMJudge_Queue.empty() and current_plan != "":
            plan = PlanQueryDao.findProjectPlanById(current_plan)
            if plan.plan_status == "completed" and project_excel == False:
                statistic_data(plan.plan_id, plan.play_config_id, turn_id)
                current_plan = ""
                project_excel = True
            time.sleep(1)
        else:
            # print("队列为空，等待数据...")
            time.sleep(1)  # 等待队列中有数据「

def statistic_data(plan_id, play_config_id, turn_id):
    data = {"play_config_id": play_config_id}
    starconfig = PlayConfigQueryDao.showAllStartConfig(data)
    config = starconfig[0]
    # 获取数据
    data = {"plan_id": plan_id, "turn_id": turn_id}
    result_list = ResultQueryDao.showAllTestResult(data)

    num = 0
    wakeup_time_sum = 0
    wakeup_success_rate_sum = 0
    false_wakeup_times_sum = 0
    interaction_success_rate_sum = 0
    word_recognition_rate_sum = 0
    response_time_sum = 0
    for result in result_list:
        num += 1
        if config.wakeup_time:
            wakeup_time_sum += result.response_time
        if config.wakeup_success_rate and result.result == "通过":
            wakeup_success_rate_sum += 1
        # 误唤醒
        if config.false_wakeup_times and result.result == "通过":
            false_wakeup_times_sum += 1
        if config.interaction_success_rate and result.asr_result != "":
            interaction_success_rate_sum += 1
        if config.word_recognition_rate:
            word_recognition_rate_sum += result.ocr_accuracy_rate
        if config.response_time:
            response_time_sum += result.response_time

    if config.wakeup_time:
        updata_data = {"wakeup_time": wakeup_time_sum/num}
        PlanOperateDao.updateProjectPlan(plan_id, updata_data)
    if config.wakeup_success_rate:
        updata_data = {"wakeup_success_rate": wakeup_success_rate_sum/num*100}
        PlanOperateDao.updateProjectPlan(plan_id, updata_data)
    if config.false_wakeup_times:
        updata_data = {"false_wakeup_times": false_wakeup_times_sum}
        PlanOperateDao.updateProjectPlan(plan_id, updata_data)
    if config.interaction_success_rate:
        updata_data = {"interaction_success_rate": interaction_success_rate_sum/num*100}
        PlanOperateDao.updateProjectPlan(plan_id, updata_data)
    if config.word_recognition_rate:
        updata_data = {"word_recognition_rate": word_recognition_rate_sum/num*100}
        PlanOperateDao.updateProjectPlan(plan_id, updata_data)
    if config.response_time:
        updata_data = {"response_time": response_time_sum/num}
        PlanOperateDao.updateProjectPlan(plan_id, updata_data)
    return

def judge_result():
    # user_text, car_text, image_url 从 Result 里面取
    llm_client = LLMJudge()
    current_project = ""
    turn_id = -1
    project = {}
    project_excel = False
    while True:
        if not LLMJudge_Queue.empty():
            Queue_lock.acquire()
            test_result = LLMJudge_Queue.get()  # 从队列中取出 Data 对象
            Queue_lock.release()
            # filter_data = {
            #     "plan_id": test_result.plan_id,
            #     "corpus_id": test_result.corpus_id
            # }
            corpus =  CorpusQueryDao.findTestCorpusById(test_result.corpus_id)
            update_data = {}
            if corpus == None: # 没找到测试语料则判断为唤醒场景
                if test_result.asr_result != "":
                    update_data = {"result": "通过", "score": 10}
                else:
                    update_data = {"result": "未通过", "score": 0}
                ResultOperateDao.updateTestResult(test_result.result_id,update_data)
                # continue
            else:
                show_project = ProjectQueryDao.findTestProjectById(test_result.project_id)
                show_plan = PlanQueryDao.findProjectPlanById(test_result.plan_id)
                log.info(f" 项目名={show_project.project_name} # 方案名={show_plan.plan_name} # 轮次={test_result.turn_id} # 语料文本={test_result.text} TEXT send to llm : user={test_result.text}, car={test_result.asr_result}")
                score, analysis_reason = llm_client.judge_by_text(test_result.text, test_result.asr_result)
                log.info(f" 项目名={show_project.project_name} # 方案名={show_plan.plan_name} # 轮次={test_result.turn_id} # 语料文本={test_result.text} TEXT llm result judge : score={score}, reason={analysis_reason}")
                score = int(score)
                # update_tree = {
                #     "score": score,
                # }
                # PlanOperateDao.updateTCorpusTree(update_tree, filter_data)
                if score >= 7:
                    update_data = {"result": "通过", "score": score}
                # elif score >=5 and score <= 7:
                else:
                    image1 = test_result.image
                    image2 = image1[:-10] + "1.jpg"
                    log.info(f" 项目名={show_project.project_name} # 方案名={show_plan.plan_name} # 轮次={test_result.turn_id} # 语料文本={test_result.text} IMAGE send to llm : user={test_result.text}, image_path1={image1}, image_path2={image2}")
                    score2, analysis_reason = llm_client.judge_image2(test_result.text, image1, image2)
                    log.info(f" 项目名={show_project.project_name} # 方案名={show_plan.plan_name} # 轮次={test_result.turn_id} # 语料文本={test_result.text} IMAGE llm result judge : score={score}, reason={analysis_reason}")
                    score2 = int(score2)
                    if score2 == 10:
                        update_data = {"result": "通过", "score": score}
                    else:
                        update_data = {"result": "未通过", "score": score}
                ResultOperateDao.updateTestResult(test_result.result_id,update_data)
                # else:
                #     update_data = {"result": "未通过", "score": score}
                #     ResultOperateDao.updateTestResult(test_result.result_id,update_data)

            LLMJudge_Queue.task_done()  # 标记任务已完成
            if current_project != test_result.project_id:
                current_project = test_result.project_id
                turn_id = test_result.turn_id
                project_excel = False
            time.sleep(1)
        elif LLMJudge_Queue.empty() and current_project != "":
            project = ProjectQueryDao.findTestProjectById(current_project)
            if project.project_status == "completed" and project_excel == False:
                # do_excel(current_project, turn_id)
                current_project = ""
                project_excel = True
            time.sleep(1)
        else:
            # print("队列为空，等待数据...")
            time.sleep(1)  # 等待队列中有数据「

    