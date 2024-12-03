
from fastapi import APIRouter, Request, HTTPException
from openai import project
from fastapi.responses import JSONResponse
from app.service.project import test_project_create, test_project_update, test_project_delete, test_project_list, test_result_check
from app.service.plan import create_test_plan, update_test_plan, delete_test_plan, test_plan_list, get_corpuslist_byplanid, \
    save_corpuslist_byplanid, test_execute, get_recent_testinfo, test_suspend, update_test_result, get_turn_list, \
    get_review_video_name, get_excel_report
from app.utils.thread_manager import thread_manager
from app.proto.project_proto import TestResultCheckRequest, TestExportResultsRequest, GetTestInfoRequest
import json

router = APIRouter(prefix="/test_project")

# 测试项目管理
@router.post("/create_test_project")
async def create_test_project(request: Request):
    data = await request.json()

    res = test_project_create(data)
    return res

@router.post("/update_test_project")
async def update_test_project(request: Request):
    data = await request.json()

    res = test_project_update(data)
    return res

@router.post("/delete_test_project")
async def delete_test_project(request: Request):
    data = await request.json()

    res = test_project_delete(data)
    return res

@router.post("/get_test_project_list") # 此类结构需要注意，我直接用的传过来数据的 key 作为的查询 key，所以一定要和数据库存的字段相匹配
async def get_test_project_list(request: Request):
    data = await request.json()

    res = test_project_list(data)
    return res

@router.post("/create_plan")
async def create_plan(request: Request):
    data = await request.json()

    res = create_test_plan(data)
    return res


@router.post("/update_plan")
async def update_plan(request: Request):
    data = await request.json()

    res = update_test_plan(data)
    return res


@router.post("/delete_plan")
async def delete_plan(request: Request):
    data = await request.json()

    res = delete_test_plan(data)
    return res

@router.post("/get_plan_list")
async def get_plan_list(request: Request):
    data = await request.json()

    res = test_plan_list(data)
    return res

@router.post("/get_plan_detail")
async def get_plan_detail(request: Request):
    data = await request.json()

    res = get_corpuslist_byplanid(data["plan_id"])
    return res

@router.post("/save_plan_detail")
async def save_plan_detail(request: Request):
    data = await request.json()

    res = save_corpuslist_byplanid(data)
    return res

# 项目执行 根据方案内容 开始执行测试 生成测试进度和结果列表
@router.post("/start_test")
async def start_test(request: Request):
    data = await request.json()
    id = data["project_id"]
    
    try:
        thread_manager.start_thread(id, test_execute, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": f"Project {id} started"}

# 查询该项目 当前（最近一次执行）的测试信息 包括测试进度 结果列表 以及日志
@router.post("/get_test_info")
async def get_test_info(req: GetTestInfoRequest):
    res = get_recent_testinfo(req.project_id, req.turn_id, req.plan_id)
    return res

@router.post("/stop_test")
async def stop_test(request: Request):
    data = await request.json()
    # id = data["project_id"]
    # thread_manager.stop_thread(id)
    test_suspend(data)
    
    return {"message": f"Project {id} stopped"}

@router.post("/result_update")
async def result_update(request: Request):
    data = await request.json()

    res = update_test_result(data)
    return res

# @router.post("/test")
# async def test(request: Request):
#     dlh_test()
#     return {"ok"}


@router.post("/get_turns")
async def get_turns(request: Request):
    data = await request.json()
    turn_list = get_turn_list(data)
    return {"turns": turn_list}

@router.post("/get_video_name")
async def get_video_name(request: Request):
    data = await request.json()
    project_id = data["project_id"]
    turn_id = data["turn_id"]
    name = get_review_video_name(project_id, turn_id)
    return {"name": name}

@router.post("/export_results")
async def export_results(req: TestExportResultsRequest):
    file_url = get_excel_report(req.project_id, req.turn_id, req.type)
    if file_url != "":
        return {"status": "success", "url": file_url}
    else:
        return JSONResponse(status_code=500, content={"error": f"result_check fail, No reports were found available"})

@router.post("/result_check")
async def result_check(req: TestResultCheckRequest):
    ret = test_result_check(req.result_id, req.result)
    if ret:
        return JSONResponse(status_code=500, content={"error": f"result_check fail, {ret}"})
    return {
        "status": "success",
        "error_msg": "复核结果已成功更新"
    }