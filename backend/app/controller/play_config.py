from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.service.play_config import play_config_create, play_config_update, play_config_delete, play_config_list
from app.proto.play_config_proto import PlayConfigCreateRequest, PlayConfigUpdateRequest, PlayConfigDeleteRequest
import json

router = APIRouter(prefix="/play_config")

@router.post("/create_play_config")
async def create_play_config(req: PlayConfigCreateRequest):
    ret = play_config_create(req.config_name, req.description, req.type)
    if ret:
        return JSONResponse(status_code=500, content={"error": "create_play_config fail"})
    return {"success": True}

@router.post("/update_play_config")
async def update_play_config(req: PlayConfigUpdateRequest):
    ret = play_config_update(req.play_config_id, req.config_name, req.description, req.type, req.configs)
    if ret:
        return JSONResponse(status_code=500, content={"error": "update_play_config fail"})
    return {"success": True}

@router.post("/delete_play_config")
async def delete_play_config(req: PlayConfigDeleteRequest):
    ret = play_config_delete(req.play_config_id)
    if ret:
        return JSONResponse(status_code=500, content={"error": "delete_play_config fail"})
    return {"success": True}

@router.post("/get_play_config_list")
async def get_play_config_list(request: Request):
    data = await request.json()

    res = play_config_list(data)
    return res