from abc import ABC, abstractmethod

class BaseASR(ABC):
    @abstractmethod
    def identify(self, audio_path) -> str:
        raise NotImplementedError("Subclass must implement abstract method")
