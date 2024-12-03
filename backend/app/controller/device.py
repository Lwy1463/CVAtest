from fastapi import APIRouter
from app.config.device_config import deviceConfig
from app.proto.device_proto import DeviceConfigResponse


router = APIRouter(prefix="/device")

@router.post("/config_set")
async def config_set(req: DeviceConfigResponse):
    if req.camera_times is not None:
        deviceConfig.device_map["camera_times"] = req.camera_times
    if req.camera_interval is not None:
        deviceConfig.device_map["camera_interval"] = req.camera_interval
    if req.camera_start_wait is not None:
        deviceConfig.device_map["camera_start_wait"] = req.camera_start_wait
    if req.result_photo_interval is not None:
        deviceConfig.device_map["result_photo_interval"] = req.result_photo_interval
    if req.result_start_wait is not None:
        deviceConfig.device_map["result_start_wait"] = req.result_start_wait
    if req.result_photo_diff_rate is not None:
        deviceConfig.device_map["result_photo_diff_rate"] = req.result_photo_diff_rate
    if req.video_width is not None:
        deviceConfig.device_map["video_width"] = req.video_width
    if req.video_height is not None:
        deviceConfig.device_map["video_height"] = req.video_height
    if req.video_frame_rate is not None:
        deviceConfig.device_map["video_frame_rate"] = req.video_frame_rate
    deviceConfig.set_all()
    return {"status": "success"}


@router.post("/config_get")
async def config_get():
    res = DeviceConfigResponse()
    res.camera_times = deviceConfig.device_map["camera_times"]
    res.camera_interval = deviceConfig.device_map["camera_interval"]
    res.camera_start_wait = deviceConfig.device_map["camera_start_wait"]
    res.result_photo_interval = deviceConfig.device_map["result_photo_interval"]
    res.result_start_wait = deviceConfig.device_map["result_start_wait"]
    res.result_photo_diff_rate = deviceConfig.device_map["result_photo_diff_rate"]
    res.video_width = deviceConfig.device_map["video_width"]
    res.video_height = deviceConfig.device_map["video_height"]
    res.video_frame_rate = deviceConfig.device_map["video_frame_rate"]
    return res