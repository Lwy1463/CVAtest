import os.path

from fastapi import APIRouter,File, UploadFile, Form
from fastapi.responses import JSONResponse
import json
import time
from torch.utils.tensorboard.summary import audio

from app.dao.models import RouseCorpus
from app.proto import SynthesizeListRequest, SynthesizeListResponse, SynthesizeProcessRequest, BatchSynthesizeProcessRequest, CorpusGeneralizate
from app.service.synthesize_svc import SynthesizeSvc
from app.utils.utils import chinese_to_pinyin, generate_random_string, get_audio_duration, get_file_dir
from app.dao.corpus_dao import CorpusOperateDao, CorpusQueryDao
from app.dao.models.sqlite_gen import CorpusAudio, TestCorpus, DisturbCorpus
from app.constant import Vocalists
from typing import List
from app.service.corpus import excel_create_syncorpus
from app.service.generalizate_svc import generalizate

router = APIRouter(prefix="/synthesize")


@router.post("/synthesize_list")
async def synthesize_list(req: SynthesizeListRequest):
    data = {
        "is_tts": True
    }
    res = []
    num = 0

    corpus_list = CorpusQueryDao.showAllTestCorpus(data)
    for corpus in corpus_list:
        temp = {"corpus_id": corpus.corpus_id, "aud_id": corpus.aud_id, "text": corpus.text, "pinyin": corpus.pinyin,
                "test_scenario": corpus.test_scenario, "evaluation_metric": corpus.evaluation_metric,
                "audio_url": corpus.audio_url, "audio_duration": corpus.audio_duration, "speaker": corpus.speaker,
                "language": corpus.language, "label": corpus.label, "operation": corpus.operation,
                "car_function": corpus.car_function, "audio_path": corpus.audio_path, "is_tts": corpus.is_tts}

        res.append(temp)
        num += 1

    corpus_list = CorpusQueryDao.showAllRouseCorpus(data)
    for corpus in corpus_list:
        temp = {"corpus_id": corpus.corpus_id, "aud_id": corpus.aud_id, "text": corpus.text, "pinyin": corpus.pinyin,
                "test_scenario": corpus.test_scenario, "test_object": corpus.test_object,
                "audio_url": corpus.audio_url, "audio_duration": corpus.audio_duration, "speaker": corpus.speaker,
                "language": corpus.language, "label": corpus.label, "operation": corpus.operation,
                "audio_path": corpus.audio_path, "is_tts": corpus.is_tts}

        res.append(temp)
        num += 1

    corpus_list = CorpusQueryDao.showAllDisturbCorpus(data)
    for corpus in corpus_list:
        temp = {"corpus_id": corpus.corpus_id, "aud_id": corpus.aud_id, "text": corpus.text, "pinyin": corpus.pinyin,
                "audio_url": corpus.audio_url, "audio_duration": corpus.audio_duration, "speaker": corpus.speaker,
                "language": corpus.language, "label": corpus.label, "operation": corpus.operation,
                "audio_path": corpus.audio_path, "is_tts": corpus.is_tts}

        res.append(temp)
        num += 1

    return {"data": res, 'total': num}

@router.post("/process_synthesize")
async def process_synthesize(req: SynthesizeProcessRequest):
    svc = SynthesizeSvc()
    ret, url = svc.synthesize(req.text, req.name, req.voice, req.language, req.type, req.is_tone)
    if ret:
        return JSONResponse(status_code=500, content={"error": "process_synthesize fail"})
    if (req.voice == 1 and req.language >= 7) or (req.voice == 2 and req.language >= 8):
        time.sleep(1)
    file_name_pinyin = chinese_to_pinyin(req.text)
    # random_audio_id = generate_random_string(0)
    # random_corpus_id = generate_random_string(1)
    duration = get_audio_duration(url)
    if duration["status"] == "error":
        os.remove(url)
        return JSONResponse(status_code=500, content={"error": duration["data"]})
    audio = CorpusAudio(
        aud_url=url,
        pinyin=file_name_pinyin,
        audio_duration=duration["data"]
    )
    save_audio = CorpusOperateDao.saveAudio(audio)
    name = os.path.basename(url)
    if req.voice == Vocalists.female:
        voice = "female"
    elif req.voice == Vocalists.male:
        voice = "male"
    else:
        voice = ""
    # language = "mandarin"
    if req.type == 2:
        corpus = RouseCorpus(
            aud_id=save_audio.aud_id,
            text=req.text,
            pinyin=file_name_pinyin,
            audio_url=name,
            audio_duration=duration["data"],
            speaker=voice,
            language=req.language,
            test_scenario="wake-up",
            label=req.label,
            audio_path=url,
            is_tts=True
        )
    elif req.type == 3:
        corpus = DisturbCorpus(
            aud_id=save_audio.aud_id,
            text=req.text,
            pinyin=file_name_pinyin,
            audio_url=name,
            audio_duration=duration["data"],
            speaker=voice,
            language=req.language,
            label=req.label,
            audio_path=url,
            is_tts=True
        )
    else:
        corpus = TestCorpus(
            aud_id=save_audio.aud_id,
            text=req.text,
            pinyin=file_name_pinyin,
            audio_url=name,
            audio_duration=duration["data"],
            speaker=voice,
            language=req.language,
            label=req.label,
            expect_result=req.expect_result,
            audio_path=url,
            is_tts=True
        )
    save_corpus = CorpusOperateDao.saveTestCorpus(corpus)
    CorpusOperateDao.updateAudio(save_audio.aud_id,{"corpus_id": save_corpus.corpus_id})
    return {"success": True}

@router.post("/batch_process_synthesize")
async def batch_process_synthesize(data_list: BatchSynthesizeProcessRequest):
    reqs = data_list.list
    for req in reqs:
        await process_synthesize(req)
    return {"success": True}

# 上传excel，批量生成 测试语料
@router.post("/batch_import")
async def upload_audio_file(file: UploadFile = File(...), info: str = Form(...)):
    data = json.loads(info)
    file_data = await file.read()
    res = excel_create_syncorpus(file, file_data, data)
    return res

@router.post("/corpus_generalizate")
async def corpus_generalizate(req: CorpusGeneralizate):
    result = []
    if req.text:
        result = generalizate(req.text)
    return {"list": result}
