from typing import Optional
from pydantic import BaseModel, Field


class DeviceConfigResponse(BaseModel):
    # ocr config
    camera_interval: Optional[float] = Field(None, description="ocr抓拍间隔", gt=0)
    camera_times: Optional[int] = Field(None, description="ocr抓拍次数", gt=0)
    camera_start_wait: Optional[float] = Field(None, description="ocr抓拍等待时间", ge=0)
    # llm result photo config
    result_photo_interval: Optional[float] = Field(None, description="结果图片抓拍间隔", gt=0)
    result_photo_diff_rate: Optional[float] = Field(None, description="结果图片变化率", gt=0, le=1)
    result_start_wait: Optional[float] = Field(None, description="结果图片抓拍等待时间", ge=0)
    # Camera Resolution
    video_width: Optional[int] = Field(None, description="分辨率宽度", gt=0)
    video_height: Optional[int] = Field(None, description="分辨率高度", gt=0)
    video_frame_rate: Optional[float] = Field(None, description="帧率", gt=0)
