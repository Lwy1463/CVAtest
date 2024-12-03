from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from app.controller import RegisterRouterList
from app.dao.base_dao import init_db
from app.middleware.log import RequestIdMiddleware
from app.service.llm_judge import llm_judge_result
import threading


def init(server: FastAPI):
    # 挂载静态资源目录
    server.mount("/static", StaticFiles(directory="video"), name="static")
    server.mount("/mic_static", StaticFiles(directory="mic_audio"), name="mic_static")
    server.mount("/audio", StaticFiles(directory="audio"), name="audio")
    server.mount("/photo", StaticFiles(directory="photo"), name="photo")

    # 注册自定义错误处理器
    # errors.registerCustomErrorHandle(server)
    # 注册中间件
    # middleware.registerMiddlewareHandle(server)
    server.add_middleware(RequestIdMiddleware)
    # 初始化数据库
    init_db()

    # 创建并启动 大模型判断线程
    func1_thread = threading.Thread(target=llm_judge_result, daemon=True)
    func1_thread.start()

    # 加载路由
    for item in RegisterRouterList:
        server.include_router(item.router)