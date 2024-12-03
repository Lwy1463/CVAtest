<template>
  <div>
    <h2>开始配置</h2>
    <a-form :model="config">
      <a-form-item label="循环次数">
        <a-input-number v-model:value="config.circle" />
      </a-form-item>
      <a-form-item label="输出通道">
        <a-select v-model:value="config.channel">
          <a-select-option value="channel1">Channel 1</a-select-option>
          <a-select-option value="channel2">Channel 2</a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item label="输出增益 (dB)">
        <a-input-number v-model:value="config.gain" />
      </a-form-item>

      <!-- 根据 type 动态渲染表单项 -->
      <template v-if="type === 'rouse'">
        <a-form-item label="唤醒时间">
          <a-switch v-model:checked="config.wakeup_time" />
        </a-form-item>
        <a-form-item label="唤醒成功率">
          <a-switch v-model:checked="config.wakeup_success_rate" />
        </a-form-item>
      </template>

      <template v-if="type === 'false-rouse'">
        <a-form-item label="误唤醒次数">
          <a-switch v-model:checked="config.false_wakeup_times" />
        </a-form-item>
      </template>

      <template v-if="type === 'interaction'">
        <a-form-item label="交互成功率">
          <a-switch v-model:checked="config.interaction_success_rate" />
        </a-form-item>
        <a-form-item label="字识别率">
          <a-switch v-model:checked="config.word_recognition_rate" />
        </a-form-item>
        <a-form-item label="响应时间">
          <a-switch v-model:checked="config.response_time" />
        </a-form-item>
      </template>

      <template v-if="type === 'interaction-multi'">
        <a-form-item label="交互成功率">
          <a-switch v-model:checked="config.interaction_success_rate" />
        </a-form-item>
      </template>
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
  type: {
    type: String,
    required: true,
  },
});

const { config, type } = toRefs(props);
</script>