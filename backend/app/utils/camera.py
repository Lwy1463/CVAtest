import time
import asyncio
import os
import app.utils.gxipy as gx
from PIL import Image
from app.utils.gxipy.ImageFormatConvert import *
from app.middleware.log import logger as log

INIT_SUCCESS = 0
INIT_FAIL = 1


def get_best_valid_bits(pixel_format):
    valid_bits = DxValidBit.BIT0_7
    if pixel_format in (GxPixelFormatEntry.MONO8, GxPixelFormatEntry.BAYER_GR8, GxPixelFormatEntry.BAYER_RG8,
                        GxPixelFormatEntry.BAYER_GB8, GxPixelFormatEntry.BAYER_BG8
                        , GxPixelFormatEntry.RGB8, GxPixelFormatEntry.BGR8, GxPixelFormatEntry.R8,
                        GxPixelFormatEntry.B8, GxPixelFormatEntry.G8):
        valid_bits = DxValidBit.BIT0_7
    elif pixel_format in (
    GxPixelFormatEntry.MONO10, GxPixelFormatEntry.MONO10_PACKED, GxPixelFormatEntry.BAYER_GR10,
    GxPixelFormatEntry.BAYER_RG10, GxPixelFormatEntry.BAYER_GB10, GxPixelFormatEntry.BAYER_BG10):
        valid_bits = DxValidBit.BIT2_9
    elif pixel_format in (
    GxPixelFormatEntry.MONO12, GxPixelFormatEntry.MONO12_PACKED, GxPixelFormatEntry.BAYER_GR12,
    GxPixelFormatEntry.BAYER_RG12, GxPixelFormatEntry.BAYER_GB12, GxPixelFormatEntry.BAYER_BG12):
        valid_bits = DxValidBit.BIT4_11
    elif pixel_format in (GxPixelFormatEntry.MONO14):
        valid_bits = DxValidBit.BIT6_13
    elif pixel_format in (GxPixelFormatEntry.MONO16):
        valid_bits = DxValidBit.BIT8_15
    return valid_bits


class Camera:
    def __init__(self):
        self.device_manager = None
        self.image_convert = None
        self.image_process = None
        self.image_process_config = None
        self.cam = None
        return

    def camera_init(self) -> int:
        # 设备已经打开，无需重复初始化，直接返回
        if self.device_manager and self.cam:
            return INIT_SUCCESS

        self.device_manager = gx.DeviceManager()
        dev_num, dev_info_list = self.device_manager.update_all_device_list()
        
        if dev_num is 0:
            print("Number of enumerated devices is 0")
            return INIT_FAIL


        self.cam = self.device_manager.open_device_by_index(1)
        remote_device_feature = self.cam.get_remote_device_feature_control()

        # get image convert obj
        self.image_convert = self.device_manager.create_image_format_convert()

        # get image improvement obj
        self.image_process = self.device_manager.create_image_process()
        self.image_process_config = self.cam.create_image_process_config()
        self.image_process_config.enable_color_correction(False)
        # exit when the camera is a mono camera
        pixel_format_value, pixel_format_str = remote_device_feature.get_enum_feature("PixelFormat").get()
        if Utility.is_gray(pixel_format_value):
            log.error("This sample does not support mono camera.")
            self.cam.close_device()
            return INIT_FAIL

        # set continuous acquisition
        trigger_mode_feature = remote_device_feature.get_enum_feature("TriggerMode")
        trigger_mode_feature.set("Off")

        # get param of improving image quality
        if remote_device_feature.is_readable("GammaParam"):
            gamma_value = remote_device_feature.get_float_feature("GammaParam").get()
            self.image_process_config.set_gamma_param(gamma_value)
        else:
            self.image_process_config.set_gamma_param(1)
        if remote_device_feature.is_readable("ContrastParam"):
            contrast_value = remote_device_feature.get_int_feature("ContrastParam").get()
            self.image_process_config.set_contrast_param(contrast_value)
        else:
            self.image_process_config.set_contrast_param(0)
        return INIT_SUCCESS

    def camera_close(self):
        # close device
        self.cam.close_device()
        self.cam = None
        self.device_manager = None
        return

    def convert_to_rgb(self, raw_image):
        self.image_convert.set_dest_format(GxPixelFormatEntry.RGB8)
        valid_bits = get_best_valid_bits(raw_image.get_pixel_format())
        self.image_convert.set_valid_bits(valid_bits)

        # create out put image buffer
        buffer_out_size = self.image_convert.get_buffer_size_for_conversion(raw_image)
        output_image_array = (c_ubyte * buffer_out_size)()
        output_image = addressof(output_image_array)

        # convert to rgb
        self.image_convert.convert(raw_image, output_image, buffer_out_size, False)
        if output_image is None:
            log.error('Failed to convert RawImage to RGBImage')
            return

        return output_image_array, buffer_out_size

    def gather(self):
        # acquisition image: num is the image number
        # get raw image
        raw_image = self.cam.data_stream[0].get_image()
        if raw_image is None:
            log.error("Getting image failed.")
            return

        # get RGB image from raw image
        image_buf = None
        if raw_image.get_pixel_format() != GxPixelFormatEntry.RGB8:
            rgb_image_array, rgb_image_buffer_length = self.convert_to_rgb(raw_image)
            if rgb_image_array is None:
                return
            # create numpy array with data from rgb image
            numpy_image = numpy.frombuffer(rgb_image_array, dtype=numpy.ubyte, count=rgb_image_buffer_length). \
                reshape(raw_image.frame_data.height, raw_image.frame_data.width, 3)
            image_buf = addressof(rgb_image_array)
        else:
            numpy_image = raw_image.get_numpy_array()
            image_buf = raw_image.frame_data.image_buf

        # 图像质量提升
        rgb_image = GxImageInfo()
        rgb_image.image_width = raw_image.frame_data.width
        rgb_image.image_height = raw_image.frame_data.height
        rgb_image.image_buf = image_buf
        rgb_image.image_pixel_format = GxPixelFormatEntry.RGB8

        # improve image quality
        self.image_process.image_improvement(rgb_image, image_buf, self.image_process_config)

        if numpy_image is None:
            log.error("numpy_image is None.")
            return
        # show acquired image
        return numpy_image, raw_image

    def take_photo(self, save_path, photo_name):
        self.cam.stream_on()

        numpy_image, raw_image = self.gather()
        # show acquired image
        img = Image.fromarray(numpy_image, 'RGB')
        image_name = photo_name
        if "." not in photo_name:
            image_name = "%s.jpg" % photo_name
        img.save(os.path.join(save_path, image_name))

        # stop data acquisition
        self.cam.stream_off()
        return image_name

    async def take_photos(self, save_path, photo_name, interval, times):
        for i in range(times):
            self.cam.stream_on()
            await asyncio.sleep(interval)
            numpy_image, raw_image = self.gather()
            # show acquired image
            img = Image.fromarray(numpy_image, 'RGB')
            img.save(os.path.join(save_path, "%s-%d.jpg" % (photo_name, i)))

            # stop data acquisition
            self.cam.stream_off()
        return

    def take_photos_sync(self, save_path, photo_name, interval, times):
        for i in range(times):
            self.cam.stream_on()
            time.sleep(interval)  # 使用 time.sleep 代替 await asyncio.sleep
            numpy_image, raw_image = self.gather()
            
            # 保存采集的图像
            img = Image.fromarray(numpy_image, 'RGB')
            img.save(os.path.join(save_path, "%s-%d.jpg" % (photo_name, i)))

            # 停止数据采集
            self.cam.stream_off()
        return