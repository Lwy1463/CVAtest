<template>
  <div>
    <!-- 表头 -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
      <div style="display: flex; gap: 10px;">
        <a-select v-model:value="filter.car_function" placeholder="对应车机功能" style="width: 150px" allowClear>
          <a-select-option value="audio-video">音视频</a-select-option>
          <a-select-option value="navigation-travel">导航与出行</a-select-option>
          <a-select-option value="communication">通讯</a-select-option>
          <a-select-option value="vehicle-settings-info-query">车辆设置与信息查询</a-select-option>
          <a-select-option value="vehicle-control-command">车辆控制指令</a-select-option>
          <a-select-option value="ai-assistant">AI助手</a-select-option>
          <a-select-option value="security-privacy">安全与隐私</a-select-option>
        </a-select>
        <a-input v-model:value="filter.label" placeholder="标签" style="width: 150px" />
        <a-select v-model:value="filter.speaker" placeholder="发声人" style="width: 120px" @change="handleSpeakerChange" allowClear>
          <a-select-option value="male">男声</a-select-option>
          <a-select-option value="female">女声</a-select-option>
        </a-select>
        <a-select v-model:value="filter.language" placeholder="语种" style="width: 120px" allowClear>
          <a-select-option v-for="option in languageOptions" :key="option.value" :value="option.value">{{ option.label }}</a-select-option>
        </a-select>
      </div>
      <div style="display: flex; gap: 10px;">
        <a-button type="primary" @click="showCreateModal">新增多轮语料</a-button>
        <a-button type="primary" @click="batchDelete">批量删除</a-button>
      </div>
    </div>

    <!-- 表格 -->
    <a-table :columns="columns" :data-source="corpusList" :rowKey="record => record.corpus_id" :row-selection="rowSelection">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'index'">
          {{ record.index }}
        </template>
        <template v-else-if="column.key === 'operation'">
          <a-button type="link" @click="showEditModal(record)">编辑</a-button>
          <a-button type="link" style="color: red" @click="deleteCorpus(record.corpus_id)">删除</a-button>
        </template>
        <template v-else-if="column.key === 'car_function'">
          {{ getCarFunctionLabel(record.car_function) }}
        </template>
        <template v-else-if="column.key === 'speaker'">
          {{ getSpeakerLabel(record.speaker) }}
        </template>
        <template v-else-if="column.key === 'language'">
          {{ getLanguageLabel(record.speaker, record.language) }}
        </template>
      </template>
      <template #expandedRowRender="{ record }">
        <a-table :columns="subColumns" :data-source="record.corpusItems" row-key="aud_id">
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'index'">
              {{ record.index }}
            </template>
            <template v-else-if="column.key === 'audio_url'">
              {{ record.audio_url }}
            </template>
            <template v-else-if="column.key === 'speaker'">
              {{ getSpeakerLabel(record.speaker) }}
            </template>
            <template v-else-if="column.key === 'language'">
              {{ getLanguageLabel(record.speaker, record.language) }}
            </template>
            <template v-else-if="column.key === 'action'">
              <a-button type="link" style="color: #de8dcc" @click="playAudio(record)">试听</a-button>
            </template>
          </template>
        </a-table>
      </template>
    </a-table>

    <!-- 新增/编辑模态框 -->
    <a-modal
      :title="editMode ? '编辑语料' : '新增语料'"
      v-model:visible="modalVisible"
      @ok="handleOk"
      @cancel="handleCancel"
      width="80%"
    >
      <a-form :model="currentItem" layout="vertical">
        <a-row :gutter="[16, 16]">
          <a-col :span="12">
            <a-form-item label="测试类型">
              <a-select v-model:value="currentItem.test_type" disabled>
                <a-select-option value="speech-recognition">语音识别</a-select-option>
                <a-select-option value="intelligent-interaction">智能交互</a-select-option>
                <a-select-option value="wake-up-free">免唤醒</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="测试场景">
              <a-select v-model:value="currentItem.test_scenario" disabled>
                <a-select-option value="speech-recognition-interaction">语音识别交互</a-select-option>
                <a-select-option value="speech-recognition-ability">语音识别能力</a-select-option>
                <a-select-option value="single-command-interaction">单指令交互</a-select-option>
                <a-select-option value="continuous-dialogue-interaction">连续对话交互</a-select-option>
                <a-select-option value="multi-command-interaction">多指令交互</a-select-option>
                <a-select-option value="fuzzy-command-interaction">模糊指令交互</a-select-option>
                <a-select-option value="multi-topic-cross-execution">多话题交叉执行</a-select-option>
                <a-select-option value="wake-up-free">免唤醒</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="[16, 16]">
          <a-col :span="12">
            <a-form-item label="语料名称">
              <a-input v-model:value="currentItem.corpus_name" placeholder="请输入语料名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="对应车机功能">
              <a-select v-model:value="currentItem.car_function">
                <a-select-option value="audio-video">音视频</a-select-option>
                <a-select-option value="navigation-travel">导航与出行</a-select-option>
                <a-select-option value="communication">通讯</a-select-option>
                <a-select-option value="vehicle-settings-info-query">车辆设置与信息查询</a-select-option>
                <a-select-option value="vehicle-control-command">车辆控制指令</a-select-option>
                <a-select-option value="ai-assistant">AI助手</a-select-option>
                <a-select-option value="security-privacy">安全与隐私</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="[16, 16]">
          <a-col :span="12">
            <a-form-item label="标签">
              <a-input v-model:value="currentItem.label" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="发声人">
              <a-select v-model:value="currentItem.speaker" @change="handleSpeakerChange">
                <a-select-option value="male">男声</a-select-option>
                <a-select-option value="female">女声</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="[16, 16]">
          <a-col :span="12">
            <a-form-item label="语种">
              <a-select v-model:value="currentItem.language">
                <a-select-option v-for="option in languageOptions" :key="option.value" :value="option.value">{{ option.label }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="语料列表">
          <!-- 语料列表表头 -->
          <div class="table-header">
            <div class="table-cell" style="flex: 1;">序号</div> <!-- 新增序号列 -->
            <div class="table-cell" style="flex: 1;">语料文本</div>
            <div class="table-cell" style="flex: 1;">音频文件</div>
            <div class="table-cell" style="flex: 1;">音频时长</div>
            <div class="table-cell" style="flex: 1;">预期结果</div>
            <div class="table-cell" style="flex: 1;">操作</div>
          </div>
          <!-- 语料列表内容 -->
          <div class="table-content">
            <div v-for="(item, index) in currentItem.corpusItems" :key="item.index" class="table-row">
              <div class="table-cell" style="flex: 1;">
                <a-select v-model:value="item.index" :options="getIndexOptions(currentItem.corpusItems.length)" @change="handleIndexChange(item, index)" />
              </div>
              <div class="table-cell" style="flex: 1;">
                <a-input v-model:value="item.text" placeholder="语料文本" />
              </div>
              <div class="table-cell" style="flex: 1.25;">
                <el-upload ref="uploadRef" :auto-upload="false" :on-change="(file, fileList) => onBeforeUploadAudio(file, fileList, item)" accept=".mp3,.wav" :limit="1" :file-list="audioFileList[index]">
                  <template #trigger>
                    <el-button>上传文件</el-button>
                  </template>
                </el-upload>
              </div>
              <div class="table-cell" style="flex: 1;">
                <a-input v-model:value="item.audio_duration" placeholder="音频时长" disabled />
              </div>
              <div class="table-cell" style="flex: 1;">
                <a-input v-model:value="item.expect_result" placeholder="预期结果" />
              </div>
              <div class="table-cell" style="flex: 1;">
                <a-button type="primary" @click="addCorpusItem(index)">+</a-button>
                <a-button class="ml-[10px]" type="primary" @click="removeCorpusItem(index)" :disabled="currentItem.corpusItems.length === 1">-</a-button>
              </div>
            </div>
          </div>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { message } from 'ant-design-vue';
import { http } from '@renderer/http';
import type { UploadProps } from 'element-plus';
import { ElMessage, ElMessageBox } from 'element-plus';

const columns = [
  { title: '语料名称', dataIndex: 'corpus_name', key: 'corpus_name'},
  { title: '对应车机功能', dataIndex: 'car_function', key: 'car_function' },
  { title: '标签', dataIndex: 'label', key: 'label' },
  { title: '发声人', dataIndex: 'speaker', key: 'speaker' },
  { title: '语种', dataIndex: 'language', key: 'language' },
  { title: '操作', key: 'operation' }
];

const subColumns = [
  { title: '语料文本', dataIndex: 'text', key: 'text' },
  { title: '音频文件', dataIndex: 'audio_url', key: 'audio_url' },
  { title: '音频时长', dataIndex: 'audio_duration', key: 'audio_duration' },
  { title: '预期结果', dataIndex: 'expect_result', key: 'expect_result' },
  { title: '操作', key: 'action' }
];

const corpusList = ref([
]);
const modalVisible = ref(false);
const editMode = ref(false);
const currentItem = ref({
  corpus_id: '',
  corpus_name: '', // 新增 corpus_name 字段
  test_type: 'intelligent-interaction',
  test_scenario: 'continuous-dialogue-interaction',
  car_function: 'audio-video',
  label: '',
  speaker: 'male',
  language: '1',
  corpusItems: [] as any[]
});
const audioFileList = ref<any[]>([]);

const filter = reactive({
  car_function: undefined,
  label: '',
  speaker: undefined,
  language: undefined,
});

const testScenarioOptions = ref([]);
const languageOptions = ref([]);

const selectedRowKeys = ref<string[]>([]);

const rowSelection = {
    onChange: (selectedRowKeysValue, selectedRows) => {
        selectedRowKeys.value = selectedRowKeysValue;
    },
    getCheckboxProps: (record) => ({
        props: {
            id: record.corpus_id,
        },
    }),
};

// 获取列表数据
const fetchCorpusList = async () => {
  try {
    const res = await http.post('/multi-corpus/list', { ...filter });
    corpusList.value = res.data;
  } catch (error) {
    message.error('获取列表失败');
  }
};

// 编辑行
const showEditModal = (item) => {
  editMode.value = true;
  currentItem.value = {
    ...item,
    corpus_name: item.corpus_name || '', // 初始化 corpus_name 字段
    corpusItems: item.corpusItems.map((corpusItem, index) => ({ ...corpusItem, index: index + 1 }))
  };
  // 设置默认发声人和语种
  currentItem.value.speaker = 'male';
  currentItem.value.language = '1';
  currentItem.value.corpus_id = item.corpus_id;
  handleSpeakerChange('male'); // 更新语种选项
  modalVisible.value = true;

  // 为每一行的音频文件生成 audioFileList 条目
  audioFileList.value = (currentItem.value.corpusItems || []).map(corpusItem => {
    return [{
      name: corpusItem.audio_url,
      url: corpusItem.audio_url
    }]
  });
};

// 新增多轮语料
const showCreateModal = () => {
  editMode.value = false;
  currentItem.value = {
    corpus_id: '',
    corpus_name: '', // 初始化 corpus_name 字段
    test_type: 'intelligent-interaction',
    test_scenario: 'continuous-dialogue-interaction',
    car_function: 'audio-video',
    label: '',
    speaker: 'male',
    language: '1',
    corpusItems: [{ text: '', audio_url: '', audio_duration: '', expect_result: '', aud_id: '', index: 1 }]
  };
  handleSpeakerChange('male'); // 更新语种选项
  modalVisible.value = true;
  audioFileList.value = []; // 清空音频文件列表
};

// 上传音频前处理
const onBeforeUploadAudio = async (file, fileList, item) => {
  console.log(file);
  const formData = new FormData();
  formData.append('info', JSON.stringify({ category: 'audio', text: item.text }));
  formData.append('file', file.raw);
  try {
    const response = await http.post(`/corpus/upload_audio_file`, formData);

    if (response) {
      item.audio_url = file.name;
      item.pinyin = response.pinyin;
      item.audio_duration = response.audio_duration;
      item.aud_id = response.aud_id;
    }
  } catch (error) {
    console.error("Upload failed: ", error);
  }
};

// 模态框确认
const handleOk = async () => {
  if (currentItem.value.corpusItems.some(item => !item.text || !item.audio_url)) {
    message.warning('请填写完整语料信息');
    return;
  }

  // 确保 index 是顺序排列的
  currentItem.value.corpusItems.sort((a, b) => a.index - b.index);
  currentItem.value.corpusItems.forEach((item, index) => {
    item.index = index + 1;
  });

  if (editMode.value) {
    // 更新语料
    try {
      await http.post('/multi-corpus/update', {
        ...currentItem.value,
        corpus_name: currentItem.value.corpus_name // 包含 corpus_name 字段
      });
      // 更新corpusList中的数据
      const index = corpusList.value.findIndex(item => item.corpus_id === currentItem.value.corpus_id);
      if (index !== -1) {
        corpusList.value[index] = { ...currentItem.value };
      }
      message.success('更新成功');
      fetchCorpusList();
    } catch (error) {
      message.error('更新失败');
    }
  } else {
    // 新增语料
    try {
      await http.post('/multi-corpus/create', {
        ...currentItem.value,
        corpus_name: currentItem.value.corpus_name // 包含 corpus_name 字段
      });
      // 将新增的数据添加到corpusList中
      corpusList.value.push(currentItem.value);
      message.success('新增成功');
      fetchCorpusList();
    } catch (error) {
      message.error('新增失败');
    }
  }
  modalVisible.value = false;
};

// 模态框取消
const handleCancel = () => {
  modalVisible.value = false;
};

// 处理测试类型变化
const handleTestTypeChange = (value) => {
  testScenarioOptions.value = getTestScenarioOptions(value);
  if (testScenarioOptions.value.length > 0) {
    filter.test_scenario = testScenarioOptions.value[0].value;
  }
};

// 处理发声人变化
const handleSpeakerChange = (value) => {
  languageOptions.value = getLanguageOptions(value);
  if (languageOptions.value.length > 0) {
    filter.language = languageOptions.value[0].value;
  }
};

// 获取测试场景选项
const getTestScenarioOptions = (test_type) => {
  const options = {
    'speech-recognition': [
      { value: 'speech-recognition-interaction', label: '语音识别交互' },
      { value: 'speech-recognition-ability', label: '语音识别能力' },
    ],
    'intelligent-interaction': [
      { value: 'single-command-interaction', label: '单指令交互' },
      { value: 'continuous-dialogue-interaction', label: '连续对话交互' },
      { value: 'multi-command-interaction', label: '多指令交互' },
      { value: 'fuzzy-command-interaction', label: '模糊指令交互' },
      { value: 'multi-topic-cross-execution', label: '多话题交叉执行' },
    ],
    'wake-up-free': [
      { value: 'wake-up-free', label: '免唤醒' },
    ],
  };
  return options[test_type] || [];
};

// 获取语种选项
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

// 获取对应车机功能的中文标签
const getCarFunctionLabel = (car_function) => {
  const carFunctionMap = {
    'audio-video': '音视频',
    'navigation-travel': '导航与出行',
    'communication': '通讯',
    'vehicle-settings-info-query': '车辆设置与信息查询',
    'vehicle-control-command': '车辆控制指令',
    'ai-assistant': 'AI助手',
    'security-privacy': '安全与隐私'
  };
  return carFunctionMap[car_function] || car_function;
};

// 获取发声人的中文标签
const getSpeakerLabel = (speaker) => {
  const speakerMap = {
    'male': '男声',
    'female': '女声'
  };
  return speakerMap[speaker] || speaker;
};

// 获取语种的中文标签
const getLanguageLabel = (speaker, language) => {
  const languageOptions = getLanguageOptions(speaker);
  const languageOption = languageOptions.find(option => option.value === language);
  return languageOption ? languageOption.label : language;
};

// 新增语料项
const addCorpusItem = (index) => {
  currentItem.value.corpusItems.splice(index + 1, 0, {
    text: '',
    audio_url: '',
    audio_duration: '',
    expect_result: '',
    aud_id: '',
    index: currentItem.value.corpusItems.length + 1
  });
};

// 删除语料项
const removeCorpusItem = (index) => {
  if (currentItem.value.corpusItems.length > 1) {
    currentItem.value.corpusItems.splice(index, 1);
    currentItem.value.corpusItems.forEach((item, index) => {
      item.index = index + 1;
    });
  } else {
    message.warning('不能删除第一行');
  }
};

// 监听 filter 变化并触发查询
watch(() => [filter.test_type, filter.test_scenario, filter.car_function, filter.label, filter.speaker, filter.language], () => {
  fetchCorpusList();
});

// 组件挂载时获取列表数据
fetchCorpusList();

// 播放音频
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

// 删除单个语料
const deleteCorpus = async (corpus_id) => {
  ElMessageBox.confirm('确定要删除该语料吗？', '确认删除', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await http.post('/multi-corpus/batchDelete', { corpus_ids: [corpus_id] });
      // 更新corpusList中的数据
      corpusList.value = corpusList.value.filter(item => item.corpus_id !== corpus_id);
      message.success('删除成功');
    } catch (error) {
      message.error('删除失败');
    }
  }).catch(() => {
    // 用户取消删除
  });
};

// 批量删除语料
const batchDelete = async () => {
  if (selectedRowKeys.value.length === 0) {
    ElMessage.warning('请选择要删除的语料');
    return;
  }

  ElMessageBox.confirm('确定要删除选中的语料吗？', '确认删除', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await http.post('/multi-corpus/batchDelete', { corpus_ids: selectedRowKeys.value });
      // 更新corpusList中的数据
      corpusList.value = corpusList.value.filter(item => !selectedRowKeys.value.includes(item.corpus_id));
      selectedRowKeys.value = [];
      message.success('批量删除成功');
    } catch (error) {
      message.error('批量删除失败');
    }
  }).catch(() => {
    // 用户取消删除
  });
};

// 获取 index 选项
const getIndexOptions = (length) => {
  return Array.from({ length }, (_, i) => ({ value: i + 1, label: i + 1 }));
};

// 处理 index 变化
const handleIndexChange = (item, index) => {
  const newIndex = item.index;
  const oldIndex = index + 1;

  if (newIndex === oldIndex) return;

  const movedItem = currentItem.value.corpusItems.splice(index, 1)[0];
  currentItem.value.corpusItems.splice(newIndex - 1, 0, movedItem);

  currentItem.value.corpusItems.forEach((item, index) => {
    item.index = index + 1;
  });
};
</script>

<style scoped>
.container {
  padding: 20px;
}

.card {
  width: 100%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.table-header, .table-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.table-cell {
  flex: 1;
  padding: 0 10px;
  text-align: center;
}

.table-cell > div {
  display: flex;
}

.table-header .table-cell {
  font-weight: bold;
}

.table-content {
  max-height: calc(100vh - 24rem);
  overflow-y: auto;
}

:deep(.el-upload__input) {
    display: none !important;
}

:deep(.el-upload-list__item-name) {
  min-width: 80px;
  max-width: 80px;
}

:deep(.el-upload-list__item .el-icon--close) {
  right: -1rem !important;

}
</style>