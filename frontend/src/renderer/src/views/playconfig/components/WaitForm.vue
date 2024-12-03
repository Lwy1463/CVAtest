<!-- WaitForm.vue -->
<template>
    <div>
      <h2>等待配置</h2>
      <a-form :model="config">
        <a-form-item label="时长 (ms)">
          <a-input-number v-model:value="config.duration" />
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