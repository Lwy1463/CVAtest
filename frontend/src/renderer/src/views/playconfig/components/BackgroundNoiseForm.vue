<!-- BackgroundNoiseForm.vue -->
<template>
    <div>
      <h2>播放背景噪声配置</h2>
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