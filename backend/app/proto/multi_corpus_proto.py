from typing import Optional
from pydantic import BaseModel, Field

class MultiCorpusCreateRequest(BaseModel):
    corpus_name: Optional[str] = Field(default="", description="语料名字")
    test_type: Optional[str] = Field(default="", description="测试类型")
    test_scenario: Optional[str] = Field(default="", description="测试场景")
    speaker: Optional[str] = Field(default="", description="发声人")
    language: Optional[str] = Field(default="", description="语种")
    car_function: Optional[str] = Field(default="", description="对应车机功能")
    label: Optional[str] = Field(default="", description="标签")
    corpusItems: Optional[list] = Field(default=[], description="音频列表")

class MultiCorpusUpdateRequest(BaseModel):
    corpus_name: Optional[str] = Field(default="", description="语料名字")
    corpus_id: Optional[str] = Field(..., description="语料ID")
    test_type: Optional[str] = Field(default="", description="测试类型")
    test_scenario: Optional[str] = Field(default="", description="测试场景")
    speaker: Optional[str] = Field(default="", description="发声人")
    language: Optional[str] = Field(default="", description="语种")
    car_function: Optional[str] = Field(default="", description="对应车机功能")
    label: Optional[str] = Field(default="", description="标签")
    corpusItems: Optional[list] = Field(default=[], description="音频列表")

class CorpusDeleteRequest(BaseModel):
    corpus_id: Optional[str] = Field(..., description="语料ID")

class CorpusBatchDeleteRequest(BaseModel):
    corpus_ids: Optional[list] = Field(default=[], description="语料ID列表")
