import os
import shutil
from pathlib import Path
from pprint import pprint
import time
import zipfile
from io import BytesIO
import requests
from .base import BaseTTS
from app.config import globalAppSettings
from app.middleware.log import logger as log
from app.constant import Vocalists


class Chattts(BaseTTS):
    speaker = 2218
    url = "http://183.66.251.10:20000/generate_voice"
    skip_refine_text = True
    refine_text_only = True
    suffix = "[lbreak]"
    tmp_dir = os.path.join(globalAppSettings.synthesize_corpus_path, "tmp")
    # 男: 1996,1509,2211,2418,848,1882；女: 2218,1742,1903,1814,2476
    female_voice_map = {
        1: 2218,
        2: 1742,
        3: 1903,
        4: 1814,
        5: 2476,
        6: 181,
        7: 2000,
    }

    male_voice_map = {
        1: 1996,
        2: 1509,
        3: 2211,
        4: 2418,
        5: 848,
        6: 1882,
    }

    def convert(self, text, audio_path) -> int:
        return 0

    def convert_with_voice(self, text, voice, language, audio_path, tts_tone=True) -> int:
        speaker = self.speaker
        text += self.suffix
        if voice == Vocalists.male:
            speaker = self.male_voice_map[language]
        if voice == Vocalists.female:
            speaker = self.female_voice_map[language]
        body = {
            "text": [
                text,
            ],
            "stream": False,
            "lang": None,
            "skip_refine_text": self.skip_refine_text,
            "refine_text_only": self.refine_text_only,
            "use_decoder": True,
            "audio_seed": 2836122105,
            "text_seed": 42,
            "do_text_normalization": True,
            "do_homophone_replacement": False,
            "params_refine_text": {
                "prompt": "[oral_3][laugh_0][break_6]",
                "top_P": 0.7,
                "top_K": 20,
                "temperature": 0.7,
                "repetition_penalty": 1,
                "max_new_token": 384,
                "min_new_token": 0,
                "show_tqdm": True,
                "ensure_non_empty": True,
                "stream_batch": 24,
            },
            "params_infer_code": {
                "prompt": "[speed_1]",
                "top_P": 0.7,
                "top_K": 20,
                "temperature": 0.7,
                "repetition_penalty": 1.05,
                "max_new_token": 2048,
                "min_new_token": 0,
                "show_tqdm": True,
                "ensure_non_empty": True,
                "stream_batch": True,
                "spk_emb": None,
                "manual_seed": speaker,
            },
        }
        if not tts_tone:
            body["params_refine_text"]["prompt"] = "[oral_0][laugh_0][break_6]"
        response = requests.post(self.url, json=body, stream=True)
        response.raise_for_status()
        output_dir = self.save_response_content(response.content)
        src_path = os.path.join(output_dir, "0.mp3")
        shutil.move(src_path, audio_path)
        shutil.rmtree(output_dir)
        log.info(f"Chattts convert_with_voice speaker({speaker}), save_path({audio_path}), text: {text}")
        return 0

    def save_response_content(self, response_content):
        """Save the extracted response to a timestamped folder"""
        output_dir = os.path.join(self.tmp_dir, f"{int(time.time())}")
        os.makedirs(output_dir, exist_ok=True)

        with zipfile.ZipFile(BytesIO(response_content), "r") as zip_ref:
            zip_ref.extractall(output_dir)
        return output_dir
