from .base import BaseOcr
from paddleocr import PaddleOCR, draw_ocr


class PadOcr(BaseOcr):
    languages = "ch"
    ocr = PaddleOCR(use_angle_cls=True, lang=languages, use_dilation=True)

    def identify(self, img_path):
        result = self.ocr.ocr(img_path)
        return result
