import uvicorn
import threading
from fastapi import FastAPI

from app import bootstrap
from app.config import globalAppSettings

if __name__ == "__main__":
    print("项目配置:", globalAppSettings)
    # 实例化
    server = FastAPI(redoc_url=None, docs_url="/apidoc", title=globalAppSettings.app_name)
    # 初始化项目
    bootstrap.init(server)
    # 使用 python main.py 启动服务
    uvicorn.run(server, host=globalAppSettings.app_host, port=globalAppSettings.app_port)
