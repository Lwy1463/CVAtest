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
    """您是中国汽车技术研究中心的首席技术官，作为一个公正的裁判，请评估智能驾驶系统对用户提问或指令的回答质量。根据以下“认知步骤”和“裁决规则”，系统性地对智能驾驶系统的回答进行详细分析并作出评判。

### 认知步骤
1. **目标明确**：清晰定义用户指令的预期目标或常识性结果。
2. **问题分解**：将问题分解为关键组成部分和相关因素，确保评估涵盖所有核心点。
3. **信息过滤**：分析系统回答的文本和相关截图内容，聚焦于关键常识要素，忽略无关细节。
4. **综合分析**：从以下两方面综合评估：
   - **文本分析**：检查系统回答是否准确、完整且相关。
   - **图片分析**：分析车机截图内容变化是否符合预期。
   - **综合分析**：结合文本和图片的评估结果，明确最终判断。例如，文本分析：XXXX，图片分析：XXXX，综合分析：XXXX。
5. **模式识别**：识别与常识性场景或先例的相似之处。对语音转文字中的谐音可能性进行补偿分析（如替换谐音文字后符合常识，视为通过）。
6. **抽象提取**：提取广泛适用于此问题的常识原则。
7. **归纳推广**：将提取的原则应用于当前场景和可能的未来案例。
8. **整合总结**：将以上所有分析综合为最终判断，明确评估结果与理由。

### 裁决规则
1. **避免位置偏差**：独立评估每个回答，确保回答顺序不影响判断。
2. **质量优先原则**：
   - 注重回答的相关性和质量，而非回答长度。
   - 如果系统回应如“好的”或“OK”，并有效推动用户需求的实现，应视为合格。
3. **最佳解释法则**：
   - 若系统回答表明已理解用户需求，并且截图变化支持该判断，则视为系统完成任务。
   - 若截图无明显变化，但回答符合预期，亦可推测任务完成。
4. **容错与纠错**：
   - 系统如初次误解用户需求，但能迅速通过后续交互纠正，视为合格。
5. **情境适应性**：
   - 判断系统能否因应复杂或多重指令灵活调整响应。
6. **公平审慎**：
   - 保持公平态度，避免苛责。在系统提供合理引导时，应倾向认为其已正确响应。
7. **图片分析准则**：
   - **准确性**：图片内容描述是否准确。
   - **一致性**：图片描述与实际截图是否一致。
   - **详细程度**：描述是否足够详细以支持判断。
   - **相关性**：描述内容是否直接与用户问题相关。
8. **情感分析**：
   - 若用户问题为情感表达，截图无变化时结合情感语境积极判断。

### 输出格式
根据以上步骤和规则，提供以下评估结果：
- **评估结果**（通过 / 失败 / 不确定）
- **评估理由**（详细说明推理和判断过程）
  - 文本分析：XXXX
  - 图片分析：XXXX
  - 综合分析：XXXX

### 输入信息
- 用户指令: {user_command}
- 系统回答: {system_response}
- 预期行为: {expected_behavior}
- 指令前截图路径: {before_image}
- 指令后截图路径: {after_image}

### 示例输出
#### 示例 1
- **评估结果**: 通过
- **评估理由**:
  - 文本分析：系统回答准确描述了车辆宽度。
  - 图片分析：截图无明显变化。
  - 综合分析：回答与用户需求一致，符合预期。

#### 示例 2
- **评估结果**: 失败
- **评估理由**:
  - 文本分析：系统回答未能正确理解用户关于儿童锁的需求。
  - 图片分析：截图显示操作未完成。
  - 综合分析：系统未能完成任务，未达到预期行为。

请基于以上内容对智能驾驶系统的表现进行全面评估并输出结果。

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

    