from typing import Optional
from pydantic import BaseModel, Field

class TestResultCheckRequest(BaseModel):
    # project_id: Optional[str] = Field(..., description="项目id")
    # turn_id: Optional[str] = Field(default="", description="轮次id")
    result_id: Optional[str] = Field(default="", description="结果id")
    result: Optional[str] = Field(default="", description="结果")

class TestExportResultsRequest(BaseModel):
    project_id: Optional[str] = Field(default="", description="项目id")
    turn_id: Optional[str] = Field(default="", description="轮次id")
    type: Optional[str] = Field(default="", description="类型")

class GetTestInfoRequest(BaseModel):
    project_id: Optional[str] = Field(default="", description="项目id")
    turn_id: Optional[str] = Field(default="", description="轮次id")
    plan_id: Optional[str] = Field(default="", description="方案id")
    # type: Optional[str] = Field(default="", description="类型")