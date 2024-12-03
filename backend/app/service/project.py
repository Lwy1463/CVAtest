
from app.utils.utils import generate_random_string
from app.dao.project_dao import ProjectOperateDao, ProjectQueryDao
from app.dao.plan_dao import PlanQueryDao
from app.service.plan import delete_test_plan
from app.dao.models.sqlite_gen import TestProject
from app.dao.result_dao import ResultQueryDao, ResultOperateDao
import os

def test_project_create(data):
    # random_str = generate_random_string()
    project = TestProject(
        project_name = data["project_name"],
        project_code = data["project_code"],
        description = data["description"]
        # test_object = data["test_object"],
        # project_status = data["project_status"]
        )
    save_project = ProjectOperateDao.saveTestProject(project)
    return {
        "status": "success",
        "error_msg": ""
    }

def test_project_update(data):
    updated_data = {
        "project_name": data["project_name"],
        "project_code": data["project_code"],
        "description": data["description"]
        # "test_object": data["test_object"],
        # "project_status": data["project_status"]
    }

    update_project = ProjectOperateDao.updateTestProject(data["project_id"], updated_data)
    return {
        "status": "success",
        "error_msg": ""
    }

def test_project_delete(data):
    plan_list = PlanQueryDao.showAllProjectPlan(data)
    for plan in plan_list:
        d_data = {"plan_id": plan.plan_id}
        res = delete_test_plan(d_data)
        if res["status"] == "error":
            return {
                "status": "success",
                "error_msg": res["error_msg"]
            }
    # 删除项目
    ProjectOperateDao.deleteTestProject(data["project_id"])
    return {
        "status": "success",
        "error_msg": ""
    }

def test_project_list(data):
    project_list = ProjectQueryDao.showAllTestProject(data)
    res = []
    num = 0
    for project in project_list:
        temp = {}
        temp["project_id"] = project.project_id
        temp["project_name"] = project.project_name
        temp["project_code"] = project.project_code
        temp["description"] = project.description
        # temp["test_object"] = project.test_object
        # temp["project_status"] = project.project_status

        res.append(temp)
        num += 1
    return {"data": res, 'total': num}

def test_result_check(project_id, turn_id, result_id, result):
    res = ResultQueryDao.findTestResultById(result_id)
    if res is None:
        return " No result_id was found available "
    updata_data = {
        "result": result
    }
    ResultOperateDao.updateTestResult(result_id, updata_data)
    return 0