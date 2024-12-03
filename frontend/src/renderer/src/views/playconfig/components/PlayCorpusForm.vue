<template>
  <div>
    <h2>播放语料配置</h2>
    <a-form :model="config">
      <a-form-item label="输出增益 (dB)">
        <a-input-number v-model:value="config.gain" />
      </a-form-item>
      <a-form-item label="输出通道">
        <a-select v-model:value="config.channel">
          <a-select-option value="channel1">Channel 1</a-select-option>
          <a-select-option value="channel2">Channel 2</a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item label="重复次数">
        <a-input-number v-model:value="config.repeat" />
      </a-form-item>
      <!-- 新增的播放语料响应时间字段 -->
      <a-form-item label="无声音等待时间 (s)">
        <a-input-number v-model:value="config.wait_time" />
      </a-form-item>
      <a-form-item label="最长录制时间 (s)">
        <a-input-number v-model:value="config.timout" />
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup>
import { defineProps, toRefs } from 'vue';

const props = defineProps({
  config: {
    type: Object,
    required: true,
  },
});

const { config } = toRefs(props);
</script>