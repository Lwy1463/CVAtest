import os.path

from .base import BaseTTS
import dashscope
from dashscope.audio.tts_v2 import *
from app.config import globalAppSettings
from app.middleware.log import logger as log
from app.constant import Vocalists


class AlTTS(BaseTTS):
    speaker = "longxiaocheng"
    language = "mandarin"
    model = "cosyvoice-v1"
    path = globalAppSettings.audio_path
    dashscope.api_key = "sk-19e8955ee9ff4e08b58e2f337f06e6a6"
    # key = Vocalists-Language
    voice_map = {
        "1-1": "longshu",
        "2-1": "longxiaoxia",
    }
    female_voice_map = {
        1: "longxiaochun", #柔滑温暖
        2: "longxiaoxia",  #温润磁性
        3: "longxiaobai",  #轻松亲和
        4: "longjing",     #庄重俨然
        5: "longmiao",     #清澈透亮
        6: "longyue",      #抑扬顿挫
        7: "longyuan",     #细腻丰富
        8: "longtong",     #童声
    }

    male_voice_map = {
        1: "longxiaocheng", #深邃稳重
        2: "longlaotie",    #东北腔调
        3: "longshu",       #专业沉稳
        4: "longshuo",      #阳光活力
        5: "longfei",       #冷静睿智
        6: "longxiang",     #稳如老茶
        7: "longjielidou",  #童声
    }

    def convert(self, text, audio_path) -> int:
        return 0

    def convert_with_voice(self, text, voice, language, audio_path, tts_tone=False) -> int:
        speaker = self.speaker
        if voice == Vocalists.male:
            speaker = self.male_voice_map[language]
        if voice == Vocalists.female:
            speaker = self.female_voice_map[language]
        synthesizer = SpeechSynthesizer(model=self.model, voice=speaker, speech_rate=0.9)
        audio = synthesizer.call(text)
        with open(audio_path, 'wb') as f:
            f.write(audio)
        log.info(f"AlTTS convert_with_voice speaker({speaker}), save_path({audio_path}), text: {text}")
        return 0
