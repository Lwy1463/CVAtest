
from fastapi import APIRouter,File, UploadFile, Form, Request
from fastapi.responses import JSONResponse
from app.service.corpus import create_mulcorpus, update_mulcorpus, delete_mulcorpus, mul_corpus_list,\
                batch_delete_mulcorpus
import json
from app.proto.multi_corpus_proto import MultiCorpusCreateRequest, MultiCorpusUpdateRequest, CorpusDeleteRequest,\
    CorpusBatchDeleteRequest

router = APIRouter(prefix="/multi-corpus")

# 测试语料
@router.post("/create")
async def create(req: MultiCorpusCreateRequest):
    ret = create_mulcorpus(req.corpus_name, req.test_type, req.test_scenario, req.speaker, req.language, req.car_function, req.label, req.corpusItems)
    if ret:
        return JSONResponse(status_code=500, content={"error": "multi corpus create fail"})
    return {
        "status": "success",
        "error_msg": ""
    }
    
@router.post("/update")
async def update(req: MultiCorpusUpdateRequest):
    ret = update_mulcorpus(req.corpus_name, req.corpus_id, req.test_type, req.test_scenario, req.speaker, req.language, req.car_function, req.label, req.corpusItems)
    if ret:
        return JSONResponse(status_code=500, content={"error": f"multi corpus update fail, {ret}"})
    return {
        "status": "success",
        "error_msg": ""
    }

@router.post("/delete")
async def delete(req: CorpusDeleteRequest):
    ret = delete_mulcorpus(req.corpus_id)
    if ret:
        return JSONResponse(status_code=500, content={"error": f"multi corpus delete fail, {ret}"})
    return {
        "status": "success",
        "error_msg": ""
    }

@router.post("/batchDelete")
async def batchDelete(req: CorpusBatchDeleteRequest):
    ret = batch_delete_mulcorpus(req.corpus_ids)
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

@router.post("/list")
async def list(request: Request):
    data = await request.json()

    res = mul_corpus_list(data)
    return res