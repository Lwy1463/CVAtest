<template>
  <div
    style="background-color: #f0f2f5; height: calc(100vh - 14rem); padding: 1rem; display: flex; flex-direction: column;">
    <a-breadcrumb style="margin-bottom: 1rem;">
      <a-breadcrumb-item><a @click="goToProject">项目管理</a></a-breadcrumb-item>
      <a-breadcrumb-item>项目执行</a-breadcrumb-item>
    </a-breadcrumb>
    <a-row justify="space-between" align="top" style="flex: 1;">
      <a-col :span="9">
        <a-row>
          <a-col :span="24">
            <a-card :bordered="false" class="test-progress-card">
              <div class="test-progress">
                <a-progress type="circle" :percent="progress" />
                <div class="status-text">{{ statusText }}</div>
              </div>
              <a-row justify="center" style="margin-top: 20px;">
                <a-button type="primary" @click="startTest">开始测试</a-button>
                <a-button type="primary" style="margin-left: 10px;" @click="pauseTest">暂停测试</a-button>
                <a-button type="primary" style="margin-left: 10px;" @click="stopTest">停止测试</a-button>
              </a-row>
            </a-card>
          </a-col>
        </a-row>
        <a-row style="margin-top: 20px;">
          <a-col :span="24">
            <a-card :bordered="false" class="log-card">
              <div class="log-header">
                Log 信息
              </div>
              <div class="log-content">
                <pre style="min-height: 10rem;">{{ logContent }}</pre>
              </div>
            </a-card>
          </a-col>
        </a-row>
      </a-col>
      <a-col :span="15">
        <a-card :bordered="false" class="test-results-card">
          <div class="test-results-header">
            测试结果
          </div>
          <a-tabs v-model:activeKey="selectedType" @change="onTypeChange">
            <a-tab-pane key="interaction" tab="单次对话"></a-tab-pane>
            <a-tab-pane key="interaction-multi" tab="连续对话"></a-tab-pane>
            <a-tab-pane key="rouse" tab="唤醒"></a-tab-pane>
            <a-tab-pane key="false-rouse" tab="误唤醒"></a-tab-pane>

          </a-tabs>
          <a-row align="middle" style="margin-bottom: 1rem;">
            <a-col :span="8">
              <div style="display: flex; align-items: center;">
                <label style="margin-right: 10px;">Turn:</label>
                <a-select v-model:value="selectedTurnId" style="width: 12rem;" @change="onTurnChange">
                  <a-select-option v-for="turn in turns" :key="turn.turn_id" :value="turn.turn_id">
                    {{ turn.time }}
                  </a-select-option>
                </a-select>
              </div>
            </a-col>
            <a-col :span="8" style="text-align: right;">
              <div style="display: flex; align-items: center; justify-content: flex-end;">
                <label style="margin-right: 10px;">Plan:</label>
                <a-select v-model:value="selectedPlanId" style="width: 12rem;" @change="onPlanChange">
                  <a-select-option v-for="plan in treeData" :key="plan.key" :value="plan.key">
                    {{ plan.title }}
                  </a-select-option>
                </a-select>
              </div>
            </a-col>
          </a-row>
          <a-row justify="space-between" style="margin-bottom: 1rem;">
            <a-col :span="12">
              <a-button type="primary" style="margin-left: 1rem;" @click="exportResults">导出结果</a-button>
              <a-button type="primary" style="margin-left: 1rem;" @click="jumpToCheck">结果复核</a-button>
              <a-button type="primary" style="margin-left: 1rem" @click="refreshContinuously">刷新</a-button>
            </a-col>
          </a-row>
          <InteractionTable v-if="['rouse', 'false-rouse', 'interaction'].includes(selectedType)" :previewImage="previewImage"
             :testResults="testResults"></InteractionTable>
          <InteractionMultiTable v-if="selectedType === 'interaction-multi'" :testResults="testResults" :previewImage="previewImage"></InteractionMultiTable>
        </a-card>
      </a-col>
    </a-row>
    <!-- 图片预览模态框 -->
    <a-modal v-model:visible="imagePreviewVisible" :footer="null" @cancel="imagePreviewVisible = false"
      style="height: 80vh; width: 80vw">
      <div ref="imageContainer" @wheel="handleWheel"
        style="display: flex; justify-content: center; align-items: center; ">
        <img ref="previewImageRef" alt="example" :src="imagePreviewUrl" style="max-width: 100%; max-height: 100%;" />
      </div>
    </a-modal>
  </div>
</template>
<script lang="tsx" setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useProjectStore } from '@renderer/stores/useProject';
import { storeToRefs } from 'pinia';
import { http } from '@renderer/http';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import InteractionTable from './InteractionTable.vue';
import InteractionMultiTable from './InteractionMultiTable.vue';

const projectStore = useProjectStore();
const { projectDetail } = storeToRefs(projectStore);

const testResults = ref([]);
const progress = ref(0);
const treeData = ref([]);
const selectedKeys = ref<string[]>([]);
const logContent = ref('');
const statusText = ref('进行中');

const imagePreviewVisible = ref(false);
const imagePreviewUrl = ref('');
const turns = ref([]);
const selectedTurnId = ref('');
const imageContainer = ref(null);
const previewImageRef = ref(null);
const scale = ref(1);
const selectedType = ref('interaction'); // 默认选中唤醒

const selectedPlanId = ref('');

onMounted(() => {
  fetchPlanList().finally(() => {
    if (treeData.value.length > 0) {
      selectedKeys.value = [treeData.value[0].key];
      selectedPlanId.value = treeData.value[0].key;
    }
    fetchTurns();
  });

  // 监听 showpic 事件
  window.electron.ipcRenderer.on('showpic', (event, { data }) => {
    const blob = new Blob([data], { type: 'image/jpeg' });
    const url = URL.createObjectURL(blob);
    imagePreviewUrl.value = url;
    imagePreviewVisible.value = true;
  });

  window.electron.ipcRenderer.on('download-template-selected', (event, fileName) => {
    window.electron.ipcRenderer.send('start-download', base64String.value, fileName, 'results.xlsx', 'default', projectDetail.value.project_id);
  });
});

onUnmounted(() => {
  clearInterval(interval);
  window.electron.ipcRenderer.removeAllListeners('showpic');
});

const handleReportGenerated = (reportUrl) => {
  console.log('报告生成成功，URL:', reportUrl);
  // 你可以在这里处理报告生成的逻辑
};

const fetchPlanList = async () => {
  const response = await http.post('/test_project/get_plan_list', {
    project_id: projectDetail.value.project_id,
  });
  
  // 根据当前选中的 type 过滤 plan 列表
  const filteredData = response.data.filter(item => item.type === selectedType.value);
  
  treeData.value = filteredData.map(item => ({
    title: item.plan_name,
    key: item.plan_id,
  }));
  
  // 如果没有匹配的 plan，清空选择项
  if (treeData.value.length === 0) {
    selectedPlanId.value = '';
  } else {
    selectedPlanId.value = treeData.value[0].key;
  }
};

const fetchTurns = async (notFetch = true) => {
  http.post('/test_project/get_turns', {
    project_id: projectDetail.value.project_id,
  }).then((resp) => {
    // 将 turns 数组中的每个元素转换为一个对象，并添加一个 time 属性
    turns.value = resp.turns.map((turn_id, index) => ({
      turn_id,
      time: `Turn ${index + 1}`, // 这里可以根据实际需求设置时间格式
    }));
    if (turns.value.length > 0) {
      selectedTurnId.value = turns.value[turns.value.length - 1]?.turn_id;
    }

    if (turns.value.length > 0 && notFetch) {
      fetchTestInfo();
    }
  })
};

const fetchTestInfo = async () => {
  if (!window.location.hash.includes('/execution')) {
    clearInterval(interval);
    return;
  }
  await fetchTurns(false);
  if (!selectedPlanId.value) {
    testResults.value = [];
    return;
  }
  const response = await http.post('/test_project/get_test_info', {
    project_id: projectDetail.value.project_id,
    turn_id: String(selectedTurnId.value),
    plan_id: selectedPlanId.value, // 传递 plan_id 参数
    type: selectedType.value, // 传递 type 参数
  });
  progress.value = parseInt(response.process); // 使用 process 字段更新进度
  testResults.value = (response.result_list || []).reverse();
  console.log(testResults.value);
  logContent.value = response.log; // 假设 response 中有 log 字段

  // 更新状态文本
  statusText.value = response.status === 'completed' ? '已完成' : '进行中';
  if (response.status === 'completed') {
    clearInterval(interval);
  }
};

const startTest = async () => {
  const payload = {
    project_id: projectDetail.value.project_id,
  };
  http.post('/test_project/start_test', payload).then((resp) => {
    setTimeout(async () => {
      await fetchTurns();
      interval = setInterval(fetchTestInfo, 10000);
    }, 1000)
  }).catch((err) => {
    console.log(err);
    if (err.response.data.detail) {
      ElMessage.error(err.response.data.detail);
    }
  });
};

const pauseTest = async () => {
  const payload = {
    project_id: projectDetail.value.project_id,
  };
  http.post('/test_project/pause_test', payload).then((result) => {
    if (result.status === 'success') {
      ElMessage.success('测试已暂停');
      clearInterval(interval);
    } else {
      ElMessage.error('暂停失败')
    }
  }).finally(() => {
    ElMessage.error('暂停失败')
  });


}

const stopTest = async () => {
  const payload = {
    project_id: projectDetail.value.project_id,
  };
  await http.post('/test_project/stop_test', payload);
  clearInterval(interval);
};

const onSelect = (selectedKeys, info) => {
  selectedPlanId.value = selectedKeys[0];
  fetchTestInfo();
  console.log('selected', selectedKeys, info);
};

const onTurnChange = async () => {
  const response = await http.post('/test_project/get_test_info', {
    project_id: projectDetail.value.project_id,
    turn_id: String(selectedTurnId.value),
    plan_id: selectedPlanId.value, // 传递 plan_id 参数
    type: selectedType.value, // 传递 type 参数
  });
  progress.value = parseInt(response.process); // 使用 process 字段更新进度
  testResults.value = (response.result_list || []).reverse();
  console.log(testResults.value);
  logContent.value = response.log; // 假设 response 中有 log 字段

  // 更新状态文本
  statusText.value = response.status === 'completed' ? '已完成' : '进行中';
  if (response.status === 'completed') {
    clearInterval(interval);
  }
};

const onPlanChange = async () => {
  await fetchTestInfo();
};

const onTypeChange = async () => {
  await fetchPlanList(); // 重新获取 plan 列表
  await fetchTestInfo(); // 更新表格数据
};

const previewImage = (filePath) => {
  window.electron.ipcRenderer.send('getImage', filePath);
};

const exportResults = async () => {
  const response = await http.post('/test_project/export_results', { project_id: projectDetail.value.project_id, turn_id: selectedTurnId.value },);
  // const response = {};
  if (response.url || '/Users/luotianyou/CVAtest') {
    ElMessage.success(`结果文件已保存到${response.url || '/Users/luotianyou/CVAtest'}`)
    window.electron.ipcRenderer.send('show_path', response.url || '/Users/luotianyou/CVAtest');
  }
};

const router = useRouter();

const jumpToCheck = () => {
  localStorage.setItem('turn_id', selectedTurnId.value);
  localStorage.setItem('plan_id', selectedPlanId.value);
  localStorage.setItem('result_type', selectedType.value);
  router.push('/resultCheck');
}

let interval = null;

const handleWheel = (event) => {
  event.preventDefault();
  const delta = event.deltaY > 0 ? -0.1 : 0.1;
  scale.value += delta;
  scale.value = Math.min(Math.max(0.1, scale.value), 3); // 限制缩放范围
  if (previewImageRef.value) {
    previewImageRef.value.style.transform = `scale(${scale.value})`;
  }
};

let last = 0;

const refreshContinuously = () => {
  if (Date.now() - last < 1000) {
    ElMessage.error('刷新太频繁了, 请等一会')
    return;
  }
  last = Date.now();
  setTimeout(async () => {
    interval = setInterval(fetchTestInfo, 5000);
  }, 0)
};

const goToProject = () => {
  router.push('/project');
};
</script>

<style scoped>
@import './ExecutionMain.css';
</style>