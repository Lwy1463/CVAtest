import threading
import yaml
import os


class DeviceConfig:
    def __init__(self) -> None:
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)
        self.yaml = os.path.join(current_dir, "device_config.yaml")
        self.camera_interval = "camera_interval"
        self.camera_times = "camera_times"
        self.camera_start_wait = "camera_start_wait"
        # llm result photo config
        self.result_photo_interval = "result_photo_interval"
        self.result_photo_diff_rate = "result_photo_diff_rate"
        self.result_start_wait = "result_start_wait"
        # Camera Resolution
        self.video_width = "video_width"
        self.video_height = "video_height"
        self.video_frame_rate = "video_frame_rate"
        self.lock = threading.Lock()

        if os.path.exists(self.yaml):
            self.device_map = self.read_yaml_file()
        else:
            self.device_map = {
                "camera_interval": 0.5,
                "camera_start_wait": 1.0,
                "camera_times": 8,
                "result_photo_diff_rate": 0.1,
                "result_photo_interval": 0.75,
                "result_start_wait": 0,
                "video_height": 1080,
                "video_width": 1920,
                "video_frame_rate": 30,
            }
            self.write_yaml_file(self.device_map)


    def read_yaml_file(self):
        with open(self.yaml, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)  # 使用 safe_load 更安全
        return data

    def write_yaml_file(self, device):
        with open(self.yaml, "w", encoding="utf-8") as file:
            yaml.dump(device, file, allow_unicode=True)
        return

    def set(self, key, value):
        self.lock.acquire()
        self.device_map[key] = value
        self.write_yaml_file(self.device_map)
        self.lock.release()

    def set_all(self):
        self.lock.acquire()
        self.write_yaml_file(self.device_map)
        self.lock.release()

    def get(self, key):
        self.lock.acquire()
        value = self.device_map.get(key, "")
        self.lock.release()
        return value

    def set_ocr_config(self, start_wait:float =None, interval:int = None, times:float = None):
        self.lock.acquire()
        if start_wait:
            self.device_map[self.camera_start_wait] = start_wait
        if interval:
            self.device_map[self.camera_interval] = interval
        if times:
            self.device_map[self.camera_times] = times
        self.write_yaml_file(self.device_map)
        self.lock.release()

    def get_ocr_config(self):
        self.lock.acquire()
        camera_interval = self.device_map[self.camera_interval]
        camera_times = self.device_map[self.camera_times]
        camera_start_wait = self.device_map[self.camera_start_wait]
        self.lock.release()
        return camera_start_wait, camera_interval, camera_times

    def get_result_photo_config(self):
        self.lock.acquire()
        result_photo_interval = self.device_map[self.result_photo_interval]
        result_start_wait = self.device_map[self.result_start_wait]
        result_photo_diff_rate = self.device_map[self.result_photo_diff_rate]
        self.lock.release()
        return result_start_wait, result_photo_interval, result_photo_diff_rate

    def get_video_config(self):
        self.lock.acquire()
        video_width = self.device_map[self.video_width]
        video_height = self.device_map[self.video_height]
        video_frame_rate = self.device_map[self.video_frame_rate]
        self.lock.release()
        return video_frame_rate, video_width, video_height


deviceConfig = DeviceConfig()
print("deviceConfig, ", deviceConfig.device_map)
