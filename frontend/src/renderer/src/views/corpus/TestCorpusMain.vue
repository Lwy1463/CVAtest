<template>
    <a-tabs v-model:activeKey="activeTab" @change="handleTabChange" style="margin: 1rem"> 
        <a-tab-pane key="test" tab="普通语料">
            <!-- 测试语料内容 -->
            <test-corpus></test-corpus>
        </a-tab-pane>
        <a-tab-pane key="multi" tab="多轮对话语料">
            <multi-corpus></multi-corpus>
        </a-tab-pane>
    </a-tabs>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TestCorpus from './TestCorpus.vue'
import MultiCorpus from './MultiCorpus.vue';
const activeTab = ref('test');
const handleTabChange = (key: string) => {
    activeTab.value = key;
  };
</script>

<style scoped></style>