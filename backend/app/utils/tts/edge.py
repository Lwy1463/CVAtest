import os.path

from .base import BaseTTS
import subprocess
from app.config import globalAppSettings
from app.middleware.log import logger as log


class EdgeTTS(BaseTTS):
    speaker = "male"
    language = "mandarin"
    command = "edge-tts"
    path = globalAppSettings.audio_path
    list_voice = [
        "zh-CN-XiaoxiaoNeural",
        "zh-CN-XiaoyiNeural",
        "zh-CN-YunjianNeural",
        "zh-CN-YunxiNeural",
        "zh-CN-YunxiaNeural",
        "zh-CN-YunyangNeural",
        "zh-CN-liaoning-XiaobeiNeural",
        "zh-CN-shaanxi-XiaoniNeural",
        "zh-HK-HiuGaaiNeural",
        "zh-HK-HiuMaanNeural",
        "zh-HK-HiuGaaiNeural l",
        "zh-TW-HsiaoChenNeural",
        "zh-TW-HsiaoYuNeural",
        "zh-TW-YunJheNeural"
    ]

    # key = Vocalists-Language
    voice_map = {
        "1-1": "zh-CN-YunjianNeural",
        "2-1": "zh-CN-XiaoxiaoNeural",
        "2-4": "zh-CN-liaoning-XiaobeiNeural",
        "1-2": "zh-HK-WanLungNeural",
        "2-2": "zh-HK-HiuGaaiNeural",
        "2-5": "zh-CN-shaanxi-XiaoniNeural",
        "2-3": "zh-TW-HsiaoChenNeural",
        "1-3": "zh-TW-YunJheNeural",
    }

    def convert(self, text, audio_path) -> int:
        return 0
    
    def convert_with_voice(self, text, voice, language, audio_path, tts_tone=False) -> int:
        speaker = self.voice_map.get("{}-{}".format(voice, language))
        if not speaker:
            log.warn("not speaker")
            return 1
        command = "%s --voice %s --text %s --write-media %s" % (
            self.command, speaker, text, audio_path
        )
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode:
            log.warn(f"cmd: {command}. error: {result.stderr}")
        log.info(f"EdgeTTS convert_with_voice speaker({speaker}), save_path({audio_path})")
        return result.returncode
    