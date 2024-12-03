<template>
  <div>
    <h2>{{ type }} 配置</h2>
    <p>暂无配置项</p>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  type: {
    type: String,
    required: true,
  },
});
</script>