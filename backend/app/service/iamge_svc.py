import os.path
import time
import string
import jieba
import Levenshtein
import cv2
import re
import numpy as np
import glob

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.utils.ocr.paddleocr import PadOcr
from app.utils.camera import Camera
from app.middleware.log import logger as log
from app.config.device_config import deviceConfig


def calculate_difference_rate(image1_path, image2_path, threshold=50):
    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)
    # 将图像转换为灰度图
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # 计算图像的绝对差异
    diff = cv2.absdiff(gray1, gray2)

    # 将差异图像进行阈值处理
    _, diff_thresholded = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

    # 计算差异率
    changed_pixels = np.count_nonzero(diff_thresholded)
    total_pixels = diff_thresholded.size
    difference_rate = (changed_pixels / total_pixels) * 100
    return difference_rate


def remove_punctuation_by_re(text):
    # 定义一个正则表达式，匹配所有标点符号
    pattern = r'[\W_]+|[\u3000-\u303F]'
    # 使用re.sub()替换掉标点符号
    return re.sub(pattern, '', text)


# 车机图片相关服务
def calculate_car(reference, hypothesis):
    """
    计算字准确率 (CAR)

    参数:
    - reference: 实际文本
    - hypothesis: 识别文本

    返回:
    - car: 字准确率
    """
    edit_distance = Levenshtein.distance(reference.lower(), hypothesis.lower())

    # 计算 CAR
    car = (len(reference) - edit_distance) / len(reference)
    return round(car, 2)


# 计算两个文本的中文相似度
def calculate_similarity(text1, text2):
    tmp1 = text1.lower()
    tmp2 = text2.lower()
    if not tmp1 or not tmp2:
        return 0.0

    def chinese_tokenizer(text):
        return jieba.lcut(text)

    # 创建 TfidfVectorizer 对象
    vectorizer = TfidfVectorizer(tokenizer=chinese_tokenizer)
    # 将两行文字转换为 TF-IDF 矩阵
    tfidf_matrix = vectorizer.fit_transform([tmp1, tmp2])
    # 计算余弦相似度
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(similarity[0][0], 2)


def get_ocr_wdt_hgt(item):
    # [[1356, 174], [1592, 174], [1592, 222], [1356, 222]], ...
    # there we need 1592 - 1356 and 222 - 174
    return item[0][2][0] - item[0][0][0], item[0][2][1] - item[0][0][1]


def is_sim(initial_text, chinese_text):
    low_sim = 0.3
    real_sim = len(chinese_text) / len(initial_text) - 0.4
    real_sim = max(low_sim, real_sim)
    return calculate_similarity(initial_text, chinese_text) > real_sim


def delete_result_char_confidence(result, pattern, line, idx, i):
    if len(result[0][0][1]) == 3:
        delete_list = []
        for j, char in enumerate(line):
            if not pattern.match(char):
                delete_list.append(j)
        for index in sorted(delete_list, reverse=True):
            del result[idx][i][1][2][index]


class Recognition:
    def __init__(self, source, match, ocr) -> None:
        self.ocr = ocr
        self.source = source
        self.minimum_width = 200
        self.minimum_height = 40
        self.min_quality = 0.8
        self.target_area = None
        self.match = match
        self.result = ''
        self.candidate = ''
        self.char_confidence_map = {}
        self.char_confidence_list = []

    def use_confidence_map(self):
        return len(self.char_confidence_map) != 0

    def select_char(self, diff1, diff2, str1_start, str2_start, map_key):
        diff_str = ""
        min_length = min(len(diff1), len(diff2))
        for idx in range(min_length):
            if diff1[idx] == diff2[idx]:
                diff_str += diff1[idx]
            else:
                if len(self.char_confidence_map) != 0:
                    char1_confidence = self.char_confidence_list[str1_start + idx]
                    char2_confidence = self.char_confidence_map[map_key][str2_start + idx]
                    print(f"char:{diff1[idx]}:{char1_confidence} char2:{diff2[idx]}:{char2_confidence}")
                    if char2_confidence > 0.9 or char2_confidence > char1_confidence:
                        diff_str += diff2[idx]
                        self.char_confidence_list[str1_start + idx] = self.char_confidence_map[map_key][
                            str2_start + idx]
                    else:
                        diff_str += diff1[idx]
                else:
                    diff_str += diff2[idx]
        return diff_str

    def get_diff_str(self, diff1, diff2, str1_start, str2_start, map_key):
        idx = 0
        for i in range(len(diff2) - 2):
            if diff2[:len(diff2) - i] in diff1:
                idx = diff1.find(diff2)
                break
        diff_str = self.select_char(diff1[idx:], diff2, str1_start + idx, str2_start, map_key)
        if len(diff2) > len(diff1) + idx:
            for idx in range(len(diff1) + idx, len(diff2)):
                diff_str += diff2[idx]
                if len(self.char_confidence_map) != 0:
                    self.char_confidence_list.append(self.char_confidence_map[map_key][str2_start + idx])
        return diff_str

    def reconstruct_affix(self, str1, str2, str1_start, str2_start, map_key):
        diff_str = ""
        if len(str1) < 2 or len(str2) < 2:
            return str1 + str2
        if len(str1) == len(str2):
            diff_str = self.select_char(str1, str2, str1_start, str2_start, map_key)
        elif len(str1) > len(str2):
            flag = False
            idx = 0
            for i in range(len(str2) - 2):
                if str2[:len(str2) - i] in str1:
                    idx = str1.find(str2)
                    break
            if not flag:
                idx = len(str1) - len(str2) - 1
            diff_str = self.select_char(str1[idx:], str2, str1_start + idx, str2_start, map_key)
            diff_str = str1[:idx] + diff_str
        elif len(str1) < len(str2):
            flag = False
            idx = 0
            for i in range(len(str1) - 2):
                if str1[:len(str1) - i] in str2:
                    idx = str2.find(str1)
                    break
            if not flag:
                idx = 0
            diff_str = self.select_char(str1, str2[idx:], str1_start, str2_start + idx, map_key)
            diff_str = str2[:idx] + diff_str + str2[idx + len(str1):]
            self.char_confidence_list = self.char_confidence_list[:-len(str1)]
            confidence_list = []
            for i in range(idx):
                confidence_list.append(self.char_confidence_map[map_key][str2_start + i])
            confidence_list += self.char_confidence_list[-len(str1):]
            for i in range(idx + len(str1), len(str2)):
                confidence_list.append(self.char_confidence_map[map_key][str2_start + i])
            self.char_confidence_list = self.char_confidence_list[-len(str1):] + confidence_list
        return diff_str

    def filter_print_ocr(self, result, initial_text):
        initial_text = initial_text.lower()
        for idx in range(len(result)):
            res = result[idx]
            if not res:
                continue
            for i, line in enumerate(res):
                pattern = re.compile(r'[\u4e00-\u9fa5a-zA-Z0-9]')
                chinese_text = "".join(re.findall(pattern, line[1][0]))
                chinese_text = chinese_text.lower()
                if chinese_text == initial_text:
                    self.target_area = int(line[0][0][0]), int(line[0][0][1])
                    delete_result_char_confidence(result, pattern, line[1][0], idx, i)
                    return chinese_text, idx, i
                if self.target_area is None:
                    if is_sim(initial_text, chinese_text):
                        self.target_area = int(line[0][0][0]), int(line[0][0][1])
                        delete_result_char_confidence(result, pattern, line[1][0], idx, i)
                        return chinese_text, idx, i
                    continue
                if is_sim(initial_text, chinese_text):
                    delete_result_char_confidence(result, pattern, line[1][0], idx, i)
                    return chinese_text, idx, i
        return '', 0, 0

    def compare_seq(self, str1, str2, idx):
        m = len(str1)
        n = len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        length = 0
        end_pos1 = 0
        end_pos2 = 0

        if str1 == str2:
            return str1

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i - 1] == str2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                    if dp[i][j] > length:
                        length = dp[i][j]
                        end_pos1 = i - 1
                        end_pos2 = j - 1
                else:
                    dp[i][j] = 0
        if length == 0:
            if len(self.char_confidence_map) != 0:
                self.char_confidence_list += self.char_confidence_map[idx]
            return str1 + str2
        if end_pos2 - length + 1 == 0 and end_pos1 + 1 == m:
            if len(self.char_confidence_map) != 0:
                self.char_confidence_list += self.char_confidence_map[idx][length:]
            return str1 + str2[length:]
        elif end_pos2 - length + 1 > 0 and end_pos1 + 1 == m:
            diff_str2 = str2[0:end_pos2 - length + 1]
            diff_str1_start = m - length - len(diff_str2)
            diff_str1 = str1[diff_str1_start:diff_str1_start + len(diff_str2)]
            diff_str = self.get_diff_str(diff_str1, diff_str2, diff_str1_start, 0, idx)
            if len(self.char_confidence_map) != 0:
                self.char_confidence_list += self.char_confidence_map[idx][len(diff_str):]
            return str1[:diff_str1_start] + diff_str + str2[len(diff_str):]
        elif end_pos2 - length + 1 == 0 and end_pos1 + 1 < m:
            diff_str1 = str1[end_pos1 + 1:]
            diff_str2 = str2[length:length + len(diff_str1)]
            diff_str = self.get_diff_str(diff_str1, diff_str2, end_pos1 + 1, length, idx)
            if len(self.char_confidence_map) != 0:
                self.char_confidence_list += self.char_confidence_map[idx][length + len(diff_str):]
            return str1[:end_pos1 + 1] + diff_str + str2[length + len(diff_str):]

        # 公共字串字串在两个字符串的中间
        common_str = str1[end_pos1 - length + 1:end_pos1 + 1]
        str1_prefix, str1_suffix = str1[0: end_pos1 - length + 1], str1[end_pos1 + 1:]
        str2_prefix, str2_suffix = str2[0: end_pos2 - length + 1], str2[end_pos2 + 1:]
        diff_prefix = self.reconstruct_affix(str1_prefix, str2_prefix, 0, 0, idx)
        diff_suffix = self.reconstruct_affix(str1_suffix, str2_suffix, end_pos1 + 1, end_pos2 + 1, idx)
        self.char_confidence_list += self.char_confidence_map[idx][end_pos2 + 1:]
        return diff_prefix + common_str + diff_suffix

    def run(self):
        ocr_output = []
        for i, image_file in enumerate(self.source):
            if self.target_area is not None:
                img = cv2.imread(image_file)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                cropped_image = gray[self.target_area[1] - 40:self.target_area[1] + 100,
                                self.target_area[0] - 10:self.target_area[0] + 600]
                result = self.ocr.identify(cropped_image)
            else:
                result = self.ocr.identify(image_file)
            ocr_item, idx, idy = self.filter_print_ocr(result, self.match)
            if ocr_item == self.match:
                self.result = ocr_item
                return
            if self.target_area is not None and len(ocr_item) != 0:
                if len(result[0][0][1]) == 3:
                    self.char_confidence_map[len(ocr_output)] = result[idx][idy][1][2]
                ocr_output.append(ocr_item)
        sequence = ''
        for i, current in enumerate(ocr_output):
            if i == 0:
                sequence = current
                if len(self.char_confidence_map) != 0:
                    self.char_confidence_list = self.char_confidence_map[0]
            else:
                sequence = self.compare_seq(sequence, current, i)
        self.result = sequence


class QUBEImageSvc:
    ocr = PadOcr()
    camera = Camera()
    interval = 0.5
    times = 8
    start_wait = 0.5
    take_result_timeout = 30

    def image_recognize(self, image_path) -> list:
        result = self.ocr.identify(image_path)
        text_list = []
        for idx in range(len(result)):
            res = result[idx]
            if not res:
                continue
            for line in res:
                text_list.append(line[1][0])
        return text_list

    # 返回 选择图片路径 识别的文本 识别正确率
    def image_select_by_text(self, path_list, audio_text) -> (str, str, float):
        sorted(path_list, reverse=True)
        audio_text = remove_punctuation_by_re(audio_text)
        max_similarity = 0.0
        max_car = 0.0
        result_path = ""
        result_text = ""
        for i, image_path in enumerate(path_list):
            text_list = self.image_recognize(image_path)
            for text in text_list:
                text = remove_punctuation_by_re(text)
                similarity = calculate_similarity(audio_text, text)
                if int(similarity) == 1 or audio_text in text:
                    car = calculate_car(audio_text, text)
                    return image_path, text, car
                if similarity > max_similarity:
                    max_similarity = similarity
                    result_path = image_path
                    result_text = text
                    max_car = calculate_car(audio_text, text)
        return result_path, result_text, max_car

    def image_select_by_multi_recognition(self, path_list, audio_text) -> (str, str, float):
        if len(path_list) == 0:
            return "", "", 0.0
        glob_path = re.sub(r"-\d+\.jpg$", "-*.jpg", path_list[0])
        source = sorted(glob.glob(glob_path))
        rec = Recognition(source, audio_text, self.ocr)
        rec.run()
        result_text = rec.result
        max_car = calculate_car(audio_text, result_text)
        return path_list[-1], result_text, max_car

    # 从多张采集的图片中选择响应最完善的图片
    def image_select(self, path_list) -> str:
        text_lists = []
        text_length_map = {}
        different_idx = -1
        for image_path in path_list:
            text_list = self.image_recognize(image_path)
            for i, text in enumerate(text_list):
                if not text_length_map.get(i):
                    text_length_map[i] = len(text)
                else:
                    if text_length_map.get(i) != len(text):
                        different_idx = i
                        text_length_map[i] = len(text)
            text_lists.append(text_list)

        if different_idx == -1 or not text_lists:
            return ""
        max_text_list = 0
        max_length = 0
        for i, text_list in enumerate(text_lists):
            if len(text_list[different_idx]) > max_length:
                max_length = len(text_list[different_idx])
                max_text_list = i
        return path_list[max_text_list]

    def photograph(self, image_dir, name):
        ret = self.camera.camera_init()
        if ret:
            log.warn("QUBEImageSvc camera_init fail")
            return
        image_name = self.camera.take_photo(image_dir, name)
        self.camera.camera_close()
        return image_name

    # 一段时间内多次采集图片，保存多张
    # 参数 保存图像目录, 图像名字, 音频时间单位为秒
    # 在目录下以 name-1, name-2... 名字保存
    async def photograph_plan(self, image_dir, name, audio_length):
        audio_length = float(audio_length)
        start_wait, interval, times = deviceConfig.get_camera()
        ret = self.camera.camera_init()
        if ret:
            log.warn("QUBEImageSvc camera_init fail")
            return
        if audio_length > times * interval:
            time.sleep((audio_length + start_wait) - times * interval)
        else:
            time.sleep(start_wait)
        await self.camera.take_photos(image_dir, name, interval, times)
        self.camera.camera_close()
        return

    def photograph_plan_sync(self, image_dir, name, audio_length):
        audio_length = float(audio_length)
        start_wait, interval, times = deviceConfig.get_ocr_config()
        # log.info(f"{start_wait} , {interval} , {times} photograph_plan_sync")
        ret = self.camera.camera_init()
        if ret:
            log.warn("QUBEImageSvc camera_init fail")
            return
        if audio_length > times * interval:
            time.sleep((audio_length + start_wait) - times * interval)
        else:
            time.sleep(start_wait)
        times = min(times, (audio_length + start_wait) // interval + 1)
        self.camera.take_photos_sync(image_dir, name, interval, int(times))
        self.camera.camera_close()
        return

    def photograph_process(self, image_dir, name, audio_length, result_id):
        self.photograph_plan_sync(image_dir, name, audio_length)
        start_time = time.time()
        index = 2
        path_list = []
        start_wait, interval, diff_rate = deviceConfig.get_result_photo_config()
        if start_wait:
            time.sleep(start_wait)
        while time.time() - start_time < self.take_result_timeout:
            image_name = self.photograph(image_dir, f"{result_id}_{index}")
            if not image_name:
                break
            path_list.append(os.path.join(image_dir, image_name))
            if len(path_list) < 3:
                index += 1
                time.sleep(interval)
                continue
            diff1 = calculate_difference_rate(path_list[-1], path_list[-2])
            diff2 = calculate_difference_rate(path_list[-2], path_list[-3])

            # 检查变化率
            if diff1 < diff_rate and diff2 < diff_rate:
                break
            index += 1
            time.sleep(interval)
        if len(path_list) >= 3:
            for i in range(1, len(path_list) - 1):
                if os.path.exists(path_list[i]):
                    os.remove(path_list[i])
        if len(path_list) <= 1:
            log.info(f"photograph_image index({index}), no result photo")
            return
        basename = os.path.basename(path_list[-1])
        result_name = re.sub(r"_\d+", "_result", basename)
        result_path = os.path.join(os.path.dirname(path_list[-1]), result_name)
        print(f"{path_list =}")
        if os.path.exists(path_list[-1]):
            os.rename(path_list[-1], result_path)
        log.info(f"photograph_image index({index}), result photo:{result_name}")
