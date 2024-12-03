<template>
  <div style="display: flex; height: 100%; width: 100%;">
    <!-- 中间 -->
    <a-card title="选择播放配置" style="height: 100%; width: 100%;">
      <a-tree
        :tree-data="treeData"
        v-model:expandedKeys="expandedKeys"
        v-model:selectedKeys="selectedKeys"
        @select="onSelect"
      >
        <template #title="{ title, key }">
          <span>{{ title }}</span>
        </template>
      </a-tree>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, defineEmits, defineProps } from 'vue';
import { http } from '@renderer/http';

const emit = defineEmits(['update:modelValue', 'rouseSceneSelected']);
const props = defineProps({
  modelValue: {
    type: String,
    default: null,
  },
});
const allData = ref([]);
const treeData = ref([]);
const expandedKeys = ref([]); // 初始化 expandedKeys
const selectedKeys = ref([]); // 初始化 selectedKeys

const fetchPlayConfigs = async () => {
  const response = await http.post('/play_config/get_play_config_list', {});
  allData.value = response.data;
  const rouseConfigs = response.data.filter(config => config.type === 'rouse');
  const falseRouseConfigs = response.data.filter(config => config.type === 'false-rouse');
  const interactionConfigs = response.data.filter(config => config.type === 'interaction');
  const interactionMultiConfigs = response.data.filter(config => config.type === 'interaction-multi');

  treeData.value = [
    {
      title: '唤醒场景',
      key: 'rouse',
      selectable: false, // 设置为不可选择
      children: rouseConfigs.map(config => ({
        title: config.config_name,
        key: `rouse-${config.play_config_id}`,
      })),
    },
    {
      title: '误唤醒场景',
      key: 'false-rouse',
      selectable: false, // 设置为不可选择
      children: falseRouseConfigs.map(config => ({
        title: config.config_name,
        key: `false-rouse-${config.play_config_id}`,
      })),
    },
    {
      title: '智能交互场景',
      key: 'interaction',
      selectable: false, // 设置为不可选择
      children: interactionConfigs.map(config => ({
        title: config.config_name,
        key: `interaction-${config.play_config_id}`,
      })),
    },
    {
      title: '连续对话场景',
      key: 'interaction-multi',
      selectable: false, // 设置为不可选择
      children: interactionMultiConfigs.map(config => ({
        title: config.config_name,
        key: `interaction-multi-${config.play_config_id}`,
      })),
    },
  ];

  // 获取所有节点的 key
  expandedKeys.value = ['rouse', 'false-rouse', 'interaction', 'interaction-multi']; // 设置默认展开的节点
};

const onSelect = (selectedKeys, info) => {
  if (selectedKeys.length > 0) {
    const selectedPlayConfigIdSplit = selectedKeys[0].split('-');
    const selectedPlayConfigId = selectedPlayConfigIdSplit[selectedPlayConfigIdSplit.length - 1];
    emit('update:modelValue', selectedPlayConfigId);

    // 判断选择的节点类型
    const selectedKey = selectedKeys[0];
    console.log(allData.value);
    const selectedData = allData.value.find(x => x.play_config_id === selectedPlayConfigId);
    if (selectedKey.startsWith('rouse-')) {
      emit('rouseSceneSelected', true, selectedData); // 通知父组件选择了唤醒场景
    } else if (selectedKey.startsWith('false-rouse-')) {
      emit('rouseSceneSelected', true, selectedData); // 通知父组件选择了误唤醒场景
    } else if (selectedKey.startsWith('interaction-') && !selectedKey.startsWith('interaction-multi-')) {
      emit('rouseSceneSelected', false, selectedData); // 通知父组件选择了智能交互场景
    } else if (selectedKey.startsWith('interaction-multi-')) {
      emit('rouseSceneSelected', false, selectedData); // 通知父组件选择了连续对话场景
    }
  } else {
    emit('update:modelValue', null);
    emit('rouseSceneSelected', false); // 通知父组件没有选择任何场景
  }
};

onMounted(() => {
  fetchPlayConfigs();
});

watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal) {
      const selectedKey = treeData.value.flatMap(category => category.children).find((config) => {
        const list = config.key?.split('-') || [];
        return list[list.length - 1] === newVal
      })?.key;
      if (selectedKey) {
        selectedKeys.value = [selectedKey];
        const selectedPlayConfigIdSplit = selectedKey.split('-');
        const selectedPlayConfigId = selectedPlayConfigIdSplit[selectedPlayConfigIdSplit.length - 1];
        const selectedData = allData.value.find(x => x.play_config_id === selectedPlayConfigId);
        console.log(selectedData);
        if (selectedKey.startsWith('rouse-')) {
          emit('rouseSceneSelected', true, selectedData); // 通知父组件选择了唤醒场景
        } else if (selectedKey.startsWith('false-rouse-')) {
          emit('rouseSceneSelected', false, selectedData); // 通知父组件选择了误唤醒场景
        } else if (selectedKey.startsWith('interaction-')) {
          emit('rouseSceneSelected', false, selectedData); // 通知父组件选择了智能交互场景
        } else if (selectedKey.startsWith('interaction-multi-')) {
          emit('rouseSceneSelected', false, selectedData); // 通知父组件选择了连续对话场景
        }
      } else {
        selectedKeys.value = [];
      }
    } else {
      selectedKeys.value = [];
    }
  },
  { immediate: true }
);
</script>

<style scoped>
/* Add your custom styles here */
</style>