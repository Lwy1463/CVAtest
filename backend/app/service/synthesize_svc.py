import os.path
from typing import Tuple
from app.config import globalAppSettings
from app.constant import Vocalists
from app.middleware.log import logger as log
from app.utils.tts.al_dashscope import AlTTS
from app.utils.tts.chattts import Chattts
from app.utils.tts.dialects_tts import DialectsTTS
from app.constant import SynthesizeType


class SynthesizeSvc:
    synthesize_corpus_path = globalAppSettings.synthesize_corpus_path
    rouse_corpus_path = globalAppSettings.rouse_corpus_path
    # tts = AlTTS()
    chat_tts = Chattts()
    dialects_tts = DialectsTTS()


    def judge(self, voice, language):
        if voice == Vocalists.female and language >= 8:
            return self.dialects_tts
        if voice == Vocalists.male and language >= 7:
            return self.dialects_tts
        return self.chat_tts


    def synthesize(self, text, name, voice, language, synthesize_type, tts_tone=False) -> Tuple[int, str]:
        if '.' not in name:
            name = name + ".mp3"
        if synthesize_type == SynthesizeType.rouse:
            audio_path = os.path.join(self.rouse_corpus_path, name)
        else:
            audio_path = os.path.join(self.synthesize_corpus_path, name)
        if os.path.exists(audio_path):
            log.warn("synthesize fail. name is exist")
            return 1, ""
        tts = self.judge(voice, language)
        ret = tts.convert_with_voice(text, voice, language, audio_path, tts_tone)
        if ret != 0:
            log.warn("synthesize fail, ret={}".format(ret))
        return ret, audio_path
