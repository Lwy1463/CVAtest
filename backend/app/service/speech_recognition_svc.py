from app.utils.asr.fastwhisper import FasterWhisperASR
from app.middleware.log import logger as log
from app.config import globalAppSettings


class SpeechRecognitionSvc:
    asr = FasterWhisperASR(gpu=globalAppSettings.asr_use_gpu)

    def local_recognize(self, audio_path) -> str:
        text = self.asr.identify(audio_path)
        return text

    def local_recognize_rouse(self, audio_path) -> str:
        text = self.asr.identify_rouse(audio_path)
        return text