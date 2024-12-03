<template>
  <a-tabs v-model:activeKey="activeType" @change="onTypeChange" style="padding: 0 20px; background-color: #f5f7fa">
      <a-tab-pane key="rouse" tab="唤醒"></a-tab-pane>
      <a-tab-pane key="false-rouse" tab="误唤醒"></a-tab-pane>
      <a-tab-pane key="interaction" tab="单次对话"></a-tab-pane>
      <a-tab-pane key="interaction-multi" tab="连续对话"></a-tab-pane>
  </a-tabs>
  <div style="display: flex; height: calc(100vh - 3rem); margin: 0; background-color: #f5f7fa; font-family: 'Arial', sans-serif;">
    <!-- 顶部：切换 type 的 a-tab -->

    <!-- 左侧：播放配置列表 -->
    <div style="flex: 1; margin-right: 20px; overflow-y: auto; padding: 20px;">
      <a-card title="播放配置列表" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
        <a-list bordered :dataSource="playConfigs">
          <template #renderItem="{ item }">
            <a-list-item
              :class="{ 'selected': selectedConfig && selectedConfig.play_config_id === item.play_config_id }"
              @click="selectConfig(item)"
              @mouseenter="hoverItem = item"
              @mouseleave="hoverItem = null"
              style="border-radius: 10px;"
            >
              <a-list-item-meta>
                <template #title>
                  <a-tooltip>
                    <div style="font-weight: bold;  width: 50px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ item.config_name }}</div>
                    <template #title>{{ item.config_name }}</template>

                  </a-tooltip>
                  <a-tooltip>
                    <div style="color: #ccc; width: 50px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ item.description }}</div>
                    <template #title>{{ item.description }}</template>
                  </a-tooltip>

                </template>
              </a-list-item-meta>
              <template #actions>
                <a @click.stop="editPlayConfig(item)" style="color: #de8dcc;">编辑</a>
                <a @click.stop="deletePlayConfig(item.play_config_id)" style="color: #de8dcc;">删除</a>
              </template>
            </a-list-item>
          </template>
        </a-list>
        <a-card
          style="margin-top: 20px; border-radius: 10px; cursor: pointer; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);"
          @click="showCreateModal"
        >
          <div style="text-align: center;">
            <a-icon type="plus" style="font-size: 24px; color: #de8dcc;" />
            <div style="font-size: 16px; color: #de8dcc;">新建配置</div>
          </div>
        </a-card>
      </a-card>
    </div>

    <!-- 中间：Canvas -->
    <div style="flex: 3.2; margin-right: 20px; overflow-y: auto; padding: 20px;">
      <a-card title="配置项" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
        <canvas
          ref="canvas"
          width="700"
          height="500"
          style="background-color: #f0f2f5; border-radius: 10px; position: relative; margin-top: 20px; box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.1);
           cursor: pointer
          "
          @click="onCanvasClick"
        ></canvas>
        <a-button type="primary" @click="savePlayConfig" style="margin-top: 20px; background-color: #de8dcc; border-color: #de8dcc;">保存</a-button>
      </a-card>
    </div>

    <!-- 右侧：可拖拽的播放配置项 -->
    <div style="flex: 1.1; overflow-y: auto; padding: 20px;">
      <a-card title="配置项设置" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
        <div v-if="selectedItem">
          <component :is="getFormComponent(selectedItem.type)" v-model:config="selectedItem.config" :type="activeType"/>
        </div>
      </a-card>
    </div>

    <!-- 创建播放配置的模态框 -->
    <a-modal
      title="添加播放配置"
      v-model:visible="createModalVisible"
      @ok="createPlayConfig"
      @cancel="handleCancel"
      okText="确定"
      cancelText="取消"
    >
      <a-form :model="createFormData" :rules="rules">
        <a-form-item label="配置名称" config_name="config_name">
          <a-input v-model:value="createFormData.config_name" />
        </a-form-item>
        <a-form-item label="配置描述" config_name="description">
          <a-input v-model:value="createFormData.description" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 编辑播放配置的模态框 -->
    <a-modal
      title="编辑播放配置"
      v-model:visible="editModalVisible"
      @ok="saveEditPlayConfig"
      @cancel="handleEditCancel"
      okText="确定"
      cancelText="取消"
    >
      <a-form :model="editFormData" :rules="rules">
        <a-form-item label="配置名称" config_name="config_name">
          <a-input v-model:value="editFormData.config_name" />
        </a-form-item>
        <a-form-item label="配置描述" config_name="description">
          <a-input v-model:value="editFormData.description" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 添加配置项的模态框 -->
    <a-modal
      title="添加配置项"
      v-model:visible="addItemModalVisible"
      @ok="confirmAddItem"
      @cancel="handleAddItemCancel"
      okText="确定"
      cancelText="取消"
    >
      <a-select v-model:value="selectedItemType" style="width: 100%;">
        <a-select-option v-for="type in filteredItemTypes" :key="type" :value="type">
          {{ type }}
        </a-select-option>
      </a-select>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { http } from '@renderer/http';
import { ElMessage, ElMessageBox } from 'element-plus';

// 导入 SVG 文件
import playCircleIcon from './icons/play_circle.svg';
import clockCircleIcon from './icons/clock_circle.svg';
import soundIcon from './icons/sound.svg';
import audioIcon from './icons/audio.svg';
import warningIcon from './icons/warning.svg';
import startIcon from './icons/start.svg';

// 导入表单组件
import PlayCorpusForm from './components/PlayCorpusForm.vue';
import PlayRouseForm from './components/PlayRouseForm.vue';
import WaitForm from './components/WaitForm.vue';
import BackgroundNoiseForm from './components/BackgroundNoiseForm.vue';
import InterferenceForm from './components/InterferenceForm.vue';
import WakeUpForm from './components/WakeUpForm.vue';
import StartForm from './components/StartForm.vue';
import EmptyForm from './components/EmptyForm.vue';

const playConfigs = ref([]);
const createModalVisible = ref(false);
const editModalVisible = ref(false);
const addItemModalVisible = ref(false);
const selectedConfig = ref(null);
const selectedConfigItems = ref([]);
const itemTypes = [
  '播放语料', '等待', '嵌入唤醒', '播放背景噪声', '播放干扰音', '播放唤醒'
];
const selectedItemType = ref(null);
const hoverItem = ref(null);
const selectedItem = ref(null);
const activeType = ref('rouse'); // 默认选中唤醒

const createFormData = reactive({
  config_name: '',
  description: '',
  type: 'rouse', // 默认类型为唤醒
});

const editFormData = reactive({
  play_config_id: null,
  config_name: '',
  description: '',
  configs: [],
  type: 'rouse', // 默认类型为唤醒
});

const rules = {
  config_name: [{ required: true, message: '请填写配置名称', trigger: 'blur' }],
  description: [{ required: true, message: '请填写配置描述', trigger: 'blur' }],
};

const fetchPlayConfigs = async () => {
  const response = await http.post('/play_config/get_play_config_list', { type: activeType.value });
  playConfigs.value = response.data || [];
  if (playConfigs.value.length > 0) {
    selectConfig(playConfigs.value[0]); // 默认选中第一个配置
  } else {
    clearSelectedConfig(); // 如果没有配置，清空选中的配置
  }
};

const clearSelectedConfig = () => {
  selectedConfig.value = null;
  selectedConfigItems.value = [];
  drawCanvas(); // 清空 canvas
};

const showCreateModal = () => {
  createFormData.type = activeType.value; // 设置创建表单的类型为当前选中的类型
  createFormData.config_name = ''; // 清空配置名称
  createFormData.description = ''; // 清空配置描述
  createModalVisible.value = true;
};
const handleCancel = () => {
  createModalVisible.value = false;
};

const createPlayConfig = async () => {
  if (!createFormData.config_name || !createFormData.description) {
    ElMessage.error('请填写完整信息');
    return;
  }
  await http.post('/play_config/create_play_config', createFormData);
  createModalVisible.value = false;
  fetchPlayConfigs();
};

const editPlayConfig = (item) => {
  editFormData.play_config_id = item.play_config_id;
  editFormData.config_name = item.config_name;
  editFormData.description = item.description;
  editFormData.configs = item.configs;
  editFormData.type = item.type;
  editModalVisible.value = true;
};

const handleEditCancel = () => {
  editModalVisible.value = false;
};

const saveEditPlayConfig = async () => {
  if (!editFormData.config_name || !editFormData.description) {
    ElMessage.error('请填写完整信息');
    return;
  }
  await http.post('/play_config/update_play_config', editFormData);
  if (selectedConfig.value.play_config_id === editFormData.play_config_id) {
    selectedConfig.value.config_name = editFormData.config_name;
    selectedConfig.value.description = editFormData.description;
  }
  editModalVisible.value = false;
  fetchPlayConfigs();
};

const deletePlayConfig = async (id) => {
  http.post('/play_config/delete_play_config', { play_config_id: id }).then(resp => {
    fetchPlayConfigs();
  }).catch(err => {
    if (err.response.data.error) {
      ElMessage.error(err.response.data.error);
    }
  });

};

const selectConfig = (config) => {
  selectedConfig.value = config;
  console.log(config);
  selectedConfigItems.value = [
    ...config.configs
  ].map((item, index) => ({
    ...item,
    x: 0,
    y: index * 80, // 垂直居中
  }));
  drawCanvas();
};

const canvas = ref(null);
const ctx = ref(null);
const isDragging = ref(false);
const dragStartPosition = ref({ x: 0, y: 0 });
const viewPosition = ref({ x: 0, y: 0 });

const drawCanvas = () => {
  if (!ctx.value) return;
  ctx.value.clearRect(0, 0, canvas.value.width, canvas.value.height);

  selectedConfigItems.value.forEach((item, index) => {
    const x = (canvas.value.width - 150) / 2 + viewPosition.value.x; // 居中对齐并加上视图偏移
    const y = item.y + 50 + viewPosition.value.y; // 加上开始标签的高度并加上视图偏移
    const width = 150;
    const height = 50;

    // 绘制圆角矩形框
    ctx.value.strokeStyle = '#de8dcc'; // 修改为紫色
    ctx.value.lineWidth = 2;
    ctx.value.beginPath();
    ctx.value.roundRect(x, y, width, height, 10);
    ctx.value.stroke();

    // 渲染图标的位置往下一点
    // 绘制图标
    const icon = getIcon(item.type);
    const iconImage = new Image();
    iconImage.src = icon;
    iconImage.onload = () => {
      ctx.value.drawImage(iconImage, x + 5, y + 10, 20, 20);
    };

    // 绘制文本
    ctx.value.fillStyle = 'black';
    ctx.value.font = '14px Arial';
    ctx.value.fillText(item.type, x + 30, y + 30);

    // 绘制加号按钮
    if (index >= 0) {
      ctx.value.fillStyle = '#de8dcc'; // 修改为紫色
      ctx.value.fillRect(x + width + 10, y + height / 2 - 10, 20, 20);
      ctx.value.fillStyle = 'white';
      ctx.value.font = '16px Arial';
      ctx.value.fillText('+', x + width + 15, y + height / 2 + 5);
    }

    // 绘制减号按钮
    if (index >= 0) {
      ctx.value.fillStyle = '#de8dcc'; // 修改为紫色
      ctx.value.fillRect(x - 30, y + height / 2 - 10, 20, 20);
      ctx.value.fillStyle = 'white';
      ctx.value.font = '16px Arial';
      ctx.value.fillText('-', x - 25, y + height / 2 + 5);
    }

    // 绘制连接线
    if (index > 0) {
      const prevItem = selectedConfigItems.value[index - 1];
      ctx.value.beginPath();
      ctx.value.moveTo((canvas.value.width - 150) / 2 + width / 2 + viewPosition.value.x, prevItem.y + height + 50 + viewPosition.value.y);
      ctx.value.lineTo((canvas.value.width - 150) / 2 + width / 2 + viewPosition.value.x, y);
      ctx.value.strokeStyle = '#de8dcc'; // 修改为紫色
      ctx.value.stroke();
    }
  });
};

const onCanvasClick = (event) => {
  const rect = canvas.value.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;

  selectedConfigItems.value.forEach((item, index) => {
    const width = 150;
    const height = 50;
    const itemX = (canvas.value.width - 150) / 2 + viewPosition.value.x; // 居中对齐并加上视图偏移
    const itemY = item.y + 50 + viewPosition.value.y; // 加上开始标签的高度并加上视图偏移

    if (x >= itemX && x <= itemX + width && y >= itemY && y <= itemY + height) {
      selectedItem.value = item;
    } else if (x >= itemX + width + 10 && x <= itemX + width + 30 && y >= itemY + height / 2 - 10 && y <= itemY + height / 2 + 10) {
      showAddItemModal(index);
    } else if (x >= itemX - 30 && x <= itemX - 10 && y >= itemY + height / 2 - 10 && y <= itemY + height / 2 + 10) {
      deleteItem(index);
    }
  });
};

const showAddItemModal = (index) => {
  selectedItemIndex.value = index;
  addItemModalVisible.value = true;
  selectedItemType.value = filteredItemTypes.value[0]; // 设置默认选中项
};

const handleAddItemCancel = () => {
  addItemModalVisible.value = false;
};

const confirmAddItem = () => {
  const index = selectedItemIndex.value;
  const newItem = {
    type: selectedItemType.value,
    x: 0,
    y: (index + 1) * 80, // 垂直居中
    config: getDefaultConfig(selectedItemType.value),
  };

  // 检查是否已经存在相同类型的配置项
  const isDuplicate = selectedConfigItems.value.some(item => item.type === newItem.type);
  if (isDuplicate) {
    ElMessage.error('当前配置列表中已存在相同类型的配置项');
    return;
  } else {
    selectedConfigItems.value.splice(index + 1, 0, newItem);
    selectedConfigItems.value.forEach((item, i) => {
      item.y = i * 80; // 重新计算所有项的 y 坐标
    });
    addItemModalVisible.value = false;
    drawCanvas();
    selectedItem.value = newItem; // 默认选中添加的配置项
  }
};

const selectedItemIndex = ref(null);

const getIcon = (type) => {
  const icons = {
    '播放语料': playCircleIcon,
    '播放唤醒': playCircleIcon, // 使用相同的图标
    '等待': clockCircleIcon,
    '嵌入唤醒': soundIcon,
    '播放背景噪声': audioIcon,
    '播放干扰音': warningIcon,
    '开始': startIcon, // 使用一个默认图标
  };
  return icons[type];
};

const getFormComponent = (type) => {
  const components = {
    '播放语料': PlayCorpusForm,
    '播放唤醒': PlayRouseForm, // 使用新的 PlayRouseForm 组件
    '等待': WaitForm,
    '播放背景噪声': BackgroundNoiseForm,
    '播放干扰音': InterferenceForm,
    '嵌入唤醒': WakeUpForm,
    '开始': StartForm,
  };
  return components[type];
};

const getDefaultConfig = (type) => {
  const defaultConfigs = {
    '播放语料': { gain: 0, channel: 'channel1', repeat: 1, wait_time: 5, timout: 10},
    '播放唤醒': { gain: 0, channel: 'channel1', repeat: 1 }, // 使用相同的默认配置
    '等待': { duration: 1000 },
    '播放背景噪声': { gain: 0, channel: 'channel1' },
    '播放干扰音': { gain: 0, channel: 'channel1' },
    '嵌入唤醒': { wakeUpWaitDifferent: 500, frequencyDifferent: 'every', frequencyIntervalDifferent: 1, wakeUpWaitRepeated: 500, frequencyRepeated: 'none'},
    '开始': {
      circle: '3',
      wakeup_time: false,
      wakeup_success_rate: false,
      false_wakeup_times: false,
      interaction_success_rate: false,
      word_recognition_rate: false,
      response_time: false,
    },
  };
  return defaultConfigs[type];
};

const savePlayConfig = async () => {
  if (!selectedConfig.value) {
    ElMessage.error('请选择一个配置进行保存');
    return;
  }

  const payload = {
    play_config_id: selectedConfig.value.play_config_id,
    config_name: selectedConfig.value.config_name,
    description: selectedConfig.value.description,
    configs: selectedConfigItems.value.map(item => ({
      type: item.type,
      config: item.config,
    })),
    type: activeType.value
  };

  try {
    await http.post('/play_config/update_play_config', payload);
    ElMessage.success('配置保存成功');
    fetchPlayConfigs(); // Refresh the list after saving
  } catch (error) {
    ElMessage.error('配置保存失败，请重试');
    console.error(error);
  }
};

const deleteItem = (index) => {
  if (index === 0) {
    ElMessage.error('不能删除开始配置项');
    return;
  }
  selectedConfigItems.value.splice(index, 1);
  selectedConfigItems.value.forEach((item, i) => {
    item.y = i * 80; // 重新计算所有项的 y 坐标
  });
  drawCanvas();
};

const onMouseDown = (event) => {
  isDragging.value = true;
  dragStartPosition.value = {
    x: event.clientX,
    y: event.clientY,
  };
};

const onMouseMove = (event) => {
  if (!isDragging.value) return;

  const dx = event.clientX - dragStartPosition.value.x;
  const dy = event.clientY - dragStartPosition.value.y;

  viewPosition.value.x += dx;
  viewPosition.value.y += dy;

  dragStartPosition.value = {
    x: event.clientX,
    y: event.clientY,
  };

  drawCanvas();
};

const onMouseUp = () => {
  isDragging.value = false;
};

const onTypeChange = () => {
  fetchPlayConfigs();
  filterItemTypes();
};

const filterItemTypes = () => {
  if (activeType.value === 'rouse') {
    filteredItemTypes.value = [...itemTypes].filter(type => { return type !== '播放语料' && type !== '嵌入唤醒' });
  } else if (activeType.value === 'false-rouse') {
    filteredItemTypes.value = [...itemTypes].filter(type => { return  type !== '播放语料' && type !== '嵌入唤醒' });
  } else if (activeType.value === 'interaction') {
    filteredItemTypes.value = [...itemTypes].filter(type => { return type !== '播放唤醒' });
  } else if (activeType.value === 'interaction-multi') {
    filteredItemTypes.value = [...itemTypes].filter(type => { return type !== '播放唤醒' });
  }
};

const filteredItemTypes = ref([...itemTypes]);

onMounted(() => {
  fetchPlayConfigs().finally(() => {
    nextTick(() => {
      canvas.value = document.querySelector('canvas');
      ctx.value = canvas.value.getContext('2d');
      drawCanvas();

      canvas.value.addEventListener('mousedown', onMouseDown);
      canvas.value.addEventListener('mousemove', onMouseMove);
      canvas.value.addEventListener('mouseup', onMouseUp);
      canvas.value.addEventListener('mouseleave', onMouseUp);
    });
  });
  filterItemTypes();
});

onBeforeUnmount(() => {
  canvas.value.removeEventListener('mousedown', onMouseDown);
  canvas.value.removeEventListener('mousemove', onMouseMove);
  canvas.value.removeEventListener('mouseup', onMouseUp);
  canvas.value.removeEventListener('mouseleave', onMouseUp);
});
</script>

<style scoped>
/* 样式代码 */
.selected {
  background-color: #e6f7ff;
}

.ant-list-item:hover {
  background-color: #f5f5f5;
}
</style>