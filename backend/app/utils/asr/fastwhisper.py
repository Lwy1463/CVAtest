import os
import time
import site
import re
from .base import BaseASR
from app.middleware.log import logger as log

os.environ['KMP_DUPLICATE_LIB_OK']='True'

from faster_whisper import WhisperModel


class FasterWhisperASR(BaseASR):
    model_size = "large-v3"
    cublas_path = ""
    cudnn_path = ""
    initial_prompt = "音频为车机响应,不要胡乱输出和发散,有合适的标点符号."


    def __init__(self, gpu=False):
        if len(site.getsitepackages()) > 1 and gpu:
            site_path = site.getsitepackages()[1]
            self.cublas_path = os.path.join(site_path, r"nvidia\cublas\bin")
            self.cudnn_path = os.path.join(site_path, r"nvidia\cudnn\bin")
            env_path = os.environ["PATH"]
            if self.cublas_path not in env_path or self.cudnn_path not in env_path:
                os.environ["PATH"] = f"{self.cublas_path};{self.cudnn_path};{env_path}"
        # Run on GPU with FP16
        if gpu:
            self.model = WhisperModel(self.model_size, device="cuda", compute_type="float16")
        else:
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        log.info(f"FasterWhisperASR model load. use_gpu={gpu}")
        return

    def identify(self, audio_path) -> str:
        start_time = time.time()
        vad_param = {
            "threshold": 0.2,
            "min_speech_duration_ms": 200,
            "max_speech_duration_s": float("inf"),
            "min_silence_duration_ms": 1000,
            "speech_pad_ms": 400,
        }
        segments, info = self.model.transcribe(audio_path, beam_size=5, language="zh",
                                               initial_prompt=self.initial_prompt, vad_filter=True,
                                               vad_parameters=vad_param)
        text = ""
        for segment in segments:
            text += segment.text
        # 特殊处理 请不吝点赞..情况
        text = re.sub(r"请不吝点赞.*", "", text)
        log.info(f"Recognition: {time.time() - start_time} s, text: {text}")
        return text

    def identify_rouse(self, audio_path) -> str:
        start_time = time.time()
        segments, info = self.model.transcribe(audio_path, beam_size=5, language="zh")
        text = ""
        for segment in segments:
            text += segment.text
        log.info(f"Recognition: {time.time() - start_time} s, text: {text}")
        return text
