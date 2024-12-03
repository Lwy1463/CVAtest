<template>
  <div>
    <h2>嵌入唤醒配置</h2>
    <a-form :model="config">
      <!-- 不同语料间嵌入 -->
      <p>不同语料间嵌入</p>
      <a-form-item label="唤醒等待 (ms)">
        <a-input-number v-model:value="config.wakeUpWaitDifferent" />
      </a-form-item>
      <a-form-item label="嵌入频次">
        <a-radio-group v-model:value="config.frequencyDifferent">
          <a-radio value="none">不嵌入</a-radio>
          <a-radio value="first">首次</a-radio>
          <a-radio value="every">每次</a-radio>
          <a-radio value="interval">间隔</a-radio>
        </a-radio-group>
      </a-form-item>
      <a-form-item v-if="config.frequencyDifferent === 'interval'" label="播放一次唤醒的间隔">
        <a-input-number v-model:value="config.frequencyIntervalDifferent" />
      </a-form-item>

      <!-- 语料重复时嵌入 -->
      <p v-if="config.frequencyDifferent === 'every'">语料重复时嵌入</p>
      <a-form-item label="唤醒等待 (ms)" v-if="config.frequencyDifferent === 'every'">
        <a-input-number v-model:value="config.wakeUpWaitRepeated" />
      </a-form-item>
      <a-form-item label="嵌入频次" v-if="config.frequencyDifferent === 'every'">
        <a-radio-group v-model:value="config.frequencyRepeated">
          <a-radio value="none">不嵌入</a-radio>
          <a-radio value="every">每次</a-radio>
        </a-radio-group>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup>
import { defineProps, toRefs, watch } from 'vue';

const props = defineProps({
  config: {
    type: Object,
    required: true,
  },
});

const { config } = toRefs(props);

// 初始化默认值
if (!config.value.wakeUpWaitDifferent) {
  config.value.wakeUpWaitDifferent = 0;
}
if (!config.value.frequencyDifferent) {
  config.value.frequencyDifferent = 'first';
}
if (!config.value.frequencyIntervalDifferent) {
  config.value.frequencyIntervalDifferent = 0;
}
if (!config.value.wakeUpWaitRepeated) {
  config.value.wakeUpWaitRepeated = 0;
}
if (!config.value.frequencyRepeated) {
  config.value.frequencyRepeated = 'none';
}
</script>