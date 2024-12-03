from app.utils.utils import generate_random_string
from app.dao.play_config_dao import PlayConfigQueryDao, PlayConfigOperateDao
from app.dao.plan_dao import PlanQueryDao, PlanOperateDao
from app.dao.project_dao import ProjectQueryDao, ProjectOperateDao
from app.dao.models.sqlite_gen import PlayConfig, StartConfig, RouseConfig, DisturbConfig, NoiseConfig, TestCorpusConfig, WaitConfig, RouseCorpusConfig
import os
import time

def play_config_create(name, desc, type):
    # random_str = generate_random_string()
    config = PlayConfig(
        config_name = name,
        description = desc,
        type = type
    )
    save_config = PlayConfigOperateDao.savePlayConfig(config)
    config = StartConfig(
        play_config_id = save_config.play_config_id,
        circle = 1,
        seat = 0
    )
    PlayConfigOperateDao.saveStartConfig(config)
    return 0

def play_config_update(id, name, desc, type, configs_list):
    find_config = {"play_config_id": id}
    in_use = PlanQueryDao.showAllProjectPlan(find_config)
    for ii in in_use:
        check_status = ProjectQueryDao.findTestProjectById(ii.project_id)
        if check_status is not None and check_status.project_status == "progressing":
            return {
                "status": "error",
                "error_msg": "the play_config is in use"
            }
    updated_data = {
        "config_name": name,
        "description": desc
    }
    updated_data = {key: value for key, value in updated_data.items() if value}
    update_config = PlayConfigOperateDao.updatePlayConfig(id, updated_data)
    # 删除老配置
    delete2 = PlayConfigOperateDao.deleteRouseConfig(id)
    delete3 = PlayConfigOperateDao.deleteDisturbConfig(id)
    delete4 = PlayConfigOperateDao.deleteNoiseConfig(id)
    if type == "rouse":
        delete5 = PlayConfigOperateDao.deleteRouseCorpusConfig(id)
    else:
        delete5 = PlayConfigOperateDao.deleteTestCorpusConfig(id)
    delete6 = PlayConfigOperateDao.deleteWaitConfig(id)
    num = 0
    for c in configs_list:
        config_type = c["type"]
        config_info = c["config"]
        if config_type == "开始":
            # config = {
            #     "circle": config_info["circle"]
            # }
            PlayConfigOperateDao.updateStartConfig(id, config_info)
        elif config_type == "嵌入唤醒":
            config = RouseConfig(
                play_config_id = id,
                wakeUpWaitDifferent = config_info["wakeUpWaitDifferent"],
                wakeUpWaitRepeated = config_info["wakeUpWaitRepeated"],
                frequencyDifferent = config_info["frequencyDifferent"],
                frequencyRepeated = config_info["frequencyRepeated"],
                frequencyIntervalDifferent = config_info["frequencyIntervalDifferent"],
                # channel = config_info["channel"],
                # gain = config_info["gain"],
                seat = num
            )
            PlayConfigOperateDao.saveRouseConfig(config)
        elif config_type == "播放背景噪声":
            config = DisturbConfig(
                play_config_id = id,
                channel = config_info["channel"],
                gain = config_info["gain"],
                seat = num
            )
            PlayConfigOperateDao.saveDisturbConfig(config)
        elif config_type == "播放干扰音":
            config = NoiseConfig(
                play_config_id = id,
                channel = config_info["channel"],
                gain = config_info["gain"],
                seat = num
            )
            PlayConfigOperateDao.saveNoiseConfig(config)
        elif config_type == "播放语料":
            config = TestCorpusConfig(
                play_config_id = id,
                repeat = config_info["repeat"],
                wait_time = config_info["wait_time"],
                timout = config_info["timout"],
                channel = config_info["channel"],
                gain = config_info["gain"],
                seat = num
            )
            PlayConfigOperateDao.saveTestCorpusConfig(config)
        elif config_type == "等待":
            config = WaitConfig(
                play_config_id = id,
                duration = config_info["duration"],
                seat = num
            )
            PlayConfigOperateDao.saveWaitConfig(config)
        elif config_type == "播放唤醒":
            config = RouseCorpusConfig(
                play_config_id = id,
                repeat = config_info["repeat"],
                channel = config_info["channel"],
                gain = config_info["gain"],
                seat = num
            )
            PlayConfigOperateDao.saveRouseCorpusConfig(config)
        else:
            return {"config type error"}
        num += 1
    return 0

def play_config_delete(id):
    find_config = {"play_config_id": id}
    in_use = PlanQueryDao.showAllProjectPlan(find_config)
    if len(in_use) != 0:
        return {
            "status": "error",
            "error_msg": "the play_config is in use"
        }
    delete_config = PlayConfigOperateDao.deletePlayConfig(id)
    delete1 = PlayConfigOperateDao.deleteStartConfig(id)
    delete2 = PlayConfigOperateDao.deleteRouseConfig(id)
    delete3 = PlayConfigOperateDao.deleteDisturbConfig(id)
    delete4 = PlayConfigOperateDao.deleteNoiseConfig(id)
    delete5 = PlayConfigOperateDao.deleteTestCorpusConfig(id)
    delete5 = PlayConfigOperateDao.deleteRouseCorpusConfig(id)
    delete6 = PlayConfigOperateDao.deleteWaitConfig(id)
    return 0

def get_playconfiglist_byid(id):
    data = {"play_config_id" : id}
    res_list = []
    temp_list = []
    a_list = PlayConfigQueryDao.showAllStartConfig(data)
    for i in a_list:
        temp_list.append(i)
    b_list = PlayConfigQueryDao.showAllRouseConfig(data)
    for i in b_list:
        temp_list.append(i)
    c_list = PlayConfigQueryDao.showAllDisturbConfig(data)
    for i in c_list:
        temp_list.append(i)
    d_list = PlayConfigQueryDao.showAllNoiseConfig(data)
    for i in d_list:
        temp_list.append(i)
    e_list = PlayConfigQueryDao.showAllTestCorpusConfig(data)
    for i in e_list:
        temp_list.append(i)
    f_list = PlayConfigQueryDao.showAllWaitConfig(data)
    for i in f_list:
        temp_list.append(i)
    g_list = PlayConfigQueryDao.showAllRouseCorpusConfig(data)
    for i in g_list:
        temp_list.append(i)

    for i in range(len(temp_list)):
        for con in temp_list:
            if i == con.seat:
                res_list.append(con)
                break
    return res_list

def get_config_info(config_body):
    if type(config_body) == StartConfig:
        con = {
            "circle": config_body.circle,
            "wakeup_time": config_body.wakeup_time,
            "wakeup_success_rate": config_body.wakeup_success_rate,
            "false_wakeup_times": config_body.false_wakeup_times,
            "interaction_success_rate": config_body.interaction_success_rate,
            "word_recognition_rate": config_body.word_recognition_rate,
            "response_time": config_body.response_time
        }
        return {"type": "开始", "config": con}
    elif type(config_body) == RouseConfig:
        con = {
            "wakeUpWaitDifferent": config_body.wakeUpWaitDifferent,
            "wakeUpWaitRepeated": config_body.wakeUpWaitRepeated,
            "frequencyDifferent": config_body.frequencyDifferent,
            "frequencyRepeated": config_body.frequencyRepeated,
            "frequencyIntervalDifferent": config_body.frequencyIntervalDifferent,
            "channel": config_body.channel,
            "gain": config_body.gain
        }
        return {"type": "嵌入唤醒", "config": con}
    elif type(config_body) == DisturbConfig:
        con = {
            "channel": config_body.channel,
            "gain": config_body.gain
        }
        return {"type": "播放背景噪声", "config": con}
    elif type(config_body) == NoiseConfig:
        con = {
            "channel": config_body.channel,
            "gain": config_body.gain
        }
        return {"type": "播放干扰音", "config": con}
    elif type(config_body) == TestCorpusConfig:
        con = {
            "repeat": config_body.repeat,
            "wait_time": config_body.wait_time,
            "timout": config_body.timout,
            "channel": config_body.channel,
            "gain": config_body.gain
        }
        return {"type": "播放语料", "config": con}
    elif type(config_body) == RouseCorpusConfig:
        con = {
            "repeat": config_body.repeat,
            "channel": config_body.channel,
            "gain": config_body.gain
        }
        return {"type": "播放唤醒", "config": con}
    elif type(config_body) == WaitConfig:
        con = {
            "duration": config_body.duration
        }
        return {"type": "等待", "config": con}

def play_config_list(data):
    config_list = PlayConfigQueryDao.showAllPlayConfig(data)
    res = []
    num = 0
    for config in config_list:
        temp = {}
        temp["play_config_id"] = config.play_config_id
        temp["config_name"] = config.config_name
        temp["description"] = config.description
        temp["type"] = config.type
        c_list = get_playconfiglist_byid(config.play_config_id)

        config_temp = []
        for i in c_list:
            info = get_config_info(i)
            config_temp.append(info)
        temp["configs"] = config_temp

        res.append(temp)
        num += 1
    return {"data": res, 'total': num}
