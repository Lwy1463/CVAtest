<template>
  <div style="margin: 2rem;">
    <!-- 上方tab -->
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" tab="数据采集">
        <!-- 下方配置项 -->
        <a-card title="设备配置" style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); height: calc(100vh - 14rem);">
          <div>
            <strong>抓拍</strong>
            <a-form :model="device_config" layout="inline">
              <a-form-item label="抓拍频率（张/秒）" name="camera_interval" :rules="[{ required: true, message: '请输入抓拍频率' }]">
                <a-input v-model:value="device_config.camera_interval" />
              </a-form-item>
              <a-form-item label="抓拍次数" name="camera_times" :rules="[{ required: true, message: '请输入抓拍次数' }]">
                <a-input v-model:value="device_config.camera_times" />
              </a-form-item>
              <a-form-item label="抓拍开始等待时间（秒）" name="camera_start_wait" :rules="[{ required: true, message: '请输入抓拍开始等待时间' }]">
                <a-input v-model:value="device_config.camera_start_wait" />
              </a-form-item>
              <a-form-item label="结果照片间隔（秒）" name="result_photo_interval" :rules="[{ required: true, message: '请输入结果照片间隔' }]">
                <a-input v-model:value="device_config.result_photo_interval" />
              </a-form-item>
              <a-form-item label="结果照片差异率（%）" name="result_photo_diff_rate" :rules="[{ required: true, message: '请输入结果照片差异率' }]">
                <a-input v-model:value="device_config.result_photo_diff_rate" />
              </a-form-item>
              <a-form-item label="结果开始等待时间（秒）" name="result_start_wait" :rules="[{ required: true, message: '请输入结果开始等待时间' }]">
                <a-input v-model:value="device_config.result_start_wait" />
              </a-form-item>
            </a-form>
          </div>
          <div style="margin-top: 20px;">
            <strong>录像</strong>
            <a-form :model="device_config" layout="inline">
              <a-form-item label="分辨率 宽(px)" name="video_width" :rules="[{ required: true, message: '请输入分辨率宽度' }]">
                <a-input v-model:value="device_config.video_width" />
              </a-form-item>
              <a-form-item label="分辨率 高(px)" name="video_height" :rules="[{ required: true, message: '请输入分辨率高度' }]">
                <a-input v-model:value="device_config.video_height" />
              </a-form-item>
              <a-form-item label="帧率（帧/秒）" name="video_frame_rate" :rules="[{ required: true, message: '请输入帧率' }]">
                <a-input v-model:value="device_config.video_frame_rate" />
              </a-form-item>
            </a-form>
          </div>
          <a-button type="primary" @click="submit_config" style="margin-top: 20px;">提交配置</a-button>
        </a-card>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { http } from '@renderer/http';

// 设备配置数据
const device_config = ref({
  camera_interval: '',
  camera_times: '',
  camera_start_wait: '',
  result_photo_interval: '',
  result_photo_diff_rate: '',
  result_start_wait: '',
  video_width: '',
  video_height: '',
  video_frame_rate: '', // 新增帧率字段
});

// 获取设备配置
const get_device_config = async () => {
  try {
    const response = await http.post('/device/config_get');

    const data = response;
    device_config.value = {
      camera_interval: Number(data.camera_interval),
      camera_times: Number(data.camera_times),
      camera_start_wait: Number(data.camera_start_wait),
      result_photo_interval: Number(data.result_photo_interval),
      result_photo_diff_rate: Number(data.result_photo_diff_rate) * 100, // 将小数转换为百分比
      result_start_wait: Number(data.result_start_wait),
      video_width: Number(data.video_width),
      video_height: Number(data.video_height),
      video_frame_rate: Number(data.video_frame_rate || 30), // 新增帧率字段
    };
  } catch (error) {
    message.error('获取设备配置失败');
    console.error(error);
  }
};

// 提交配置
const submit_config = async () => {
  try {
    const response = await http.post('/device/config_set', {
      camera_interval: Number(device_config.value.camera_interval),
      camera_times: Number(device_config.value.camera_times),
      camera_start_wait: Number(device_config.value.camera_start_wait),
      result_photo_interval: Number(device_config.value.result_photo_interval),
      result_photo_diff_rate: Number(device_config.value.result_photo_diff_rate) / 100, // 将百分比转换为小数
      result_start_wait: Number(device_config.value.result_start_wait),
      video_width: Number(device_config.value.video_width),
      video_height: Number(device_config.value.video_height),
      video_frame_rate: Number(device_config.value.video_frame_rate), // 新增帧率字段
    });
    if (response.status === 'success') {
      message.success('配置提交成功');
    }
  } catch (error) {
    message.error('配置提交失败');
    console.error(error);
  }
};

// 组件挂载后调用获取设备配置
onMounted(() => {
  get_device_config();
});
</script>
<style scoped>
/* 自定义样式 */
.ant-card {
  margin-top: 10px;
}

.ant-form-item {
  margin-bottom: 10px;
}
</style>