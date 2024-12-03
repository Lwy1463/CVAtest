from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import uuid
import logging

# 创建Logger对象
import os


request_id_context: ContextVar[str] = ContextVar("request_id", default="")

# 配置日志格式，添加请求 ID
class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_context.get("no-request-id")
        return True


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 生成64位请求 ID
        request_id = str(uuid.uuid4())
        request_id_context.set(request_id)

        # 打印请求 ID 到日志
        # logger.info(f"url: {request.url} request ID: {request_id}")

        # 执行请求
        response = await call_next(request)

        # 在响应头中加入请求 ID（可选）
        response.headers["X-Request-ID"] = request_id
        return response


logger = logging.getLogger(__name__)
# 设置标准日志等级
logger.setLevel(logging.INFO)

# 如果不存在定义的日志目录就创建一个
logfile_dir = "./logs"
logfile_name = "app.log"
if not os.path.isdir(logfile_dir):
    os.mkdir(logfile_dir)

# 创建FileHandler对象，将日志写入文件
logfile_path = os.path.join(logfile_dir, logfile_name)
file_handler = logging.FileHandler(logfile_path, mode='a', encoding='utf-8')
# 设置文件中写入的日志等级
file_handler.setLevel(logging.DEBUG)

# 创建StreamHandler对象，将日志输出到控制台
stream_handler = logging.StreamHandler()
# 设置控制台显示的日志等级
stream_handler.setLevel(logging.INFO)

# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - [%(request_id)s] - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addFilter(RequestIdFilter())
# 将处理器添加到Logger对象中（注册）
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
