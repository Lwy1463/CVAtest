from typing import Optional
from pydantic import BaseModel, Field

class PlayConfigCreateRequest(BaseModel):
    config_name: Optional[str] = Field(..., description="播放配置名字")
    description: Optional[str] = Field(default="", description="播放配置描述")
    type: Optional[str] = Field(..., description="播放配置类型")

class PlayConfigUpdateRequest(BaseModel):
    play_config_id: Optional[str] = Field(..., description="播放配置id")
    config_name: Optional[str] = Field(default="", description="播放配置名字")
    description: Optional[str] = Field(default="", description="播放配置描述")
    type: Optional[str] = Field(default="", description="播放配置类型")
    configs: Optional[list] = Field(default=[], description="播放配置配置列表")

class PlayConfigDeleteRequest(BaseModel):
    play_config_id: Optional[str] = Field(..., description="播放配置id")

