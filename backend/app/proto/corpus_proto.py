from typing import Optional
from pydantic import BaseModel, Field

class TestCorpusCreateRequest(BaseModel):
    text: Optional[str] = Field(..., description="语料文本")
    test_type: Optional[str] = Field(default="", description="测试类型")
    test_scenario: Optional[str] = Field(default="", description="测试场景")
    speaker: Optional[str] = Field(default="", description="发声人")
    language: Optional[str] = Field(default="", description="语种")
    car_function: Optional[str] = Field(default="", description="对应车机功能")
    label: Optional[str] = Field(default="", description="标签")
    expect_result: Optional[str] = Field(default="", description="预期结果")

class TestCorpusUpdateRequest(BaseModel):
    corpus_id: Optional[str] = Field(..., description="语料ID")
    text: Optional[str] = Field(..., description="语料文本")
    test_type: Optional[str] = Field(default="", description="测试类型")
    test_scenario: Optional[str] = Field(default="", description="测试场景")
    speaker: Optional[str] = Field(default="", description="发声人")
    language: Optional[str] = Field(default="", description="语种")
    car_function: Optional[str] = Field(default="", description="对应车机功能")
    label: Optional[str] = Field(default="", description="标签")
    expect_result: Optional[str] = Field(default="", description="预期结果")

class CorpusDeleteRequest(BaseModel):
    corpus_id: Optional[str] = Field(..., description="语料ID")

class CorpusBatchDeleteRequest(BaseModel):
    corpus_ids: Optional[list] = Field(default=[], description="语料ID列表")

class TestCorpusUploadRequest(BaseModel):
    corpus_id: Optional[str] = Field(..., description="语料ID")
    aud_id: Optional[str] = Field(..., description="音频ID")
    audio_url: Optional[str] = Field(..., description="语料路径")
    pinyin: Optional[str] = Field(..., description="拼音")
    audio_duration: Optional[str] = Field(..., description="音频长度")
    text: Optional[str] = Field(..., description="语料文本")

class CorpusSynthesize(BaseModel):
    corpus_ids: Optional[list] = Field(default=[], description="语料ID列表")
    label: Optional[str] = Field(default="", description="标签")
    is_tone: Optional[bool] = Field(default=False, description="是否添加语气词")

class RouseCorpusCreateRequest(BaseModel):
    text: Optional[str] = Field(..., description="语料文本")
    test_scenario: Optional[str] = Field(default="", description="测试场景")
    speaker: Optional[str] = Field(default="", description="发声人")
    language: Optional[str] = Field(default="", description="语种")
    label: Optional[str] = Field(default="", description="标签")

class RouseCorpusUpdateRequest(BaseModel):
    corpus_id: Optional[str] = Field(..., description="语料ID")
    text: Optional[str] = Field(..., description="语料文本")
    test_scenario: Optional[str] = Field(default="", description="测试场景")
    speaker: Optional[str] = Field(default="", description="发声人")
    language: Optional[str] = Field(default="", description="语种")
    label: Optional[str] = Field(default="", description="标签")

class RouseCorpusBatchDeleteRequest(BaseModel):
    corpus_ids: Optional[list] = Field(default=[], description="语料ID列表")