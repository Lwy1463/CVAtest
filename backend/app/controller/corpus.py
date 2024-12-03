
from fastapi import APIRouter,File, UploadFile, Form, Request
from fastapi.responses import JSONResponse
from app.service.corpus import save_audio_file, create_testcorpus, update_testcorpus, delete_testcorpus, test_corpus_list,\
    create_rousecorpus, update_rousecorpus, delete_rousecorpus, rouse_corpus_list,\
        disturb_corpus_create, disturb_corpus_update, disturb_corpus_delete, disturb_corpus_list,\
            background_noise_create, background_noise_update, background_noise_delete, background_noise_list, excel_create_corpus,\
                batch_delete_testcorpus, batch_delete_rousecorpus, upload_testcorpus, synthesize_testcorpus, upload_rousecorpus, synthesize_rousecorpus
import json
from app.proto.corpus_proto import TestCorpusCreateRequest, TestCorpusUpdateRequest, CorpusDeleteRequest,\
    CorpusBatchDeleteRequest, TestCorpusUploadRequest, CorpusSynthesize, RouseCorpusCreateRequest,\
        RouseCorpusUpdateRequest

router = APIRouter(prefix="/corpus")


@router.post("/upload_audio_file")
async def upload_audio_file(file: UploadFile = File(...), info: str = Form(...)):
    data = json.loads(info)
    file_data = await file.read()
    res = save_audio_file(file, file_data, data)
    return res

# 上传excel，批量生成 测试语料
@router.post("/batch_import")
async def upload_audio_file(file: UploadFile = File(...), info: str = Form(...)):
    data = json.loads(info)
    file_data = await file.read()
    res = excel_create_corpus(file, file_data, data)
    return res

# 测试语料
@router.post("/synthesize_test_corpus")
async def synthesize_test_corpus(req: CorpusSynthesize):
    ret = synthesize_testcorpus(req.corpus_ids, req.label, req.is_tone)
    if ret:
        return JSONResponse(status_code=500, content={"error": "synthesize_test_corpus fail"})
    return {
        "status": "success",
        "error_msg": ""
    }

@router.post("/create_test_corpus")
async def create_test_corpus(req: TestCorpusCreateRequest):
    ret = create_testcorpus(req.text, req.test_type, req.test_scenario, req.speaker, req.language, req.car_function, req.label, req.expect_result)
    # if ret:
    #     return JSONResponse(status_code=500, content={"error": "create_test_corpus fail"})
    return {
        "status": "success",
        "error_msg": ""
    }
    
@router.post("/update_test_corpus")
async def update_test_corpus(req: TestCorpusUpdateRequest):
    ret = update_testcorpus(req.corpus_id, req.text, req.test_type, req.test_scenario, req.speaker, req.language, req.car_function, req.label, req.expect_result)
    if ret:
        return JSONResponse(status_code=500, content={"error": f"update_test_corpus fail, {ret}"})
    return {
        "status": "success",
        "error_msg": ""
    }

@router.post("/delete_test_corpus")
async def delete_test_corpus(req: CorpusDeleteRequest):
    ret = delete_testcorpus(req.corpus_id)
    if ret:
        return JSONResponse(status_code=500, content={"error": f"delete_test_corpus fail, {ret}"})
    return {
        "status": "success",
        "error_msg": ""
    }

@router.post("/batch_delete_test_corpus")
async def batch_delete_test_corpus(req: CorpusBatchDeleteRequest):
    ret = batch_delete_testcorpus(req.corpus_ids)
    if len(ret) == 0:
        return {
            "status": "success",
            "error_msg": ""
        }
    else:
        return {
            "status": "error",
            "error_list": ret
        }

@router.post("/upload_test_corpus")
async def upload_test_corpus(req: TestCorpusUploadRequest):
    ret = upload_testcorpus(req.corpus_id, req.aud_id, req.audio_url, req.pinyin, req.audio_duration, req.text)
    if ret:
        return JSONResponse(status_code=500, content={"error": f"upload_test_corpus fail, {ret}"})
    return {
        "status": "success",
        "error_msg": ""
    }

@router.post("/get_test_corpus_list") # 此类结构需要注意，我直接用的传过来数据的 key 作为的查询 key，所以一定要和数据库存的字段相匹配
async def get_test_corpus_list(request: Request):
    data = await request.json()

    res = test_corpus_list(data)
    return res

# 唤醒语料
@router.post("/create_rouse_corpus")
async def create_rouse_corpus(req: RouseCorpusCreateRequest):
    ret = create_rousecorpus(req.text, req.test_scenario, req.speaker, req.language, req.label)
    # if ret:
    #     return JSONResponse(status_code=500, content={"error": "create_rouse_corpus fail"})
    return {
        "status": "success",
        "error_msg": ""
    }

@router.post("/synthesize_rouse_corpus")
async def synthesize_rouse_corpus(req: CorpusSynthesize):
    ret = synthesize_rousecorpus(req.corpus_ids, req.label)
    if ret:
        return JSONResponse(status_code=500, content={"error": "synthesize_rouse_corpus fail"})
    return {
        "status": "success",
        "error_msg": ""
    }

@router.post("/update_rouse_corpus")
async def update_rouse_corpus(req: RouseCorpusUpdateRequest):
    ret = update_rousecorpus(req.corpus_id, req.text, req.test_scenario, req.speaker, req.language, req.label)
    if ret:
        return JSONResponse(status_code=500, content={"error": f"update_rouse_corpus fail, {ret}"})
    return {
        "status": "success",
        "error_msg": ""
    }

@router.post("/delete_rouse_corpus")
async def delete_rouse_corpus(req: CorpusDeleteRequest):
    ret = delete_rousecorpus(req.corpus_id)
    if ret:
        return JSONResponse(status_code=500, content={"error": f"delete_rouse_corpus fail, {ret}"})
    return {
        "status": "success",
        "error_msg": ""
    }

@router.post("/batch_delete_wake_corpus")
async def batch_delete_wake_corpus(req: CorpusBatchDeleteRequest):
    ret = batch_delete_rousecorpus(req.corpus_ids)
    if len(ret) == 0:
        return {
            "status": "success",
            "error_msg": ""
        }
    else:
        return {
            "status": "error",
            "error_list": ret
        }

@router.post("/upload_rouse_corpus")
async def upload_rouse_corpus(req: TestCorpusUploadRequest):
    ret = upload_rousecorpus(req.corpus_id, req.aud_id, req.audio_url, req.pinyin, req.audio_duration, req.text)
    if ret:
        return JSONResponse(status_code=500, content={"error": f"upload_rouse_corpus fail, {ret}"})
    return {
        "status": "success",
        "error_msg": ""
    }

@router.post("/get_rouse_corpus_list")
async def get_rouse_corpus_list(request: Request):
    data = await request.json()

    res = rouse_corpus_list(data)
    return res

# 干扰语料
@router.post("/create_disturb_corpus")
async def create_disturb_corpus(request: Request):
    data = await request.json()

    res = disturb_corpus_create(data)
    return res

@router.post("/update_disturb_corpus")
async def update_disturb_corpus(request: Request):
    data = await request.json()

    res = disturb_corpus_update(data)
    return res

@router.post("/delete_disturb_corpus")
async def delete_disturb_corpus(request: Request):
    data = await request.json()

    res = disturb_corpus_delete(data)
    return res

@router.post("/get_disturb_corpus_list")
async def get_disturb_corpus_list(request: Request):
    data = await request.json()

    res = disturb_corpus_list(data)
    return res

# 背景噪声
@router.post("/create_background_noise")
async def create_background_noise(request: Request):
    data = await request.json()

    res = background_noise_create(data)
    return res

@router.post("/update_background_noise")
async def update_background_noise(request: Request):
    data = await request.json()

    res = background_noise_update(data)
    return res

@router.post("/delete_background_noise")
async def delete_background_noise(request: Request):
    data = await request.json()

    res = background_noise_delete(data)
    return res

@router.post("/get_background_noise_list")
async def get_background_noise_list(request: Request):
    data = await request.json()

    res = background_noise_list(data)
    return res