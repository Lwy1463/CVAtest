<template>
    <div style="margin: 20px;">
      <a-tabs v-model:activeKey="activeTab" @change="handleTabChange">
        <a-tab-pane key="test" tab="测试语料">
          <!-- 测试语料内容 -->
          <test-corpus-main></test-corpus-main>
        </a-tab-pane>
        <a-tab-pane key="wake" tab="唤醒语料">
          <!-- 唤醒语料内容 -->
          <wake-corpus></wake-corpus>
        </a-tab-pane>
        <a-tab-pane key="interference" tab="干扰语料">
          <!-- 干扰语料内容 -->
          <interference-corpus></interference-corpus>
        </a-tab-pane>
        <a-tab-pane key="background" tab="背景噪声">
          <!-- 背景噪声内容 -->
          <background-noise></background-noise>
        </a-tab-pane>
        <!-- <a-tab-pane key="multi" tab="多轮对话语料">
          <multi-corpus></multi-corpus>
        </a-tab-pane> -->
      </a-tabs>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue';
  import TestCorpusMain from './TestCorpusMain.vue';
  import WakeCorpus from './WakeCorpus.vue';
  import MultiCorpus from './MultiCorpus.vue';
  import InterferenceCorpus from './InterferenceCorpus.vue';
  import BackgroundNoise from './BackgroundNoise.vue'
  
  const activeTab = ref('test');
  
  const handleTabChange = (key: string) => {
    activeTab.value = key;
  };
  </script>
  
  <style scoped>
  /* 你可以在这里添加一些样式 */
  </style>