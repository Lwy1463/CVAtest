<template>
    <div>
      <h2>人工确认配置</h2>
      <a-form :model="config">
        <a-form-item label="确认方式">
          <a-radio-group v-model:value="config.confirmMethod">
            <a-radio value="测试结果确认">测试结果确认</a-radio>
            <a-radio value="测试操作确认">测试操作确认</a-radio>
          </a-radio-group>
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