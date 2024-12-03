
from app.utils.utils import chinese_to_pinyin, get_file_dir, get_audio_duration, generate_random_string, \
    move_file_to_folder, analysis_excel, get_excel_dir, corpus_excel, copy_file_to_modifyfolder
from app.dao.corpus_dao import CorpusOperateDao, CorpusQueryDao
from app.dao.project_dao import ProjectQueryDao, ProjectOperateDao
from app.dao.plan_dao import PlanQueryDao
from app.service.synthesize_svc import SynthesizeSvc
from app.constant import Vocalists
from app.dao.models.sqlite_gen import TestCorpus, CorpusAudio, RouseCorpus, DisturbCorpus, BackgroundNoise, MultiCorpus
import os
import time

def save_audio_file(file, file_data, data):
    # print(data)
    file_name, file_extension = os.path.splitext(file.filename)
    file_name_pinyin = chinese_to_pinyin(data.get('text', ''))
    file_dir = get_file_dir()
    filepath = os.path.join(file_dir, file.filename)
    with open(filepath, 'wb') as file:
        file.write(file_data)
    duration = get_audio_duration(filepath)
    if duration["status"] == "error":
        if os.path.exists(filepath):
            os.remove(filepath)
        return {
            "status": "error",
            "error_msg": duration["data"]
        }
    else:
        # random_str = generate_random_string()
        audio = CorpusAudio(
            aud_url = filepath,
            pinyin = file_name_pinyin,
            audio_duration = duration["data"]
            )
        save_audio = CorpusOperateDao.saveAudio(audio)
        return {
            "status": "success",
            "aud_id": save_audio.aud_id,
            "pinyin": file_name_pinyin,
            "audio_duration": duration["data"]
        }

def excel_create_corpus(file, file_data, data):
    # print(data)
    file_name, file_extension = os.path.splitext(file.filename)
    excel_dir = get_excel_dir()
    storage_import_excel = os.path.join(excel_dir, 'import')
    if not os.path.exists(storage_import_excel):  
        os.makedirs(storage_import_excel)
    filepath = os.path.join(storage_import_excel, file.filename)
    with open(filepath, 'wb') as file:
        file.write(file_data)
    excel_type, corpuslist = corpus_excel(filepath)
    # print(corpuslist)
    if excel_type == "rouse":
        for cor in corpuslist:
            file_name_pinyin = chinese_to_pinyin(cor["A"])
            # aud_id_random = generate_random_string()
            # cor_random_str = generate_random_string()
            rousecorpus = create_rousecorpus(cor["A"], cor["B"], cor["C"], cor["D"], cor["E"])
            if cor["F"] is not None:
                new_path = copy_file_to_modifyfolder(cor["F"], "rouse_corpus")
                duration = get_audio_duration(new_path)
                name = os.path.basename(new_path)
                if duration["status"] == "error":
                    continue
                file_name_pinyin = chinese_to_pinyin(cor["A"])
                audio = CorpusAudio(
                    corpus_id = rousecorpus.corpus_id,
                    aud_url = new_path,
                    pinyin = file_name_pinyin,
                    audio_duration = duration["data"]
                    )
                save_audio = CorpusOperateDao.saveAudio(audio)
                corpus_data = {
                    "aud_id": save_audio.aud_id,
                    "audio_url": name,
                    "audio_path": new_path,
                    "audio_duration": duration["data"]
                }
                update_corpus = CorpusOperateDao.updateRouseCorpus(rousecorpus.corpus_id, corpus_data)
    else:
        for cor in corpuslist:
            # aud_id_random = generate_random_string()
            # cor_random_str = generate_random_string()
            testcorpus = create_testcorpus(cor["A"], cor["B"], cor["C"], cor["D"], cor["E"], cor["F"], cor["G"], cor["H"])
            if cor["I"] is not None:
                new_path = copy_file_to_modifyfolder(cor["I"], "test_corpus")
                duration = get_audio_duration(new_path)
                name = os.path.basename(new_path)
                if duration["status"] == "error":
                    continue
                file_name_pinyin = chinese_to_pinyin(cor["A"])
                audio = CorpusAudio(
                    corpus_id = testcorpus.corpus_id,
                    aud_url = new_path,
                    pinyin = file_name_pinyin,
                    audio_duration = duration["data"]
                    )
                save_audio = CorpusOperateDao.saveAudio(audio)
                corpus_data = {
                    "aud_id": save_audio.aud_id,
                    "audio_url": name,
                    "audio_path": new_path,
                    "audio_duration": duration["data"]
                }
                update_corpus = CorpusOperateDao.updateTestCorpus(testcorpus.corpus_id, corpus_data)

    return {
        "status": "success",
        "error_msg": ""
    }

def excel_create_syncorpus(file, file_data, data):
    # print(data)
    file_name, file_extension = os.path.splitext(file.filename)
    excel_dir = get_excel_dir()
    storage_import_excel = os.path.join(excel_dir, 'import')
    if not os.path.exists(storage_import_excel):  
        os.makedirs(storage_import_excel)
    filepath = os.path.join(storage_import_excel, file.filename)
    with open(filepath, 'wb') as file:
        file.write(file_data)
    corpuslist = analysis_excel(filepath)
    for corp in corpuslist:
        svc = SynthesizeSvc()
        name = generate_random_string()
        ret, url = svc.synthesize(corp["A"], name, corp["B"], corp["C"], corp["D"], corp["G"])
        file_name_pinyin = chinese_to_pinyin(corp["A"])
        # random_audio_id = generate_random_string()
        # random_corpus_id = generate_random_string()
        duration = get_audio_duration(url)
        if duration["status"] == "error":
            if os.path.exists(url):
                os.remove(url)
            continue
        audio = CorpusAudio(
            aud_url=url,
            pinyin=file_name_pinyin,
            audio_duration=duration["data"]
        )
        save_audio = CorpusOperateDao.saveAudio(audio)
        name = os.path.basename(url)
        if corp["B"] == Vocalists.female:
            voice = "female"
        elif corp["B"] == Vocalists.male:
            voice = "male"
        else:
            voice = ""
        # language = "mandarin"
        if corp["D"] == 2:
            corpus = RouseCorpus(
                aud_id=save_audio.aud_id,
                text=corp["A"],
                pinyin=file_name_pinyin,
                audio_url=name,
                audio_duration=duration["data"],
                speaker=voice,
                language=corp["C"],
                test_scenario="wake-up",
                label=corp["E"],
                audio_path=url,
                is_tts = True
            )
        elif corp["D"] == 3:
            corpus = DisturbCorpus(
                aud_id=save_audio.aud_id,
                text=corp["A"],
                pinyin=file_name_pinyin,
                audio_url=name,
                audio_duration=duration["data"],
                speaker=voice,
                language=corp["C"],
                label=corp["E"],
                audio_path=url,
                is_tts = True
            )
        else:
            corpus = TestCorpus(
                aud_id=save_audio.aud_id,
                text=corp["A"],
                pinyin=file_name_pinyin,
                audio_url=name,
                audio_duration=duration["data"],
                speaker=voice,
                language=corp["C"],
                label=corp["E"],
                expect_result=corp["F"],
                audio_path=url,
                is_tts = True
            )
        save_corpus = CorpusOperateDao.saveTestCorpus(corpus)
        CorpusOperateDao.updateAudio(save_audio.aud_id,{"corpus_id": save_corpus.corpus_id})
    return {"success": True}

def test_corpus_create(data):
    if "aud_id" not in data or data["aud_id"] == "":
        return {}
    # random_str = generate_random_string()
    filepath = get_file_dir()
    file_path = os.path.join(filepath, data["audio_url"])
    new_path = move_file_to_folder(file_path, "test_corpus")
    corpus = TestCorpus(
        aud_id = data["aud_id"],
        text = data["text"],
        pinyin = data["pinyin"],
        test_scenario = data["test_scenario"],
        test_type = data["test_type"],
        evaluation_metric = data["evaluation_metric"],
        audio_url = data["audio_url"],
        audio_duration = data["audio_duration"],
        speaker = data["speaker"],
        language = data["language"],
        car_function = data["car_function"],
        expect_result = data["expect_result"],
        audio_path=new_path
        )
    save_corpus = CorpusOperateDao.saveTestCorpus(corpus)
    updated_data = {"corpus_id": save_corpus.corpus_id, "aud_url": new_path}
    update_audio = CorpusOperateDao.updateAudio(data["aud_id"], updated_data)
    return {
        "status": "success",
        "error_msg": ""
    }

def upload_testcorpus(corpus_id, aud_id, audio_url, pinyin, audio_duration, text):
    if aud_id == "":
        return "aud_id is null"
    filepath = get_file_dir()
    file_path = os.path.join(filepath, audio_url)
    new_path = ""
    if os.path.exists(file_path):
        new_path = move_file_to_folder(file_path, "test_corpus")
    else:
        filepath1 = os.path.join(filepath, "test_corpus")
        filepath2 = os.path.join(filepath1, audio_url)
        if os.path.exists(filepath2):
            new_path = filepath2
        else:
            return "No available audio file could be found"
    corpus_data = {
        "text": text,
        "pinyin": pinyin,
        "aud_id": aud_id,
        "audio_url": audio_url,
        "audio_path": new_path,
        "audio_duration": audio_duration
    }

    update_corpus = CorpusOperateDao.updateTestCorpus(corpus_id, corpus_data)
    audio_data = {"corpus_id": corpus_id, "aud_url": new_path}
    update_audio = CorpusOperateDao.updateAudio(aud_id, audio_data)
    return 0

def create_testcorpus(text, test_type, test_scenario, speaker, language, car_function, label, expect_result):
    file_name_pinyin = chinese_to_pinyin(text)
    corpus = TestCorpus(
        text = text,
        pinyin = file_name_pinyin,
        test_scenario = test_scenario,
        test_type = test_type,
        speaker = speaker,
        language = language,
        car_function = car_function,
        label = label,
        expect_result = expect_result
        )
    save_corpus = CorpusOperateDao.saveTestCorpus(corpus)
    return save_corpus

def synthesize_testcorpus(corpus_ids, label, is_tone):
    svc = SynthesizeSvc()
    for corpus_id in corpus_ids:
        corpus = CorpusQueryDao.findTestCorpusById(corpus_id)
        random_audio_id = generate_random_string()
        voice = -1
        if corpus.speaker == "male":
            voice = 1
        elif corpus.speaker == "female":
            voice = 2
        ret, url = svc.synthesize(corpus.text, random_audio_id, voice, int(corpus.language), 1, is_tone)
        if ret:
            return "synthesize_testcorpus fail"
        duration = get_audio_duration(url)
        if duration["status"] == "error":
            if os.path.exists(url):
                os.remove(url)
            return duration["data"]
        audio = CorpusAudio(
            corpus_id=corpus_id,
            aud_url=url,
            pinyin=corpus.pinyin,
            audio_duration=duration["data"]
        )
        save_audio = CorpusOperateDao.saveAudio(audio)
        name = os.path.basename(url)
        updated_data = {
            "aud_id":save_audio.aud_id,
            "audio_url":name,
            "audio_duration":duration["data"],
            "audio_path":url,
            "label":label,
            "is_tts":True
        }
        CorpusOperateDao.updateTestCorpus(corpus_id, updated_data)
    return 0

def test_corpus_update(data):
    find_corpus = {"corpus_id": data["corpus_id"]}
    in_use = PlanQueryDao.showAllTCorpusTree(find_corpus)
    for ii in in_use:
        plan = PlanQueryDao.findProjectPlanById(ii.plan_id)
        check_status = ProjectQueryDao.findTestProjectById(plan.project_id)
        if check_status.project_status == "progressing":
            return {
                "status": "error",
                "error_msg": "the test_corpus is in use"
            }
    updated_data = {
        "text": data["text"],
        "pinyin": data["pinyin"],
        "test_scenario": data["test_scenario"],
        "test_type": data["test_type"],
        "evaluation_metric": data["evaluation_metric"],
        "audio_url": data["audio_url"],
        "audio_duration": data["audio_duration"],
        "speaker": data["speaker"],
        "language": data["language"],
        "car_function": data["car_function"],
        "expect_result": data["expect_result"]
    }

    update_corpus = CorpusOperateDao.updateTestCorpus(data["corpus_id"], updated_data)
    return {
        "status": "success",
        "error_msg": ""
    }
def update_testcorpus(corpus_id, text, test_type, test_scenario, speaker, language, car_function, label, expect_result):
    find_corpus = {"corpus_id": corpus_id}
    in_use = PlanQueryDao.showAllTCorpusTree(find_corpus)
    for ii in in_use:
        plan = PlanQueryDao.findProjectPlanById(ii.plan_id)
        check_status = ProjectQueryDao.findTestProjectById(plan.project_id)
        if check_status.project_status == "progressing":
            return "the test_corpus is in use"
    file_name_pinyin = chinese_to_pinyin(text)
    updated_data = {
        "text": text,
        "pinyin": file_name_pinyin,
        "test_scenario": test_scenario,
        "test_type": test_type,
        "speaker": speaker,
        "language": language,
        "car_function": car_function,
        "label": label,
        "expect_result": expect_result
    }

    update_corpus = CorpusOperateDao.updateTestCorpus(corpus_id, updated_data)
    return 0

def test_corpus_delete(data):
    find_corpus = {"corpus_id": data["corpus_id"]}
    in_use = PlanQueryDao.showAllTCorpusTree(find_corpus)
    if len(in_use) != 0:
        return {
            "status": "error",
            "error_msg": "the corpus is in use"
        }
    corpus = CorpusQueryDao.findTestCorpusById(data["corpus_id"])
    audio = CorpusQueryDao.findAudioById(corpus.aud_id)
    if os.path.exists(audio.aud_url):
        os.remove(audio.aud_url)
    delete_audio = CorpusOperateDao.deleteAudio(audio.aud_id)
    delete_corpus = CorpusOperateDao.deleteTestCorpus(data["corpus_id"])
    return {
        "status": "success",
        "error_msg": ""
    }

def delete_testcorpus(corpus_id):
    find_corpus = {"corpus_id": corpus_id}
    in_use = PlanQueryDao.showAllTCorpusTree(find_corpus)
    if len(in_use) != 0:
        return "the corpus is in use"
    corpus = CorpusQueryDao.findTestCorpusById(corpus_id)
    if corpus is None:
        return 0
    if corpus.aud_id is not None:
        audio = CorpusQueryDao.findAudioById(corpus.aud_id)
        if os.path.exists(audio.aud_url):
            os.remove(audio.aud_url)
        delete_audio = CorpusOperateDao.deleteAudio(audio.aud_id)
    delete_corpus = CorpusOperateDao.deleteTestCorpus(corpus_id)
    return 0

def test_corpus_list(data):
    corpus_list = CorpusQueryDao.showAllTestCorpus(data)
    res = []
    num = 0
    for corpus in corpus_list:
        temp = {}
        if "mul_" in corpus.corpus_id:
            continue
        temp["corpus_id"] = corpus.corpus_id
        temp["aud_id"] = corpus.aud_id
        temp["text"] = corpus.text
        temp["pinyin"] = corpus.pinyin
        temp["test_scenario"] = corpus.test_scenario
        temp["test_type"] = corpus.test_type
        temp["evaluation_metric"] = corpus.evaluation_metric
        temp["audio_url"] = corpus.audio_url
        temp["audio_duration"] = corpus.audio_duration
        temp["speaker"] = corpus.speaker
        temp["language"] = corpus.language
        temp["label"] = corpus.label
        temp["operation"] = corpus.operation
        temp["car_function"] = corpus.car_function
        temp["expect_result"] = corpus.expect_result
        temp["audio_path"] = corpus.audio_path
        temp["is_tts"] = corpus.is_tts

        res.append(temp)
        num += 1
    res.reverse()
    return {"data": res, 'total': num}

def rouse_corpus_create(data):
    if "aud_id" not in data or data["aud_id"] == "":
        return {}
    # random_str = generate_random_string()
    filepath = get_file_dir()
    file_path = os.path.join(filepath, data["audio_url"])
    new_path = move_file_to_folder(file_path, "rouse_corpus")
    corpus = RouseCorpus(
        aud_id = data["aud_id"],
        text = data["text"],
        pinyin = data["pinyin"],
        test_scenario = data["test_scenario"],
        test_object = data["test_object"],
        audio_url = data["audio_url"],
        audio_duration = data["audio_duration"],
        speaker = data["speaker"],
        language = data["language"],
        audio_path=new_path
        )
    save_corpus = CorpusOperateDao.saveRouseCorpus(corpus)
    updated_data = {"corpus_id": save_corpus.corpus_id, "aud_url": new_path}
    update_audio = CorpusOperateDao.updateAudio(data["aud_id"], updated_data)
    return {
        "status": "success",
        "error_msg": ""
    }

def create_rousecorpus(text, test_scenario, speaker, language, label):
    file_name_pinyin = chinese_to_pinyin(text)
    corpus = RouseCorpus(
        text = text,
        pinyin = file_name_pinyin,
        test_scenario = test_scenario,
        speaker = speaker,
        language = language,
        label = label
        )
    save_corpus = CorpusOperateDao.saveRouseCorpus(corpus)
    return save_corpus

def update_rousecorpus(corpus_id, text, test_scenario, speaker, language, label):
    find_corpus = {"corpus_id": corpus_id}
    in_use = PlanQueryDao.showAllRCorpusTree(find_corpus)
    for ii in in_use:
        plan = PlanQueryDao.findProjectPlanById(ii.plan_id)
        check_status = ProjectQueryDao.findTestProjectById(plan.project_id)
        if check_status.project_status == "progressing":
            return "the rouse_corpus is in use"
    file_name_pinyin = chinese_to_pinyin(text)
    updated_data = {
        "text": text,
        "pinyin": file_name_pinyin,
        "test_scenario": test_scenario,
        "speaker": speaker,
        "language": language,
        "label": label
    }

    update_corpus = CorpusOperateDao.updateRouseCorpus(corpus_id, updated_data)
    return 0

def upload_rousecorpus(corpus_id, aud_id, audio_url, pinyin, audio_duration, text):
    if aud_id == "":
        return "aud_id is null"
    filepath = get_file_dir()
    file_path = os.path.join(filepath, audio_url)
    new_path = move_file_to_folder(file_path, "rouse_corpus")
    corpus_data = {
        "text": text,
        "pinyin": pinyin,
        "aud_id": aud_id,
        "audio_url": audio_url,
        "audio_path": new_path,
        "audio_duration": audio_duration
    }

    update_corpus = CorpusOperateDao.updateRouseCorpus(corpus_id, corpus_data)
    audio_data = {"corpus_id": corpus_id, "aud_url": new_path}
    update_audio = CorpusOperateDao.updateAudio(aud_id, audio_data)
    return 0

def delete_rousecorpus(corpus_id):
    find_corpus = {"corpus_id": corpus_id}
    in_use = PlanQueryDao.showAllRCorpusTree(find_corpus)
    if len(in_use) != 0:
        return "the corpus is in use"
    corpus = CorpusQueryDao.findRouseCorpusById(corpus_id)
    if corpus is None:
        return 0
    if corpus.aud_id is not None:
        audio = CorpusQueryDao.findAudioById(corpus.aud_id)
        if os.path.exists(audio.aud_url):
            os.remove(audio.aud_url)
        delete_audio = CorpusOperateDao.deleteAudio(audio.aud_id)
    delete_corpus = CorpusOperateDao.deleteRouseCorpus(corpus_id)
    return 0

def rouse_corpus_update(data):
    find_corpus = {"corpus_id": data["corpus_id"]}
    in_use = PlanQueryDao.showAllRCorpusTree(find_corpus)
    for ii in in_use:
        plan = PlanQueryDao.findProjectPlanById(ii.plan_id)
        check_status = ProjectQueryDao.findTestProjectById(plan.project_id)
        if check_status.project_status == "progressing":
            return {
                "status": "error",
                "error_msg": "the rouse_corpus is in use"
            }
    updated_data = {
        "text": data["text"],
        "pinyin": data["pinyin"],
        "test_scenario": data["test_scenario"],
        "test_object": data["test_object"],
        "audio_url": data["audio_url"],
        "audio_duration": data["audio_duration"],
        "speaker": data["speaker"],
        "language": data["language"]
    }

    update_corpus = CorpusOperateDao.updateRouseCorpus(data["corpus_id"], updated_data)
    return {
        "status": "success",
        "error_msg": ""
    }

def rouse_corpus_delete(data):
    find_corpus = {"corpus_id": data["corpus_id"]}
    in_use = PlanQueryDao.showAllRCorpusTree(find_corpus)
    if len(in_use) != 0:
        return {
            "status": "error",
            "error_msg": "the corpus is in use"
        }
    corpus = CorpusQueryDao.findRouseCorpusById(data["corpus_id"])
    audio = CorpusQueryDao.findAudioById(corpus.aud_id)
    if os.path.exists(audio.aud_url):
        os.remove(audio.aud_url)
    delete_audio = CorpusOperateDao.deleteAudio(audio.aud_id)
    delete_corpus = CorpusOperateDao.deleteRouseCorpus(data["corpus_id"])
    return {
        "status": "success",
        "error_msg": ""
    }

def synthesize_rousecorpus(corpus_ids, label):
    svc = SynthesizeSvc()
    for corpus_id in corpus_ids:
        corpus = CorpusQueryDao.findRouseCorpusById(corpus_id)
        random_audio_id = generate_random_string()
        voice = -1
        if corpus.speaker == "male":
            voice = 1
        elif corpus.speaker == "female":
            voice = 2
        ret, url = svc.synthesize(corpus.text, random_audio_id, voice, int(corpus.language), 2)
        if ret:
            return "synthesize_rousecorpus fail"
        duration = get_audio_duration(url)
        if duration["status"] == "error":
            if os.path.exists(url):
                os.remove(url)
            return duration["data"]
        audio = CorpusAudio(
            corpus_id=corpus_id,
            aud_url=url,
            pinyin=corpus.pinyin,
            audio_duration=duration["data"]
        )
        save_audio = CorpusOperateDao.saveAudio(audio)
        name = os.path.basename(url)
        updated_data = {
            "aud_id":save_audio.aud_id,
            "audio_url":name,
            "audio_duration":duration["data"],
            "audio_path":url,
            "label":label,
            "is_tts":True
        }
        CorpusOperateDao.updateRouseCorpus(corpus_id, updated_data)
    return 0

def rouse_corpus_list(data):
    corpus_list = CorpusQueryDao.showAllRouseCorpus(data)
    res = []
    num = 0
    for corpus in corpus_list:
        temp = {}
        temp["corpus_id"] = corpus.corpus_id
        temp["aud_id"] = corpus.aud_id
        temp["text"] = corpus.text
        temp["pinyin"] = corpus.pinyin
        temp["test_scenario"] = corpus.test_scenario
        temp["test_object"] = corpus.test_object
        temp["audio_url"] = corpus.audio_url
        temp["audio_duration"] = corpus.audio_duration
        temp["speaker"] = corpus.speaker
        temp["language"] = corpus.language
        temp["label"] = corpus.label
        temp["operation"] = corpus.operation
        temp["audio_path"] = corpus.audio_path
        temp["is_tts"] = corpus.is_tts
        res.append(temp)
        num += 1
    res.reverse()
    return {"data": res, 'total': num}

def disturb_corpus_create(data):
    if "aud_id" not in data or data["aud_id"] == "":
        return {}
    # random_str = generate_random_string()
    filepath = get_file_dir()
    file_path = os.path.join(filepath, data["audio_url"])
    new_path = move_file_to_folder(file_path, "disturb_corpus")
    corpus = DisturbCorpus(
        aud_id = data["aud_id"],
        text = data["text"],
        pinyin = data["pinyin"],
        audio_url = data["audio_url"],
        audio_duration = data["audio_duration"],
        speaker = data["speaker"],
        language = data["language"],
        audio_path=new_path
        )
    save_corpus = CorpusOperateDao.saveDisturbCorpus(corpus)
    updated_data = {"corpus_id": save_corpus.corpus_id, "aud_url": new_path}
    update_audio = CorpusOperateDao.updateAudio(data["aud_id"], updated_data)
    return {
        "status": "success",
        "error_msg": ""
    }

def disturb_corpus_update(data):
    find_corpus = {"corpus_id": data["corpus_id"]}
    in_use = PlanQueryDao.showAllDCorpusTree(find_corpus)
    for ii in in_use:
        plan = PlanQueryDao.findProjectPlanById(ii.plan_id)
        check_status = ProjectQueryDao.findTestProjectById(plan.project_id)
        if check_status.project_status == "progressing":
            return {
                "status": "error",
                "error_msg": "the rouse_corpus is in use"
            }
    updated_data = {
        "text": data["text"],
        "pinyin": data["pinyin"],
        "audio_url": data["audio_url"],
        "audio_duration": data["audio_duration"],
        "speaker": data["speaker"],
        "language": data["language"]
    }

    update_corpus = CorpusOperateDao.updateDisturbCorpus(data["corpus_id"], updated_data)
    return {
        "status": "success",
        "error_msg": ""
    }

def disturb_corpus_delete(data):
    find_corpus = {"corpus_id": data["corpus_id"]}
    in_use = PlanQueryDao.showAllDCorpusTree(find_corpus)
    if len(in_use) != 0:
        return {
            "status": "error",
            "error_msg": "the corpus is in use"
        }
    corpus = CorpusQueryDao.findDisturbCorpusById(data["corpus_id"])
    audio = CorpusQueryDao.findAudioById(corpus.aud_id)
    if os.path.exists(audio.aud_url):
        os.remove(audio.aud_url)
    delete_audio = CorpusOperateDao.deleteAudio(audio.aud_id)
    delete_corpus = CorpusOperateDao.deleteDisturbCorpus(data["corpus_id"])
    return {
        "status": "success",
        "error_msg": ""
    }

def disturb_corpus_list(data):
    corpus_list = CorpusQueryDao.showAllDisturbCorpus(data)
    res = []
    num = 0
    for corpus in corpus_list:
        temp = {}
        temp["corpus_id"] = corpus.corpus_id
        temp["aud_id"] = corpus.aud_id
        temp["text"] = corpus.text
        temp["pinyin"] = corpus.pinyin
        temp["audio_url"] = corpus.audio_url
        temp["audio_duration"] = corpus.audio_duration
        temp["speaker"] = corpus.speaker
        temp["language"] = corpus.language
        temp["label"] = corpus.label
        temp["operation"] = corpus.operation
        temp["audio_path"] = corpus.audio_path
        temp["is_tts"] = corpus.is_tts
        res.append(temp)
        num += 1
    res.reverse()
    return {"data": res, 'total': num}

def background_noise_create(data):
    if "aud_id" not in data or data["aud_id"] == "":
        return {}
    # random_str = generate_random_string()
    filepath = get_file_dir()
    file_path = os.path.join(filepath, data["audio_url"])
    new_path = move_file_to_folder(file_path, "background_noise")
    corpus = BackgroundNoise(
        aud_id = data["aud_id"],
        text = data["text"],
        pinyin = data.get('pinyin', ''),
        noise_environ = data["noise_environ"],
        audio_url = data["audio_url"],
        audio_duration = data["audio_duration"],
        audio_path=new_path
        )
    save_corpus = CorpusOperateDao.saveBackgroundNoise(corpus)
    updated_data = {"corpus_id": save_corpus.corpus_id, "aud_url": new_path}
    update_audio = CorpusOperateDao.updateAudio(data["aud_id"], updated_data)
    return {
        "status": "success",
        "error_msg": ""
    }

def background_noise_update(data):
    find_corpus = {"corpus_id": data["corpus_id"]}
    in_use = PlanQueryDao.showAllBNoiseTree(find_corpus)
    for ii in in_use:
        plan = PlanQueryDao.findProjectPlanById(ii.plan_id)
        check_status = ProjectQueryDao.findTestProjectById(plan.project_id)
        if check_status.project_status == "progressing":
            return {
                "status": "error",
                "error_msg": "the rouse_corpus is in use"
            }
    updated_data = {
        "text": data["text"],
        "pinyin": data["pinyin"],
        "noise_environ": data["test_scenario"],
        "audio_url": data["audio_url"],
        "audio_duration": data["audio_duration"],
    }

    update_corpus = CorpusOperateDao.updateBackgroundNoise(data["corpus_id"], updated_data)
    return {
        "status": "success",
        "error_msg": ""
    }

def background_noise_delete(data):
    find_corpus = {"corpus_id": data["corpus_id"]}
    in_use = PlanQueryDao.showAllBNoiseTree(find_corpus)
    if len(in_use) != 0:
        return {
            "status": "error",
            "error_msg": "the corpus is in use"
        }
    corpus = CorpusQueryDao.findBackgroundNoiseById(data["corpus_id"])
    audio = CorpusQueryDao.findAudioById(corpus.aud_id)
    if os.path.exists(audio.aud_url):
        os.remove(audio.aud_url)
    delete_audio = CorpusOperateDao.deleteAudio(audio.aud_id)
    delete_corpus = CorpusOperateDao.deleteBackgroundNoise(data["corpus_id"])
    return {
        "status": "success",
        "error_msg": ""
    }

def background_noise_list(data):
    corpus_list = CorpusQueryDao.showAllBackgroundNoise(data)
    res = []
    num = 0
    for corpus in corpus_list:
        temp = {}
        temp["corpus_id"] = corpus.corpus_id
        temp["aud_id"] = corpus.aud_id
        temp["text"] = corpus.text
        temp["pinyin"] = corpus.pinyin
        temp["noise_environ"] = corpus.noise_environ
        temp["audio_url"] = corpus.audio_url
        temp["audio_duration"] = corpus.audio_duration
        temp["label"] = corpus.label
        temp["operation"] = corpus.operation
        temp["audio_path"] = corpus.audio_path
        res.append(temp)
        num += 1
    res.reverse()
    return {"data": res, 'total': num}

def test_corpus_batch_delete(data):
    if "corpus_ids" not in data and len(data["corpus_ids"]) == 0:
        return "No corpus was found to delete"
    for corpus_temp in data["corpus_ids"]:
        find_corpus = {"corpus_id": corpus_temp}
        in_use = PlanQueryDao.showAllTCorpusTree(find_corpus)
        if len(in_use) != 0:
            continue
        corpus = CorpusQueryDao.findTestCorpusById(corpus_temp)
        audio = CorpusQueryDao.findAudioById(corpus.aud_id)
        if os.path.exists(audio.aud_url):
            os.remove(audio.aud_url)
        delete_audio = CorpusOperateDao.deleteAudio(audio.aud_id)
        delete_corpus = CorpusOperateDao.deleteTestCorpus(corpus_temp)
    return {
        "status": "success",
        "error_msg": ""
    }

def batch_delete_testcorpus(corpus_ids):
    delete_error = []
    if len(corpus_ids) == 0:
        return "No corpus was found to delete"
    for corpus_temp in corpus_ids:
        find_corpus = {"corpus_id": corpus_temp}
        in_use = PlanQueryDao.showAllTCorpusTree(find_corpus)
        if len(in_use) != 0:
            delete_error.append(corpus_temp)
            continue
        corpus = CorpusQueryDao.findTestCorpusById(corpus_temp)
        if corpus is None:
            continue
        if corpus.aud_id is not None:
            audio = CorpusQueryDao.findAudioById(corpus.aud_id)
            if os.path.exists(audio.aud_url):
                os.remove(audio.aud_url)
            delete_audio = CorpusOperateDao.deleteAudio(audio.aud_id)
        delete_corpus = CorpusOperateDao.deleteTestCorpus(corpus_temp)
    return delete_error

def batch_delete_rousecorpus(corpus_ids):
    delete_error = []
    if len(corpus_ids) == 0:
        return "No corpus was found to delete"
    for corpus_temp in corpus_ids:
        find_corpus = {"corpus_id": corpus_temp}
        in_use = PlanQueryDao.showAllRCorpusTree(find_corpus)
        if len(in_use) != 0:
            delete_error.append(corpus_temp)
            continue
        corpus = CorpusQueryDao.findRouseCorpusById(corpus_temp)
        if corpus is None:
            continue
        if corpus.aud_id is not None:
            audio = CorpusQueryDao.findAudioById(corpus.aud_id)
            if os.path.exists(audio.aud_url):
                os.remove(audio.aud_url)
            delete_audio = CorpusOperateDao.deleteAudio(audio.aud_id)
        delete_corpus = CorpusOperateDao.deleteRouseCorpus(corpus_temp)
    return delete_error

def rouse_corpus_batch_delete(data):
    if "corpus_ids" not in data and len(data["corpus_ids"]) == 0:
        return "No corpus was found to delete"
    for corpus_temp in data["corpus_ids"]:
        find_corpus = {"corpus_id": corpus_temp}
        in_use = PlanQueryDao.showAllRCorpusTree(find_corpus)
        if len(in_use) != 0:
            continue
        corpus = CorpusQueryDao.findRouseCorpusById(corpus_temp)
        audio = CorpusQueryDao.findAudioById(corpus.aud_id)
        if os.path.exists(audio.aud_url):
            os.remove(audio.aud_url)
        delete_audio = CorpusOperateDao.deleteAudio(audio.aud_id)
        delete_corpus = CorpusOperateDao.deleteRouseCorpus(corpus_temp)
    return {
        "status": "success",
        "error_msg": ""
    }

# 多伦对话语料
def create_mulcorpus(corpus_name, test_type, test_scenario, speaker, language, car_function, label, corpusItems, mulcorpus_id=""):
    if mulcorpus_id == "":
        mulcorpus_id = generate_random_string()
    corpus_list = []
    for audio in corpusItems:
        text = audio["text"]
        audio_url = audio["audio_url"]
        audio_duration = audio["audio_duration"]
        expect_result = audio["expect_result"]
        aud_id = audio["aud_id"]
        pinyin = chinese_to_pinyin(text)
        # corpus_id = "mul_" + generate_random_string()
        save_corpus = create_testcorpus(text, test_type, test_scenario, speaker, language, car_function, label, expect_result)
        ret = upload_testcorpus(save_corpus.corpus_id, aud_id, audio_url, pinyin, audio_duration, text)
        if ret ==  0:
            corpus = MultiCorpus(corpus_id = mulcorpus_id, testcorpus_id = save_corpus.corpus_id, corpus_name = corpus_name, is_delete = False)
            corpus_list.append(corpus)
    CorpusOperateDao.saveMultiCorpusList(corpus_list)
    return 0

def update_mulcorpus(corpus_name, corpus_id, test_type, test_scenario, speaker, language, car_function, label, corpusItems):
    find_corpus = {"corpus_id": corpus_id}
    in_use = PlanQueryDao.showAllTCorpusTree(find_corpus)
    for ii in in_use:
        plan = PlanQueryDao.findProjectPlanById(ii.plan_id)
        check_status = ProjectQueryDao.findTestProjectById(plan.project_id)
        if check_status.project_status == "progressing":
            return "the multi_corpus is in use"
    # 删数据库，不删对应的音频 和 audio_id
    mult_corpus_list = CorpusQueryDao.findMultiCorpusById(corpus_id)
    # for cor in mult_corpus_list:
    #     CorpusOperateDao.deleteTestCorpus(cor.testcorpus_id)
    # CorpusOperateDao.deleteMultiCorpus(corpus_id)
    update_data = {"is_delete": True}
    CorpusOperateDao.updateMultiCorpus(corpus_id, update_data)

    create_mulcorpus(corpus_name, test_type, test_scenario, speaker, language, car_function, label, corpusItems, corpus_id)
    return 0

def delete_mulcorpus(corpus_id):
    find_corpus = {"corpus_id": corpus_id}
    in_use = PlanQueryDao.showAllTCorpusTree(find_corpus)
    for ii in in_use:
        plan = PlanQueryDao.findProjectPlanById(ii.plan_id)
        check_status = ProjectQueryDao.findTestProjectById(plan.project_id)
        if check_status.project_status == "progressing":
            return "the multi_corpus is in use"
    # 删数据库，并删除对应的音频 和 audio_id
    mult_corpus_list = CorpusQueryDao.findMultiCorpusById(corpus_id)
    for cor in mult_corpus_list:
        delete_testcorpus(cor.testcorpus_id)
    CorpusOperateDao.deleteMultiCorpus(corpus_id)
    return 0

def batch_delete_mulcorpus(corpus_ids):
    fail_list = []
    for corpus in corpus_ids:
        ret = delete_mulcorpus(corpus)
        if ret != 0:
            fail_list.append(corpus)
    return fail_list

def mul_corpus_list(data):
    temp_list = CorpusQueryDao.showAllMultiCorpus(data)
    res = []
    num = 0
    seen = set()
    corpus_list = []
    for i in temp_list:
        id = i.corpus_id
        name = i.corpus_name
        if id not in seen:
            xxxx = {"id":id, "name":name}
            corpus_list.append(xxxx)
            seen.add(id)
            
    for tttt in corpus_list:
        corpus_id = tttt["id"]
        corpus_name = tttt["name"]
        temp = {}
        first = True
        audio_list = []
        for ii in temp_list:
            if ii.corpus_id == corpus_id and ii.is_delete == False:
                corpus = CorpusQueryDao.findTestCorpusById(ii.testcorpus_id)
                if first:
                    temp["corpus_id"] = corpus_id
                    temp["corpus_name"] = corpus_name
                    temp["test_scenario"] = corpus.test_scenario
                    temp["test_type"] = corpus.test_type
                    temp["speaker"] = corpus.speaker
                    temp["language"] = corpus.language
                    temp["label"] = corpus.label
                    temp["car_function"] = corpus.car_function
                    first = False
                
                audio = {}
                audio["aud_id"] = corpus.aud_id
                audio["text"] = corpus.text
                audio["audio_url"] = corpus.audio_url
                audio["audio_duration"] = corpus.audio_duration
                audio["expect_result"] = corpus.expect_result
                audio_list.append(audio)
        temp["corpusItems"] = audio_list
        res.append(temp)
        num += 1
    res.reverse()
    return {"data": res, 'total': num}

def get_multi_testcorpus(multi_id):
    temp_list = CorpusQueryDao.findMultiCorpusById(multi_id)
    res = []
    for ii in temp_list:
        if ii.is_delete == False:
            res.append(ii.testcorpus_id)
    return res