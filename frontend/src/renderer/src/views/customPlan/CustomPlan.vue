<template>
  <!-- 面包屑导航 -->
  <a-breadcrumb style="margin: 1rem;">
    <a-breadcrumb-item>
      <a @click="goToProject">项目管理</a>
    </a-breadcrumb-item>
    <a-breadcrumb-item>方案配置</a-breadcrumb-item>
  </a-breadcrumb>
  <div style="display: flex; height: calc(100vh - 10rem);">
    <!-- 测评方案 -->
    <div style="flex: 1; padding: 5px; height: 100%;">
      <TestPlan :project_id="projectDetail.project_id" :selectedKeys="selectedKeys" @planChange="handlePlanChange" />
    </div>

    <!-- 选择播放配置 -->
    <div style="flex: 1; padding: 5px; height: 100%;">
      <PlaybackConfig v-model="selectedPlayConfigId" :project_id="projectDetail.project_id"
        @rouseSceneSelected="onRouseSceneSelected" />
    </div>

    <!-- 选择语料和方案内容 -->
    <div style="flex: 2; padding: 5px; height: 100%;">
      <a-card title="选择语料和方案内容" style="height: 100%; overflow: auto;">
        <!-- 选择语料 -->
        <div>
          <a-button type="primary" @click="showCorpusModal" style="margin-bottom: 20px;">配置语料</a-button>
        </div>

        <!-- 方案内容 -->
        <div style="margin-top: 40px;">
          <h3>唤醒语料</h3>
          <a-table :columns="rouseCorpusColumns" :data-source="selectedRouseCorpus" row-key="corpus_id" :pagination="false">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'audio_url'">
                {{ record.audio_url }}
              </template>
            </template>
          </a-table>

          <h3 style="margin-top: 20px;">测试语料</h3>
          <a-table :columns="columns" :data-source="selectedTestCorpusList" row-key="corpus_id"
            :pagination="{ pageSize: 5 }">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'audio_url'">
                {{ record.audio_url }}
              </template>
            </template>
            <template #expandedRowRender="{ record }" :rowExpandable="record.type === 'multi'">
              <a-table v-if="record.type === 'multi'" :columns="subColumns" :data-source="record.corpusItems"
                row-key="aud_id" :pagination="false">
              </a-table>
            </template>
          </a-table>
        </div>
      </a-card>
    </div>

    <!-- 配置语料弹窗 -->
    <a-modal title="配置语料" :visible="corpusModalVisible" @ok="handleCorpusModalOk" @cancel="handleCorpusModalCancel"
      width="70%">
      <a-tabs default-active-key="1">
        <a-tab-pane key="1" tab="唤醒语料">
          <a-transfer show-search :filter-option="filterOption" :locale="{
            searchPlaceholder: '请输入 文本/标签/发声人/语种 '
          }" :dataSource="rouseCorpusList.data" :list-style="{
            width: '50%',
            height: '100%',
            'max-height': '70vh',
            'overflow': 'auto'
          }" :titles="['可用语料', '已选语料']" :targetKeys="rouseCorpusKey || []"
            :render="item => `${item.text} - 时长: ${item.audio_duration || 0}s - 发声人: ${item.speaker} - 语种: ${item.language} - 标签: ${item.label}`"
            @change="handleRouseTransferChange" />
        </a-tab-pane>
        <a-tab-pane key="2" tab="测试语料">
          <a-transfer show-search :filter-option="filterOption" :locale="{
            searchPlaceholder: '请输入 文本/标签/发声人/语种 '
          }" :dataSource="testCorpusList.data" :list-style="{
            width: '50%',
            height: '100%',
            'max-height': '70vh',
            'overflow': 'auto'
          }" :titles="['可用语料', '已选语料']" :targetKeys="testCorpusKeys" :render="renderItem"
            @change="handleTransferChange" />
        </a-tab-pane>
      </a-tabs>
    </a-modal>

    <!-- 固定底部栏 -->
    <div
      style="position: fixed; bottom: 0; left: 0; width: 100%; background-color: white; padding: 10px; border-top: 1px solid #e8e8e8; display: flex; justify-content: flex-end;">
      <a-button type="primary" @click="handleReturn">返回</a-button>
      <a-button type="primary" @click="handleSave" style="margin-left: 10px;">保存</a-button>
      <a-button type="primary" @click="handleSaveAndExecute" style="margin-left: 10px;">保存并执行</a-button>
    </div>
  </div>
</template>

<script setup lang="tsx">
import { ref, onMounted, watch, computed } from 'vue';
import { http } from '@renderer/http';
import { useProjectStore } from '@renderer/stores/useProject';
import { storeToRefs } from 'pinia';
import TestPlan from './TestPlan.vue'; // 引入 TestPlan 组件
import PlaybackConfig from './PlaybackConfig.vue'; // 引入 PlaybackConfig 组件
import { ElMessage, ElMessageBox } from 'element-plus'; // 引入 ElMessageBox
import { useRouter } from 'vue-router'; // 引入 useRouter

const router = useRouter(); // 初始化 router

const female_voice_map = {
  '1': '女声1',
  '2': '女声2',
  '3': '女声3',
  '4': '女声4',
  '5': '女声5',
  '6': '女声6',
  '7': '女声7',
  '8': '童声',
  '9': '四川话',
  '10': '粤语',
  '11': '东北话',
};

const renderItem = (item) => {
  return <span>

    <div style="border: 1px solid skyblue; display: inline-block; font-size: 12px; border-radius: 8px; padding: 2px;margin-right: 0.3rem; opacity: 0.9;">{item.type === 'multi' ? '多轮对话语料': '普通语料'}</div>
    {`${item.text || item.corpus_name || item.corpus_id} - 时长: ${item.audio_duration || 0}s - 发声人: ${item.speaker} - 语种: ${item.language} - 标签: ${item.label}`}
  </span>
}
const male_voice_map = {
  '1': '男声1',
  '2': '男声2',
  '3': '男声3',
  '4': '男声4',
  '5': '男声5',
  '6': '男声6',
  '7': '童声',
  '8': '东北话',
  '9': '天津话',
};

const projectStore = useProjectStore();
const { projectDetail } = storeToRefs(projectStore);

const selectedKeys = ref<string[]>([]);
const selectedPlanId = ref<string | null>('');
const selectedPlayConfigId = ref<string | null>(null); // 新增的 selectedPlayConfigId

const treeData = ref([
  {
    title: '测试语料',
    key: 'test-corpus',
    children: [],
  },
  {
    title: '唤醒语料',
    key: 'rouse-corpus',
    children: [],
  },
]);

const checkedKeys = ref([[], []]);
const rouseCorpusKey = ref([]);
const testCorpusKeys = ref([]);

const testCorpusList = ref([]);
const rouseCorpusList = ref([]);

const selectedRouseCorpus = ref([]);
const selectedTestCorpusList = ref([]);
const isRouseRef = ref(true)

const filterOption = (inputValue: string, option: any) => {
  return (option.label || '').indexOf(inputValue) > -1 || (option.text || '').indexOf(inputValue) > -1 || option.language.indexOf(inputValue) > -1 || option.speaker?.indexOf(inputValue) > -1;
};

const extractThirdLevelId = (key) => {
  if (typeof key !== 'string') {
    return null;
  }
  const parts = key.split('-');
  return parts.length > 2 ? parts[2] : null;
};

const getIndexOptions = (length) => {
  return Array.from({ length }, (_, i) => ({ value: i + 1, label: i + 1 }));
};

const columns = [
  {
    title: '序号',
    dataIndex: 'index',
    key: 'index',
    customRender: ({ text, record, index }) => (
      <a-select
        value={record.index}
        onChange={(value) => handleIndexChange(record, value)}
        style="width: 100px"
        options={getIndexOptions(selectedTestCorpusList.value.length)}
      >
      </a-select>
    ),
  },
  { title: '语料id', dataIndex: 'corpus_id' },
  { title: '语料文本', dataIndex: 'text' },
  {
    title: '音频文件名',
    dataIndex: 'audio_url',
    key: 'audio_url',
  },
  { title: '音频时长(s)', dataIndex: 'audio_duration' },
];

const subColumns = [
  { title: '语料文本', dataIndex: 'text', key: 'text' },
  { title: '音频文件', dataIndex: 'audio_url', key: 'audio_url' },
  { title: '音频时长', dataIndex: 'audio_duration', key: 'audio_duration' },
  { title: '预期结果', dataIndex: 'expect_result', key: 'expect_result' },
  { title: '操作', key: 'action' }
];

const isMounted = ref(false);

const corpusModalVisible = ref(false); // 控制配置语料弹窗显示隐藏

const rouseCorpusColumns = [
  { title: '音频文件名', dataIndex: 'audio_url', key: 'audio_url' },
  { title: '语料id', dataIndex: 'corpus_id' },
  { title: '语料文本', dataIndex: 'text' },
  {
    title: '音频文件名',
    dataIndex: 'audio_url',
    key: 'audio_url',
  },
  { title: '音频时长(s)', dataIndex: 'audio_duration' },
];

const rouseCorpusData = computed(() => {
  if (Array.isArray(selectedRouseCorpus.value)) {
    return selectedRouseCorpus.value;
  } else if (selectedRouseCorpus.value) {
    return [selectedRouseCorpus.value];
  } else {
    return [];
  }
});

onMounted(async () => {
  if (projectDetail.value.project_id) {
    // 从这里查询接口获取treeData的初始值
    await fetchTreeData();
    await getPlanDetail(selectedPlanId.value);
    isMounted.value = true;
  }
});

const fetchTreeData = async () => {
  // 获取测试语料列表
  testCorpusList.value = await http.post('/corpus/get_test_corpus_list', {});

  // 获取唤醒语料列表
  rouseCorpusList.value = await http.post('/corpus/get_rouse_corpus_list', {});

  // 获取多轮语料列表
  const multiCorpusList = await http.post('/multi-corpus/list', { label: "" });

  multiCorpusList.data = multiCorpusList.data.map(x => {
    x.type = "multi";
    return x;
  })
  // 将多轮语料列表拼接到 testCorpusList 中
  testCorpusList.value.data = testCorpusList.value.data.concat(multiCorpusList.data);

  // 处理测试语料列表
  treeData.value[0].children = testCorpusList.value.data.map(item => {
    item.key = `test-corpus-${item.corpus_id}`;
    if (typeof item.speaker === 'string') {
      item.speaker = item.speaker === 'male' ? '男声' : '女声';
      item.language = item.speaker === '男声' ? male_voice_map[item.language] || '- -' : female_voice_map[item.language] || '- -';
    }
    return {
      title: item.text,
      key: `test-corpus-${item.corpus_id}`,
    }
  });

  // 处理唤醒语料列表
  treeData.value[1].children = rouseCorpusList.value.data.map(item => {
    if (typeof item.speaker === 'string') {
      item.speaker = item.speaker === 'male' ? '男声' : '女声';
      item.language = item.speaker === '男声' ? male_voice_map[item.language] || '- -' : female_voice_map[item.language] || '- -';
    }
    item.key = `rouse-corpus-${item.corpus_id}`;
    item.label = `${item.text || item.corpus_id} - 时长: ${item.audio_duration || '0'}s - 发声人: ${item.speaker} - 语种: ${item.language} - 标签: ${item.label}`
    return {
      title: item.text,
      key: `rouse-corpus-${item.corpus_id}`,
      label: item.label,
    }
  });
};

const getLanguageOptions = (speaker) => {
  if (speaker === 'male') {
    return [
      { value: '1', label: '男声1' },
      { value: '2', label: '男声2' },
      { value: '3', label: '男声3' },
      { value: '4', label: '男声4' },
      { value: '5', label: '男声5' },
      { value: '6', label: '男声6' },
      { value: '7', label: '童声' },
      { value: '8', label: '东北话' },
      { value: '9', label: '天津话' },
    ];
  } else if (speaker === 'female') {
    return [
      { value: '1', label: '女声1' },
      { value: '2', label: '女声2' },
      { value: '3', label: '女声3' },
      { value: '4', label: '女声4' },
      { value: '5', label: '女声5' },
      { value: '6', label: '女声6' },
      { value: '7', label: '女声7' },
      { value: '8', label: '童声' },
      { value: '9', label: '四川话' },
      { value: '10', label: '粤语' },
      { value: '11', label: '东北话' },
    ];
  } else {
    return [];
  }
};

const handlePlanChange = async (planId: string) => {
  selectedPlanId.value = planId;
  if (isMounted.value === true) {
    // 调用 getPlanDetail 方法
    await getPlanDetail(planId);
  } else {
    // donoting
  }
};

const getPlanDetail = async (planId: string) => {
  const payload = {
    project_id: projectDetail.value.project_id,
    plan_id: planId,
  };
  const result = await http.post('/test_project/get_plan_detail', payload);
  const response = await http.post('/play_config/get_play_config_list', {});
  const rouseConfigs = response.data.filter(config => config.type === 'rouse');
  const interactionConfigs = response.data.filter(config => config.type === 'interaction');

  testCorpusKeys.value = [...(result.testCorpusList || []).map(id => `test-corpus-${id}`)];

  selectedTestCorpusList.value = (testCorpusList.value.data || []).filter(item => result.testCorpusList.includes(item.corpus_id)).map((item, index) => ({
    ...item,
    index: index + 1, // 初始化 index 字段
  }));

  // 更新 selectedPlayConfigId
  selectedPlayConfigId.value = result.play_config_id;

  // 根据选中的播放配置类型设置
  const selectedPlayConfig = treeData.value.flatMap(category => category.children).find(config => config.key.split('-')[1] === result.play_config_id);

  const isRouse = rouseConfigs.some(x => x.play_config_id === result.play_config_id)
  console.log(isRouse)
  if (isRouse) {
    rouseCorpusKey.value = result.rouseCorpusList.map(id => `rouse-corpus-${id}`);
    selectedRouseCorpus.value = [...(rouseCorpusList.value.data || []).filter(item => result.rouseCorpusList.includes(item.corpus_id))];

  } else {
    rouseCorpusKey.value = result.rouseCorpusList.length > 0 ? [`rouse-corpus-${result.rouseCorpusList[0]}`] : [];
    selectedRouseCorpus.value = [(rouseCorpusList.value.data || []).find(item => item.corpus_id === result.rouseCorpusList[0])];
  }
  console.log(selectedRouseCorpus.value);
};

const onRouseSceneSelected = (isRouseScene: boolean, clean = true, selectedData) => {
  console.log(clean, selectedData)
  if (isRouseScene) {
    isRouseRef.value = 'a-transfer'; // 切换为多选
  } else {
    isRouseRef.value = 'a-radio-group'; // 切换为单选
  }
};

// 配置语料弹窗相关逻辑
const showCorpusModal = () => {
  corpusModalVisible.value = true;
};

const handleCorpusModalOk = () => {
  corpusModalVisible.value = false;
  selectedRouseCorpus.value = rouseCorpusList.value.data.filter(item => (rouseCorpusKey.value || []).includes(`rouse-corpus-${item.corpus_id}`));
  selectedTestCorpusList.value = testCorpusList.value.data.filter(item => (testCorpusKeys.value || []).includes(`test-corpus-${item.corpus_id}`)).map((item, index) => ({
    ...item,
    index: index + 1, // 初始化 index 字段
  }));
};

const handleCorpusModalCancel = () => {
  corpusModalVisible.value = false;
};

const handleTransferChange = (nextTargetKeys) => {
  testCorpusKeys.value = nextTargetKeys;
};

const handleRouseTransferChange = (nextTargetKeys) => {
  rouseCorpusKey.value = nextTargetKeys;
};

const handleSave = async () => {
  if (!selectedPlanId.value) {
    ElMessageBox.alert('请选择或新建方案', '提示', {
      confirmButtonText: '确定',
    });
    return;
  }

  if (!selectedPlayConfigId.value) {
    ElMessageBox.alert('请选择或新建播放配置', '提示', {
      confirmButtonText: '确定',
    });
    return;
  }

  const new_testCorpusList = selectedTestCorpusList.value.map(x => x.corpus_id);
  const new_rouseCorpusList = rouseCorpusData.value.map(x => x.corpus_id);

  const payload = {
    project_id: projectDetail.value.project_id,
    plan_id: selectedPlanId.value,
    testCorpusList: new_testCorpusList,
    rouseCorpusList: new_rouseCorpusList,
    play_config_id: selectedPlayConfigId.value, // 获取选中的播放配置ID
  };
  const res = await http.post('/test_project/save_plan_detail', payload);
  if (res.status === 'success') {
    ElMessage.success('保存成功');
  } else {
    ElMessage.error('保存失败');
  }
};

const handleSaveAndExecute = async () => {
  await handleSave();

  // 弹窗提示用户是否前往项目执行页面
  ElMessageBox.confirm('保存成功，是否前往项目执行页面？', '提示', {
    confirmButtonText: '是',
    cancelButtonText: '否',
    type: 'info',
  }).then(() => {
    // 用户选择“是”，导航到项目执行页面
    router.push('/execution');
  }).catch(() => {
    // 用户选择“否”，不做任何操作
  });
};

const goToProject = () => {
  router.push('/project');
};

const playAudio = (record) => {
  const audioPath = record.audio_url;
  if (!audioPath) {
    ElMessage.warning('音频路径不存在');
    return;
  }
  const newPath = audioPath.replaceAll('\\', '/').split('/backend')?.[1];
  const audio = new Audio(newPath);
  audio.play();
};

const handleIndexChange = (item, newIndex) => {
  const oldIndex = item.index;

  if (newIndex === oldIndex) return;

  // 找到要移动的项目
  const movedItem = selectedTestCorpusList.value.find(i => i.index === oldIndex);
  if (!movedItem) return;

  // 从原位置移除
  selectedTestCorpusList.value = selectedTestCorpusList.value.filter(i => i.index !== oldIndex);

  // 插入到新位置
  selectedTestCorpusList.value.splice(newIndex - 1, 0, { ...movedItem, index: newIndex });

  // 更新所有项目的 index
  selectedTestCorpusList.value.forEach((item, index) => {
    item.index = index + 1;
  });
};

const handleReturn = () => {
  router.push('/project');
}

</script>

<style scoped>
/* Add your custom styles here */
h3 {
  margin-top: 20px;
}
</style>