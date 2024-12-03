<!-- RepeatForm.vue -->
<template>
    <div>
      <h2>重复语料配置</h2>
      <a-form :model="config">
        <a-form-item label="次数">
          <a-input-number v-model:value="config.repeatCount" />
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