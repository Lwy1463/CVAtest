from abc import ABC, abstractmethod

class BaseTTS(ABC):
    @abstractmethod
    def convert(self, text, audio_path) -> int:
        raise NotImplementedError("Subclass must implement abstract method")
    
    @abstractmethod
    def convert_with_voice(self, text, voice, language, audio_path, tts_tone=False) -> int:
        raise NotImplementedError("Subclass must implement abstract method")
    