from fastapi import APIRouter
from app.config import globalAppSettings
# from app.service.iamge_svc import QUBEImageSvc

router = APIRouter(prefix="/demo")

@router.get("/path/test")
async def pathParamReceive2():
    return {
        "msg": "hello",
    }

# @router.get("/test")
# async def test():
#     file_dir = globalAppSettings.photo_dir
#     file_name = str(time.time())
#     qube = QUBEImageSvc()
#     qube.photograph(file_dir, file_name)
#     return {
#         "msg": "hello",
#     }
#
# @router.get("/test2")
# async def test():
#     file_dir = globalAppSettings.photo_dir
#     characters = string.ascii_letters + string.digits
#     file_name = ''.join(random.choices(characters, k=6))
#     qube = QUBEImageSvc()
#     await qube.photograph_plan(file_dir, file_name, 3)
#     return {
#         "msg": "hello",
#     }
