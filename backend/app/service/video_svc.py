import time
import cv2
from threading import Thread
from app.middleware.log import logger as log
from app.config.device_config import deviceConfig


fourcc = cv2.VideoWriter_fourcc(*'avc1')

# 单例模式 同时只要能存在一个实例
class Video:
    _instance = None
    video_index = 1
    close_flag = True
    width = 1920
    height = 1080
    cap = None
    frame_rate = 30.0


    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Video, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.init_cap()

    def init_cap(self):
        self.frame_rate, self.width, self.height = deviceConfig.get_video_config()
        self.cap = cv2.VideoCapture(self.video_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.frame_rate)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def record(self, video_path, out):
        start_time = time.time()
        log.info(f"video start. video path: {video_path}")
        zindex = 0
        while self.close_flag:
            ret, frame = self.cap.read()
            if not ret:
                self.cap.release()
                break
            if zindex == 0:
                zindex += 1
                continue
            # 写入视频文件
            out.write(frame)
            zindex += 1
        # self.cap.release()
        out.release()
        end_time = time.time()
        log.info(f"record is closed. 耗时{round(end_time-start_time, 2)}s zindex:{zindex}")
        return

    def start(self, video_path):
        frame_rate, width, height = deviceConfig.get_video_config()
        if self.cap.isOpened():
            for i in range(3):
                ret, frame = self.cap.read()
                if not ret:
                    self.init_cap()
                    log.info("restart camera. error shutdown")
                    break
        else:
            self.init_cap()
            log.info("restart camera. is not open")

        if "." not in video_path:
            video_path = video_path + ".mp4"

        self.close_flag = True
        if self.width != width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.width = width
        if self.height != height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.width)
            self.height = height
        if self.frame_rate != frame_rate:
            self.cap.set(cv2.CAP_PROP_FPS, self.width)
            self.frame_rate = frame_rate
        out = cv2.VideoWriter(video_path, fourcc, self.frame_rate, (self.width, self.height))
        process = Thread(target=self.record, args=(video_path, out), daemon=True)
        process.start()

    def close(self):
        self.close_flag = False

video = Video()
