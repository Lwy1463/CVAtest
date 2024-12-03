from app.utils.utils import (generate_random_string, play_audio_with_pygame, get_mic_dir, create_audio_client,
                             save_data_to_excel, audio_to_text_xf, get_pic_dir, list_all_files, play_record,
                             play_audio_with_pygame_record, pcm_to_wav, get_excel_dir, get_audio_duration_ms)
from app.utils.thread_manager import thread_manager, ThreadManager
from app.dao.plan_dao import PlanQueryDao, PlanOperateDao
from app.dao.corpus_dao import CorpusQueryDao, CorpusOperateDao
from app.dao.result_dao import ResultQueryDao, ResultOperateDao
from app.dao.project_dao import ProjectQueryDao, ProjectOperateDao
from app.dao.play_config_dao import PlayConfigQueryDao, PlayConfigOperateDao
from app.dao.models.sqlite_gen import ProjectPlan, TCorpusTree, RCorpusTree, DCorpusTree, BNoiseTree, TestResult, MultiResult
from app.dao.review_dao import ReviewResultDao, ReviewResult
from app.service.iamge_svc import QUBEImageSvc
from app.config import LLMJudge_Queue, globalAppSettings, Queue_lock
from app.service.video_svc import video
from app.service.speech_recognition_svc import SpeechRecognitionSvc
from app.service.corpus import get_multi_testcorpus
import os
import time
import threading
import queue
from app.service.play_config import play_config_list
from app.middleware.log import logger as log

def create_test_plan(data):
    # random_str = generate_random_string()
    plan = ProjectPlan(
        project_id = data["project_id"],
        plan_name = data["plan_name"]
        )
    save_plan = PlanOperateDao.saveProjectPlan(plan)
    return {
        "status": "success",
        "error_msg": ""
    }

def update_test_plan(data):
    if "plan_id" not in data or data["plan_id"] == "plan-1":
        return {}
    updated_data = {
        "plan_name": data["plan_name"]
    }

    update_plan = PlanOperateDao.updateProjectPlan(data["plan_id"], updated_data)
    return {
        "status": "success",
        "error_msg": ""
    }

def delete_test_plan(data):
    if "plan_id" not in data or data["plan_id"] == "plan-1":
        return {}
    plan = PlanQueryDao.findProjectPlanById(data["plan_id"])
    PlanOperateDao.deleteTCorpusTree(data["plan_id"])
    PlanOperateDao.deleteRCorpusTree(data["plan_id"])
    PlanOperateDao.deleteDCorpusTree(data["plan_id"])
    PlanOperateDao.deleteBNoiseTree(data["plan_id"])
    check_status = ProjectQueryDao.findTestProjectById(plan.project_id)
    if check_status.project_status == "progressing":
        return {
            "status": "error",
            "error_msg": "This project is in use"
        }
    delete_plan = PlanOperateDao.deleteProjectPlan(data["plan_id"])
    return {
        "status": "success",
        "error_msg": ""
    }

def test_plan_list(data):
    plan_list = PlanQueryDao.showAllProjectPlan(data)
    res = []
    num = 0
    for plan in plan_list:
        temp = {}
        temp["plan_id"] = plan.plan_id
        temp["plan_name"] = plan.plan_name
        temp["play_config_id"] = plan.play_config_id
        temp["type"] = plan.type

        res.append(temp)
        num += 1
    return {"data": res, 'total': num}

def get_corpuslist_byplanid(plan_id):
    if plan_id == "plan-1":
        return {}
    plan = PlanQueryDao.findProjectPlanById(plan_id)
    if plan is None:
        return {}
    temp = {}
    temp["plan_id"] = plan.plan_id
    temp["play_config_id"] = plan.play_config_id
    a_list = PlanQueryDao.findAllTCorpusByTreeId(plan.plan_id)
    a_ret = []
    for a in a_list:
        a_ret.append(a)
    temp["testCorpusList"] = a_ret

    b_list = PlanQueryDao.findAllRCorpusByTreeId(plan.plan_id)
    b_ret = []
    for b in b_list:
        b_ret.append(b.corpus_id)
    temp["rouseCorpusList"] = b_ret

    c_list = PlanQueryDao.findAllDCorpusByTreeId(plan.plan_id)
    c_ret = []
    for c in c_list:
        c_ret.append(c.corpus_id)
    temp["disturbCorpusList"] = c_ret

    d_list = PlanQueryDao.findAllNoiseByTreeId(plan.plan_id)
    d_ret = []
    for d in d_list:
        d_ret.append(d.corpus_id)
    temp["backgroundNoiseList"] = d_ret

    return temp

def save_corpuslist_byplanid(data):
    if "plan_id" not in data or data["plan_id"] == "plan-1":
        return {}
    if "testCorpusList" in data and len(data["testCorpusList"]) != 0:
        corpus_list = []
        PlanOperateDao.deleteTCorpusTree(data["plan_id"])
        for corpus_id in data["testCorpusList"]:
            corpus = TCorpusTree(plan_id = data["plan_id"], corpus_id = corpus_id)
            corpus_list.append(corpus)
        PlanOperateDao.saveTCorpusTreeList(corpus_list)
    if "rouseCorpusList" in data and len(data["rouseCorpusList"]) != 0:
        corpus_list = []
        PlanOperateDao.deleteRCorpusTree(data["plan_id"])
        for corpus_id in data["rouseCorpusList"]:
            corpus = RCorpusTree(plan_id = data["plan_id"], corpus_id = corpus_id)
            corpus_list.append(corpus)
        PlanOperateDao.saveRCorpusTreeList(corpus_list)
    if "disturbCorpusList" in data and len(data["disturbCorpusList"]) != 0:
        corpus_list = []
        PlanOperateDao.deleteDCorpusTree(data["plan_id"])
        for corpus_id in data["disturbCorpusList"]:
            corpus = DCorpusTree(plan_id = data["plan_id"], corpus_id = corpus_id)
            corpus_list.append(corpus)
        PlanOperateDao.saveDCorpusTreeList(corpus_list)
    if "backgroundNoiseList" in data and len(data["backgroundNoiseList"]) != 0:
        corpus_list = []
        PlanOperateDao.deleteBNoiseTree(data["plan_id"])
        for corpus_id in data["backgroundNoiseList"]:
            corpus = BNoiseTree(plan_id = data["plan_id"], corpus_id = corpus_id)
            corpus_list.append(corpus)
        PlanOperateDao.saveBNoiseTreeList(corpus_list)
    play_config = PlayConfigQueryDao.findPlayConfigById(data["play_config_id"])
    updated_data = {
        "play_config_id": data["play_config_id"],
        "type": play_config.type
    }
    update_plan = PlanOperateDao.updateProjectPlan(data["plan_id"], updated_data)
    return {
        "status": "success",
        "error_msg": ""
    }

def play_rousecorpus(corpus_id, wait, channel = "channel1", gain = 0):
    r_corpus  = CorpusQueryDao.findRouseCorpusById(corpus_id)
    aud = CorpusQueryDao.findAudioById(r_corpus.aud_id)
    play_audio_with_pygame(aud.aud_url)
    time.sleep(wait / 1000.0)

def play_disturbcorpus(corpus_id, channel = "channel1", gain = 0):
    d_corpus  = CorpusQueryDao.findDisturbCorpusById(corpus_id)
    aud = CorpusQueryDao.findAudioById(d_corpus.aud_id)
    play_audio_with_pygame(aud.aud_url)

def play_backgroundnoise(corpus_id, channel = "channel1", gain = 0):
    b_corpus  = CorpusQueryDao.findBackgroundNoiseById(corpus_id)
    aud = CorpusQueryDao.findAudioById(b_corpus.aud_id)
    play_audio_with_pygame(aud.aud_url)

def play_testcorpus(play_config_type, data_index_config, project_id, plan_id, corpus_id, repeat, wait_time, timout, turn, relative_interval, thread_manager: "ThreadManager",
                    channel = "channel1", gain = 0, is_multi = False):
    show_project = ProjectQueryDao.findTestProjectById(project_id)
    show_plan = PlanQueryDao.findProjectPlanById(plan_id)
    
    t_corpus = {}
    expect_result = ""
    if "rouse" in play_config_type:
        t_corpus  = CorpusQueryDao.findRouseCorpusById(corpus_id)
    else:
        t_corpus  = CorpusQueryDao.findTestCorpusById(corpus_id)
        expect_result = t_corpus.expect_result
    aud = CorpusQueryDao.findAudioById(t_corpus.aud_id)
    exclude_time = get_audio_duration_ms(aud.aud_url)

    pic_storage_path = get_pic_dir()
    pic_path = os.path.join(pic_storage_path, project_id)
    pic_path = os.path.join(pic_path,  str(turn))
    pic_path = os.path.join(pic_path, plan_id)
    pic_path = os.path.join(pic_path, corpus_id)
    if not os.path.exists(pic_path):  
        os.makedirs(pic_path)

    micaudio_name = f"{corpus_id}_mic_{repeat}.pcm"
    mic_storage_path = get_mic_dir()
    micaudio_path = os.path.join(mic_storage_path, project_id)
    micaudio_path = os.path.join(micaudio_path,  str(turn))
    micaudio_path = os.path.join(micaudio_path, plan_id)
    micaudio_path = os.path.join(micaudio_path, corpus_id)
    if not os.path.exists(micaudio_path):  
        os.makedirs(micaudio_path)
    micaudio_path = os.path.join(micaudio_path, micaudio_name)

    # 录音线程
    sub_thread1 = f"{project_id}_sub_1"
    q = queue.Queue()
    recoder_thread = thread_manager.start_sub_thread(project_id, sub_thread1, play_record, q, micaudio_path, exclude_time, wait_time, timout)

    # 播放线程
    sub_thread2 = f"{project_id}_sub_2"

    log.info(f" 项目名={show_project.project_name} # 方案名={show_plan.plan_name} # 轮次={turn} # 语料文本={t_corpus.text}  play audio : path=({aud.aud_url})")
    audio_thread = thread_manager.start_sub_thread(project_id, sub_thread2, play_audio_with_pygame, aud.aud_url)

    # ocr线程
    sub_thread3 = f"{project_id}_sub_3"
    random_str = generate_random_string()
    file_name = str(repeat) + "_" + t_corpus.corpus_id
    svc_client = QUBEImageSvc()
    svc_client.photograph(pic_path, f"{random_str}_1")
    photograph_thread = thread_manager.start_sub_thread(project_id, sub_thread3, svc_client.photograph_process, pic_path, file_name, t_corpus.audio_duration, random_str)
    # relative_interval = int(time.time() - start_time)

    # 等待三个任务完成
    recoder_thread.join()
    audio_thread.join()
    photograph_thread.join()

    Queue_lock.acquire()
    r_time = q.get()
    Queue_lock.release()
    log.info(f" 项目名={show_project.project_name} # 方案名={show_plan.plan_name} # 轮次={turn} # 语料文本={t_corpus.text} car respond: recorded_audio_path={micaudio_path}, time={r_time}ms")
    result_path, result_text, max_similarity = "", "", 1
    if data_index_config["word_recognition_rate"] == True:
        path_list = list_all_files(pic_path, file_name)
        result_path, result_text, max_similarity = svc_client.image_select_by_multi_recognition(path_list, t_corpus.text)
        log.info(f" 项目名={show_project.project_name} # 方案名={show_plan.plan_name} # 轮次={turn} # 语料文本={t_corpus.text} ocr result : save_path=({result_path}), ocr_text=({result_text}), max_similarity={max_similarity}")
    image_path = os.path.join(pic_path, random_str + "_result.jpg")
    # micaudio_path = record_audio(audio, micaudio_name)
    # 语音转文字
    asr_svc = SpeechRecognitionSvc()
    full_record = micaudio_path[:-4] + "_full.pcm"
    wav_file_full = pcm_to_wav(full_record)
    wav_file = pcm_to_wav(micaudio_path)
    if r_time == -1:
        mic_audio_text = ""
    else:
        r_time = r_time / 1000
        if "rouse" in play_config_type:
            mic_audio_text = asr_svc.local_recognize_rouse(wav_file)
        else:
            mic_audio_text = asr_svc.local_recognize(wav_file)
    # micaudio_text = audio_to_text_xf(micaudio_path)
    
    result = TestResult(
        result_id = random_str,
        project_id = project_id,
        plan_id = plan_id,
        corpus_id = corpus_id,
        turn_id = turn,
        relative_interval = int(relative_interval),
        test_scenario = t_corpus.test_scenario,
        text = t_corpus.text,
        asr_result = mic_audio_text,
        image = image_path,
        mic_audio_url = wav_file_full,
        ocr_pic_url = result_path,
        ocr_result = result_text,
        ocr_accuracy_rate = max_similarity,
        response_time = r_time,
        expect_result = expect_result
    )
    save_result = ResultOperateDao.saveTestResult(result)
    if is_multi:
        return save_result
    Queue_lock.acquire()
    LLMJudge_Queue.put(save_result)
    Queue_lock.release()
    return None

def play_wait(wait):
    time.sleep(wait / 1000.0)

def test_execute(thread_manager: "ThreadManager", data: dict):
    project_id = data["project_id"]
    turn = ResultQueryDao.getMaxTurn(project_id)
    if turn is None:
        turn_id = 1
    else:
        turn_id = ResultQueryDao.getMaxTurn(project_id) + 1
    video_path = os.path.join(globalAppSettings.video_dir, f"{project_id}_{turn_id}.mp4")
    try:
        update_status = {"project_status": "progressing"}
        ProjectOperateDao.updateTestProject(project_id, update_status)
        # plan_list = test_plan_list(data)
        plan_list = PlanQueryDao.showAllProjectPlan(data)
        # audio = create_audio_client()
        corpus_num = 0
        corpuslist = {}
        video.start(video_path)
        start_time = time.time()
        play_config_type = ""
        for plan_temp in plan_list:
            corpuslist = get_corpuslist_byplanid(plan_temp.plan_id)
            if plan_temp.play_config_id is None:
                continue
            play_data = {"play_config_id": plan_temp.play_config_id}
            config_data = play_config_list(play_data)
            configs = config_data["data"][0]["configs"]
            play_config_type = config_data["data"][0]["type"]
            # 循环次数
            circle = 0
            if configs[0]["type"] == "开始":
                config = configs[0]["config"]
                circle = int(config["circle"])
            if "rouse" in play_config_type:
                corpus_num += len(corpuslist["rouseCorpusList"]) * circle
            else:
                corpus_num += len(corpuslist["testCorpusList"]) * circle

        total_num = 0
        for plan_temp in plan_list:
            update_status = {"plan_status": "progressing"}
            PlanOperateDao.updateProjectPlan(plan_temp.plan_id, update_status)
            corpuslist = get_corpuslist_byplanid(plan_temp.plan_id)
            # 开始根据播放配置进行 语料播放
            # 获取播放配置
            if plan_temp.play_config_id is None:
                continue
            play_data = {"play_config_id": plan_temp.play_config_id}
            config_data = play_config_list(play_data)
            configs = config_data["data"][0]["configs"]
            play_config_type = config_data["data"][0]["type"]
            # 循环次数
            circle = 0
            data_index_config = {}
            if configs[0]["type"] == "开始":
                config = configs[0]["config"]
                data_index_config = config
                circle = int(config["circle"])
            else:
                return "Incorrect playback configuration"
            # 测试语料
            testlist = []
            if "rouse" in play_config_type:
                testlist = corpuslist["rouseCorpusList"]
            else:
                testlist = corpuslist["testCorpusList"]
            # 唤醒语料
            rouse_len = len(corpuslist["rouseCorpusList"])
            if rouse_len != 0:
                rouse = corpuslist["rouseCorpusList"][0]
            else:
                return "Not correct Rouse Corpus"
            # 干扰语料，这个位置我发现前端是多选，这儿默认是单选
            if corpuslist.get("disturbCorpusList"):
                disturb = corpuslist["disturbCorpusList"][0]
            # 背景噪声
            if corpuslist.get("backgroundNoiseList"):
                background = corpuslist["backgroundNoiseList"][0]
            
            for i in range(circle):
                test_num = 0
                for test in testlist:
                    test_num += 1
                    wake_repeat = 0
                    freq_repeat = ""
                    freq = ""
                    for config in configs:
                        config_info = config["config"]
                        config_type = config["type"]
                        if config_type == "开始":
                            continue
                        elif config_type == "嵌入唤醒":
                            freq = config_info["frequencyDifferent"] # 不同语料间唤醒频率 first 仅一次 every 每次 interval 间隔 frequency_interval 次
                            freq_repeat = config_info["frequencyRepeated"] # 语料重复时唤醒频率 none 不嵌入 every 每次
                            freq_interval = config_info["frequencyIntervalDifferent"] # 不同语料间间隔次数，当上面为 interval间隔 的时候起作用
                            freq_interval += 1
                            wait = config_info["wakeUpWaitDifferent"]
                            wake_repeat = config_info["wakeUpWaitRepeated"]
                            if freq == 'first' and test_num == 1:
                                play_rousecorpus(rouse, wait, channel = "channel1", gain = 0)
                                # print("play_rousecorpus ", rouse)
                            elif freq == 'every':
                                play_rousecorpus(rouse, wait, channel = "channel1", gain = 0)
                                # print("play_rousecorpus ", rouse)
                            elif freq == 'interval' and freq_interval and (test_num - 1) % freq_interval == 0:
                                play_rousecorpus(rouse, wait, channel = "channel1", gain = 0)
                                # print("play_rousecorpus ", rouse)
                            elif freq == 'every' and freq_repeat == "every":
                                play_rousecorpus(rouse, wake_repeat, channel = "channel1", gain = 0)
                                # print("play_rousecorpus ", rouse)
                        elif config_type == "播放背景噪声":
                            # print("play_backgroundnoise ", background)
                            play_backgroundnoise(background, channel = "channel1", gain = 0)
                        elif config_type == "播放干扰音":
                            play_disturbcorpus(disturb, channel = "channel1", gain = 0)
                            # print("play_disturbcorpus ", disturb)
                        elif config_type == "播放语料" or config_type == "播放唤醒":
                            repeat_num = config_info["repeat"]
                            wait_time = 2
                            timout = 10
                            if "rouse" not in play_config_type:
                                wait_time = config_info["wait_time"]
                                timout = config_info["timout"]
                            # 传一个类型来判断是 唤醒场景还是交互场景
                            for i in range(repeat_num):
                                check_status = ProjectQueryDao.findTestProjectById(data["project_id"])
                                if check_status.project_status == "stopped":
                                    return "stop test"
                                relative_interval = time.time() - start_time
                                if "rouse" not in play_config_type:
                                    # 交互场景
                                    t_corpus  = CorpusQueryDao.findTestCorpusById(test)
                                    if t_corpus == None:
                                        # 多伦
                                        multi_corpus = get_multi_testcorpus(test)
                                        mul_result = []
                                        multi_result = MultiResult(
                                            project_id = project_id,
                                            plan_id = plan_temp.plan_id,
                                            multicorpus_id = test,
                                            turn_id = turn_id
                                        )
                                        save_multi_result = ResultOperateDao.saveMultiResult(multi_result)
                                        for m_corpus_id in multi_corpus:
                                            multi_res = play_testcorpus(play_config_type, data_index_config, project_id, plan_temp.plan_id, m_corpus_id, i, wait_time, timout,
                                                    turn_id, relative_interval, thread_manager, channel = "channel1", gain = 0, is_multi = True)
                                            mul_result.append(multi_res)
                                        mul_result.append(save_multi_result)
                                        Queue_lock.acquire()
                                        LLMJudge_Queue.put(mul_result)
                                        Queue_lock.release()
                                    else:
                                        # 一次交互的测试语料
                                        play_testcorpus(play_config_type, data_index_config, project_id, plan_temp.plan_id, test, i, wait_time, timout,
                                                turn_id, relative_interval, thread_manager, channel = "channel1", gain = 0)
                                else:
                                    # 唤醒场景
                                    play_testcorpus(play_config_type, data_index_config, project_id, plan_temp.plan_id, test, i, wait_time, timout,
                                                turn_id, relative_interval, thread_manager, channel = "channel1", gain = 0)
                                if repeat_num - i > 1 and freq_repeat == "every" and freq == "every":
                                    play_rousecorpus(rouse, wake_repeat, channel = "channel1", gain = 0)
                            # print("play_testcorpus ", test)
                        elif config_type == "等待":
                            wait = config_info["duration"]
                            play_wait(wait)
                            # print("play_wait")
                        check_status = ProjectQueryDao.findTestProjectById(data["project_id"])
                        if check_status.project_status == "stopped":
                            return "stop test"
                    total_num += 1
                    process = int((total_num / corpus_num) * 100)
                    update_process = {"project_process": str(process)}
                    ProjectOperateDao.updateTestProject(data["project_id"], update_process)
            # 修改方案状态
            update_status = {"plan_status": "completed"}
            PlanOperateDao.updateProjectPlan(plan_temp.plan_id, update_status)
        # close_audio_client(audio)
        update_status = {"project_status": "completed"}
        ProjectOperateDao.updateTestProject(data["project_id"], update_status)
    finally:
        # 执行完毕后清理线程字典中的该线程
        project_id = data["project_id"]
        if project_id in thread_manager.threads:
            thread_manager.stop_thread(project_id)
        # 关闭视频录制
        video.close()
        review_data = ReviewResult(
            project_id = project_id,
            turn_id = turn_id,
            video_path = video_path,
        )
        ReviewResultDao.save(review_data)

def get_multi_result(multi_result):
    multi_corpu = CorpusQueryDao.findMultiCorpusById(multi_result.multicorpus_id)
    multi = {}
    multi["project_id"] = multi_result.project_id
    multi["plan_id"] = multi_result.plan_id
    multi["multicorpus_id"] = multi_result.multicorpus_id
    multi["turn_id"] = multi_result.turn_id
    multi["result"] = multi_result.result
    multi["reason"] = multi_result.reason
    multi["success_rate"] = multi_result.success_rate
    multi["time"] = multi_result.time
    res_temp = []
    temp_log = ""
    for corpus in multi_corpu:
        data = {
            "project_id": multi_result.project_id, 
            "turn_id": multi_result.turn_id, 
            "plan_id": multi_result.plan_id,
            "corpus_id": corpus.testcorpus_id
        }
        result_list = ResultQueryDao.showAllTestResult(data)
        for result in result_list:
            temp = {}
            temp["result_id"] = result.result_id
            temp["time"] = result.time
            # temp["project_id"] = result.project_id
            # temp["plan_id"] = result.plan_id
            temp["corpus_id"] = result.corpus_id
            # temp["turn_id"] = result.turn_id
            temp["test_scenario"] = result.test_scenario
            temp["text"] = result.text
            temp["result"] = result.result
            temp["image"] = result.image
            temp["score"] = result.score
            temp["asr_result"] = result.asr_result
            temp["mic_audio_url"] = result.mic_audio_url
            temp["ocr_pic_url"] = result.ocr_pic_url
            temp["ocr_result"] = result.ocr_result
            temp["ocr_accuracy_rate"] = result.ocr_accuracy_rate
            temp["relative_interval"] = result.relative_interval
            temp["response_time"] = result.response_time
            temp["expect_result"] = result.expect_result
            temp["relative_interval"] = result.relative_interval
            temp_log = temp_log + result.time.strftime("%Y-%m-%d %H:%M:%S") + "  " + result.text + "  " + result.asr_result + "\n"
            res_temp.append(temp)
    multi["sub_result"] = res_temp

    return multi, temp_log

def get_recent_testinfo(project_id, turn_id, plan_id):
    res = {}
    project = ProjectQueryDao.findTestProjectById(project_id)
    if project is None:
        return {
            "status": "error",
            "error_msg": "Can't find available project_id"
        }
    plan = PlanQueryDao.findProjectPlanById(plan_id)
    if plan is None:
        return {}
    res["process"] = project.project_process
    res["status"] = project.project_status
    temp_log = ""
    res["video_url"] = ""
    res["audio_url"] = ""
    res["wakeup_time"] = plan.wakeup_time
    res["wakeup_success_rate"] = plan.wakeup_success_rate
    res["false_wakeup_times"] = plan.false_wakeup_times
    res["interaction_success_rate"] = plan.interaction_success_rate
    res["word_recognition_rate"] = plan.word_recognition_rate
    res["response_time"] = plan.response_time
    data = {"project_id": project_id, "turn_id": turn_id, "plan_id": plan_id}
    result_list = ResultQueryDao.showAllTestResult(data)

    # 判断是不是多伦
    multi_result = ResultQueryDao.showAllMultiResult(data)
    if len(multi_result) > 0 :
        multi = []
        for result in multi_result:
            multi_temp, temp_log = get_multi_result(result)
            multi.append(multi_temp)
        res["result_list"] = multi
        res["log"] = temp_log
        return res

    num = 0
    res_temp = []
    for result in result_list:
        temp = {}
        temp["result_id"] = result.result_id
        temp["time"] = result.time
        temp["project_id"] = result.project_id
        temp["plan_id"] = result.plan_id
        temp["corpus_id"] = result.corpus_id
        temp["turn_id"] = result.turn_id
        temp["test_scenario"] = result.test_scenario
        temp["text"] = result.text
        temp["result"] = result.result
        temp["image"] = result.image
        temp["score"] = result.score
        temp["asr_result"] = result.asr_result
        temp["mic_audio_url"] = result.mic_audio_url
        temp["ocr_pic_url"] = result.ocr_pic_url
        temp["ocr_result"] = result.ocr_result
        temp["ocr_accuracy_rate"] = result.ocr_accuracy_rate
        temp["relative_interval"] = result.relative_interval
        temp["response_time"] = result.response_time
        temp["expect_result"] = result.expect_result

        temp["relative_interval"] = result.relative_interval
        temp_log = temp_log + result.time.strftime("%Y-%m-%d %H:%M:%S") + "  " + result.text + "  " + result.asr_result + "\n"
        res_temp.append(temp)
    res["result_list"] = res_temp
    res["log"] = temp_log
    return res

def test_suspend(data):
    update_status = {"project_status": "stopped", "project_process": str(100)}
    ProjectOperateDao.updateTestProject(data["project_id"], update_status)

def update_test_result(data):
    for i in data["result_ids"]:
        update_result = {"result": data["result"]}
        ResultOperateDao.updateTestResult(i, update_result)
    return {
        "status": "success",
        "error_msg": ""
    }

def get_turn_list(data):
    if "project_id" not in data:
        return []
    project_id = data["project_id"]
    turns = ResultQueryDao.getTurnListBySet(project_id)
    turn_list = [name[0] for name in turns]
    return list(set(turn_list))

def get_review_video_name(project_id, turn_id):
    result = ReviewResultDao.getByPorjectAndTurn(project_id, turn_id)
    name = os.path.basename(result.video_path)
    return name

def do_excel(project_name, configtype, project_id, turn_id, plan_list):
    res_temp = []
    for plan in plan_list:
        data = {"project_id": project_id, "turn_id": turn_id, "plan_id": plan.plan_id}
        result_list = ResultQueryDao.showAllTestResult(data)
    
        for result in result_list:
            temp = {}
            temp["项目名称"] = project_name
            temp["本次结果id"] = result.result_id
            temp["测试时间"] = result.time
            temp["语料id"] = result.corpus_id
            temp["第几轮测试"] = result.turn_id
            temp["测试场景"] = result.test_scenario
            temp["语料文本"] = result.text
            temp["预期结果"] = result.expect_result
            if configtype == "rouse":
                temp["判断结果"] = result.result
            else:
                temp["结果判断"] = result.result
                temp["判断分数"] = result.score
            temp["车机响应识别"] = result.asr_result
            if plan.response_time is not None:
                temp["车机响应时间"] = result.response_time
            if plan.wakeup_time is not None:
                temp["车机唤醒时间"] = result.response_time
            if configtype != "rouse":
                temp["车机识别结果"] = result.ocr_result
            if plan.word_recognition_rate is not None:
                temp["车机识别准确率"] = result.ocr_accuracy_rate

            res_temp.append(temp)
    file_path = get_excel_dir()
    save_data_to_excel(file_path, project_name, turn_id, configtype, res_temp)
    return

def do_false_rouse_excel():
    return

def get_excel_report(project_id, turn_id, configtype):
    project = ProjectQueryDao.findTestProjectById(project_id)
    if project is None:
        return ""
    plan_list = PlanQueryDao.showAllProjectPlan({"project_id": project_id})
    plan_filter_list = []
    for plan in plan_list:
        play_config = PlayConfigQueryDao.findPlayConfigById(plan.play_config_id)
        if play_config is not None and play_config.type == configtype:
            plan_filter_list.append(plan)
    if configtype != "false-rouse":
        do_excel(project.project_name, configtype, project_id, turn_id, plan_filter_list)
    else:
        do_false_rouse_excel()

    file_path = get_excel_dir()
    full_file_path = ""
    full_file_path = os.path.join(file_path, f"{project.project_name}_{turn_id}.xlsx")
    return full_file_path

# def dlh_test():
    
#     play_audio_with_pygame("/Users/dlh/Desktop/zhaoshang/code/rtasr_python3_demo/python/tts_audio/DXgU0O_tts_1.mp3")

    # audio = create_audio_client()
    # micaudio_name = f"dlh_test.pcm"
    # micaudio_path = record_audio(audio, micaudio_name)
    # micaudio_text = audio_to_text_xf(micaudio_path)
    # print(micaudio_text)
    # result = TestResult(
    #     result_id = "dlhtest_result",
    #     project_id = "dlhtest_project",
    #     plan_id = "dlhtest_plan",
    #     corpus_id = "dlhtest_corpus",
    #     test_scenario = "aaa",
    #     text = "请打开车窗",
    #     asr_result = "车窗已打开",
    #     mic_audio_url = "micaudio_path",
    #     ocr_pic_url = "ocr_pic_url",
    #     ocr_result = "ocr_result",
    #     ocr_accuracy_rate = "ocr_pic_url",
    #     response_time = " "
    # )
    # save_result = ResultOperateDao.saveTestResult(result)
    # LLMJudge_Queue.put(save_result)
    # close_audio_client(audio)

