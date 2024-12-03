from abc import ABC, abstractmethod

class BaseOcr(ABC):
    @abstractmethod
    def identify(self, img_path):
        raise NotImplementedError("Subclass must implement abstract method")

def ocr_identify(ocr: BaseOcr, img_path):
    return ocr.identify(img_path)
