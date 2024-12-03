from typing import Optional
from pydantic import BaseModel, Field


class SynthesizeListRequest(BaseModel):
    audio_name: Optional[str] = Field(None, description="音频文件名")
    audio_url: Optional[str] = Field(None, description="音频文件的URL")


class SynthesizeListResponse(BaseModel):
    audio_name: Optional[str] = Field(default="", description="音频文件名")
    audio_url: Optional[str] = Field(default="", description="音频文件的URL")


class SynthesizeProcessRequest(BaseModel):
    name: Optional[str] = Field(..., description="名字")
    type: Optional[int] = Field(default=1, description="类型") # 1是交互，2是唤醒
    text: Optional[str] = Field(default="", description="语料文本")
    voice: Optional[int] = Field(default=1, description="发声人")
    language: Optional[int] = Field(default=1, description="语种")
    label: Optional[str] = Field(default="tts", description="标签")
    expect_result: Optional[str] = Field(default="", description="预期结果")
    is_tone: Optional[bool] = Field(default=False, description="是否添加语气词")

class BatchSynthesizeProcessRequest(BaseModel):
    list: Optional[list[SynthesizeProcessRequest]]


class CorpusGeneralizate(BaseModel):
    text: Optional[str] = Field(default="", description="语料文本")
