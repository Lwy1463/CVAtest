<template>
    <div style="margin: 20px;">
        <a-page-header title="语料管理" />
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <a-input-search v-model:value="searchText" placeholder="请输入语料文本" style="width: 200px"
                @search="fetchCorpusList" />
            <div class="flex flex-end gap-[1rem]">
                <a-button type="primary" @click="showCreateModal"> 新增语料 </a-button>
                <a-button type="primary" @click="showImportModal">从文件导入</a-button>
                <a-button type="primary" @click="batchDeleteCorpus">批量删除</a-button>
                <a-button type="primary" @click="showSynthesizeModal">合成</a-button>
            </div>
        </div>

        <!-- 新增的搜索过滤项 -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div style="display: flex; gap: 10px;">
                <a-select v-model:value="filter.test_type" placeholder="测试类型" style="width: 150px"
                    @change="handleTestTypeChange" allowClear>
                    <a-select-option value="speech-recognition">语音识别</a-select-option>
                    <a-select-option value="intelligent-interaction">智能交互</a-select-option>
                    <a-select-option value="wake-up-free">免唤醒</a-select-option>
                </a-select>
                <a-select v-model:value="filter.test_scenario" placeholder="测试场景" style="width: 150px" allowClear>
                    <a-select-option v-for="option in testScenarioOptions" :key="option.value" :value="option.value">{{
                        option.label }}</a-select-option>
                </a-select>
                <a-select v-model:value="filter.speaker" placeholder="发声人" style="width: 120px"
                    @change="handleSpeakerChange" allowClear>
                    <a-select-option value="male">男声</a-select-option>
                    <a-select-option value="female">女声</a-select-option>
                </a-select>
                <a-select v-model:value="filter.language" placeholder="语种" style="width: 120px" allowClear>
                    <a-select-option v-for="option in languageOptions" :key="option.value" :value="option.value">{{
                        option.label }}</a-select-option>
                </a-select>
                <a-select v-model:value="filter.car_function" placeholder="对应车机功能" style="width: 150px" allowClear>
                    <a-select-option value="audio-video">音视频</a-select-option>
                    <a-select-option value="navigation-travel">导航与出行</a-select-option>
                    <a-select-option value="communication">通讯</a-select-option>
                    <a-select-option value="vehicle-settings-info-query">车辆设置与信息查询</a-select-option>
                    <a-select-option value="vehicle-control-command">车辆控制指令</a-select-option>
                    <a-select-option value="ai-assistant">AI助手</a-select-option>
                    <a-select-option value="security-privacy">安全与隐私</a-select-option>
                </a-select>
            </div>
            <a-button type="primary" @click="fetchCorpusList">搜索</a-button>
        </div>

        <a-table :columns="columns" :dataSource="corpusList" :rowKey="record => record.corpus_id"
            :pagination="paginationConfig" :scroll="{ y: table_height }" :rowSelection="rowSelection">
            <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'action'">
                    <a-button type="link" style="color: #de8dcc" @click="showEditModal(record)">编辑</a-button>
                    <a-button type="link" style="color: #de8dcc" @click="deleteCorpus(record.corpus_id)">删除</a-button>
                    <a-button type="link" style="color: #de8dcc" @click="showUploadModal(record)">上传</a-button>
                    <a-button type="link" style="color: #de8dcc" @click="showGeneralizeModal(record)">泛化</a-button>
                    <a-button type="link" style="color: #de8dcc" @click="playAudio(record)">试听</a-button>
                    <a-button type="link" style="color: #de8dcc" @click="showRecordModal(record)">录音</a-button> <!-- 新增录音按钮 -->
                </template>
                <template v-else-if="column.key === 'audio'">
                    {{ record.audio_url }}
                </template>
                <template v-else-if="column.key === 'test_scenario'">
                    {{ getTestScenarioTextForTable(record.test_type, record.test_scenario) }}
                </template>
                <template v-else-if="column.key === 'evaluation_metric'">
                    {{ getEvaluationMetricText(record.evaluation_metric) }}
                </template>
                <template v-else-if="column.key === 'speaker'">
                    {{ getSpeakerText(record.speaker) }}
                </template>
                <template v-else-if="column.key === 'language'">
                    {{ getLanguageTextForTable(record.language, record.speaker) }}
                </template>
                <template v-else-if="column.key === 'label'">
                    {{ record.label }}
                </template>
                <template v-else-if="column.key === 'car_function'">
                    {{ getCarFunctionText(record.car_function) }}
                </template>
            </template>
        </a-table>

        <!-- 新增语料模态框 -->
        <a-modal title="新增语料" v-model:visible="createModalVisible" @ok="createCorpus" @cancel="handleCancel" okText="确定"
            cancelText="取消" width="60%">
            <a-form ref="createForm" :model="createFormData" :rules="rules">
                <div class="modal-form-grid">
                    <a-form-item label="语料文本" name="text">
                        <a-input v-model:value="createFormData.text" />
                    </a-form-item>
                    <a-form-item label="测试类型" name="test_type">
                        <a-select v-model:value="createFormData.test_type" @change="handleCreateTestTypeChange">
                            <a-select-option value="speech-recognition">语音识别</a-select-option>
                            <a-select-option value="intelligent-interaction">智能交互</a-select-option>
                            <a-select-option value="wake-up-free">免唤醒</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="测试场景" name="test_scenario">
                        <a-select v-model:value="createFormData.test_scenario">
                            <a-select-option v-for="option in createTestScenarioOptions" :key="option.value"
                                :value="option.value">{{ option.label }}</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="发声人" name="speaker">
                        <a-select v-model:value="createFormData.speaker">
                            <a-select-option value="male">男声</a-select-option>
                            <a-select-option value="female">女声</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="语种" name="language">
                        <a-select v-model:value="createFormData.language" v-if="createFormData.speaker === 'female'">
                            <a-select-option value="1">女声1</a-select-option>
                            <a-select-option value="2">女声2</a-select-option>
                            <a-select-option value="3">女声3</a-select-option>
                            <a-select-option value="4">女声4</a-select-option>
                            <a-select-option value="5">女声5</a-select-option>
                            <a-select-option value="6">女声6</a-select-option>
                            <a-select-option value="7">女声7</a-select-option>
                            <a-select-option value="8">童声</a-select-option>
                            <a-select-option value="9">四川话</a-select-option>
                            <a-select-option value="10">粤语</a-select-option>
                            <a-select-option value="11">东北话</a-select-option>
                        </a-select>
                        <a-select v-model:value="createFormData.language" v-if="createFormData.speaker === 'male'">
                            <a-select-option value="1">男声1</a-select-option>
                            <a-select-option value="2">男声2</a-select-option>
                            <a-select-option value="3">男声3</a-select-option>
                            <a-select-option value="4">男声4</a-select-option>
                            <a-select-option value="5">男声5</a-select-option>
                            <a-select-option value="6">男声6</a-select-option>
                            <a-select-option value="7">童声</a-select-option>
                            <a-select-option value="8">东北话</a-select-option>
                            <a-select-option value="9">天津话</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="对应车机功能" name="car_function">
                        <a-select v-model:value="createFormData.car_function">
                            <a-select-option value="audio-video">音视频</a-select-option>
                            <a-select-option value="navigation-travel">导航与出行</a-select-option>
                            <a-select-option value="communication">通讯</a-select-option>
                            <a-select-option value="vehicle-settings-info-query">车辆设置与信息查询</a-select-option>
                            <a-select-option value="vehicle-control-command">车辆控制指令</a-select-option>
                            <a-select-option value="ai-assistant">AI助手</a-select-option>
                            <a-select-option value="security-privacy">安全与隐私</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="标签" name="label">
                        <a-input v-model:value="createFormData.label"></a-input>
                    </a-form-item>
                    <a-form-item label="预期结果" name="expect_result">
                        <a-input v-model:value="createFormData.expect_result"></a-input>
                    </a-form-item>
                </div>
            </a-form>
        </a-modal>

        <!-- 编辑语料模态框 -->
        <a-modal title="编辑语料" v-model:visible="editModalVisible" @ok="updateCorpus" @cancel="handleCancel" okText="确定"
            cancelText="取消" width="60%">
            <a-form ref="editForm" :model="editFormData" :rules="rules">
                <div class="modal-form-grid">
                    <a-form-item label="语料文本" name="text">
                        <a-input v-model:value="editFormData.text" />
                    </a-form-item>
                    <a-form-item label="测试类型" name="test_type">
                        <a-select v-model:value="editFormData.test_type" @change="handleEditTestTypeChange">
                            <a-select-option value="speech-recognition">语音识别</a-select-option>
                            <a-select-option value="intelligent-interaction">智能交互</a-select-option>
                            <a-select-option value="wake-up-free">免唤醒</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="测试场景" name="test_scenario">
                        <a-select v-model:value="editFormData.test_scenario">
                            <a-select-option v-for="option in editTestScenarioOptions" :key="option.value"
                                :value="option.value">{{ option.label }}</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="发声人" name="speaker">
                        <a-select v-model:value="editFormData.speaker">
                            <a-select-option value="male">男声</a-select-option>
                            <a-select-option value="female">女声</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="语种" name="language">
                        <a-select v-model:value="editFormData.language" v-if="editFormData.speaker === 'female'">
                            <a-select-option value="1">女声1</a-select-option>
                            <a-select-option value="2">女声2</a-select-option>
                            <a-select-option value="3">女声3</a-select-option>
                            <a-select-option value="4">女声4</a-select-option>
                            <a-select-option value="5">女声5</a-select-option>
                            <a-select-option value="6">女声6</a-select-option>
                            <a-select-option value="7">女声7</a-select-option>
                            <a-select-option value="8">童声</a-select-option>
                            <a-select-option value="9">四川话</a-select-option>
                            <a-select-option value="10">粤语</a-select-option>
                            <a-select-option value="11">东北话</a-select-option>
                        </a-select>
                        <a-select v-model:value="editFormData.language" v-if="editFormData.speaker === 'male'">
                            <a-select-option value="1">男声1</a-select-option>
                            <a-select-option value="2">男声2</a-select-option>
                            <a-select-option value="3">男声3</a-select-option>
                            <a-select-option value="4">男声4</a-select-option>
                            <a-select-option value="5">男声5</a-select-option>
                            <a-select-option value="6">男声6</a-select-option>
                            <a-select-option value="7">童声</a-select-option>
                            <a-select-option value="8">东北话</a-select-option>
                            <a-select-option value="9">天津话</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="对应车机功能" name="car_function">
                        <a-select v-model:value="editFormData.car_function">
                            <a-select-option value="audio-video">音视频</a-select-option>
                            <a-select-option value="navigation-travel">导航与出行</a-select-option>
                            <a-select-option value="communication">通讯</a-select-option>
                            <a-select-option value="vehicle-settings-info-query">车辆设置与信息查询</a-select-option>
                            <a-select-option value="vehicle-control-command">车辆控制指令</a-select-option>
                            <a-select-option value="ai-assistant">AI助手</a-select-option>
                            <a-select-option value="security-privacy">安全与隐私</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="标签" name="label">
                        <a-input v-model:value="editFormData.label"></a-input>
                    </a-form-item>
                    <a-form-item label="预期结果" name="expect_result">
                        <a-input v-model:value="editFormData.expect_result"></a-input>
                    </a-form-item>
                </div>
            </a-form>
        </a-modal>

        <!-- 上传语料模态框 -->
        <a-modal title="上传语料" v-model:visible="uploadModalVisible" @ok="handleUpload" @cancel="handleCancel" okText="确定"
            cancelText="取消" width="60%">
            <a-form ref="uploadForm" :model="uploadFormData" :rules="rules">
                <div class="modal-form-grid">
                    <a-form-item label="语料音频" name="audio_url">
                        <el-upload ref="uploadRef" :auto-upload="false" :on-change="onBeforeUploadAudio"
                            v-model:file-list="audio_list" accept=".mp3,.wav" :limit="1">
                            <template #trigger>
                                <el-button>上传文件</el-button>
                            </template>
                        </el-upload>
                    </a-form-item>
                    <a-form-item label="拼音" name="pinyin">
                        <a-input v-model:value="uploadFormData.pinyin" disabled />
                    </a-form-item>
                    <a-form-item label="音频时长" name="audio_duration">
                        <a-input v-model:value="uploadFormData.audio_duration" disabled />
                    </a-form-item>
                </div>
            </a-form>
        </a-modal>

        <!-- 合成语料模态框 -->
        <a-modal title="合成语料" v-model:visible="synthesizeModalVisible" @ok="handleSynthesize" @cancel="handleCancel"
            okText="确定" cancelText="取消" width="60%">
            <a-form ref="synthesizeForm" :model="synthesizeFormData" :rules="rules">
                <div class="modal-form-grid">
                    <a-form-item label="标签" name="label">
                        <a-input v-model:value="synthesizeFormData.label"></a-input>
                    </a-form-item>
                    <a-form-item label="是否添加语气助词" name="is_tone">
                        <a-select v-model:value="synthesizeFormData.is_tone">
                            <a-select-option :value="true">是</a-select-option>
                            <a-select-option :value="false">否</a-select-option>
                        </a-select>
                    </a-form-item>
                </div>
            </a-form>
        </a-modal>

        <!-- 导入语料模态框 -->
        <a-modal title="导入语料" v-model:visible="importModalVisible" @ok="handleCancelImport" @cancel="handleCancelImport"
            okText="确定">
            <div class="flex space-between">
                <a-button type="link" @click="showExcel">打开模板</a-button>
                <el-upload ref="uploadRef" :auto-upload="false" :on-change="batchImport" v-model:file-list="file_list"
                    :show-file-list="false" accept=".xls, .xlsx, .csv">
                    <template #trigger>
                        <a-button type="primary">从文件导入</a-button>
                    </template>
                </el-upload>
            </div>
        </a-modal>

        <!-- 录音模态框 -->
        <RecordModal :visible="recordModalVisible" :corpus_id="recordCorpusId" :text="recordText" @update:visible="recordModalVisible = $event; fetchCorpusList()"
        @updateCorpus="updateRecordCorpus"
            />

        <GeneralizeModal :visible="generalizeModalVisible" :text="generalizeText" :type="'test'"
            @update:visible="generalizeModalVisible = $event" @generalize-success="handleGeneralizeSuccess"
            @generalize-error="handleGeneralizeError" />
        <BatchTableModal :visible="batchTableModalVisible" :batchData="batchData"
            @update:visible="batchTableModalVisible = $event" @update:batchData="batchSynthesizeSuccess"
            @synthesize="" />
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { http } from '@renderer/http';
import { ElMessage, ElMessageBox, UploadProps, ElLoading } from 'element-plus';
import GeneralizeModal from './BatchGeneralize.vue';
import BatchTableModal from './BatchTableModal.vue';
import RecordModal from './RecordModal.vue'; // 引入录音模态框
import BatchSynthesize from '../synthesize/BatchSynthesize.vue';
import { nextTick } from 'process';

const searchText = ref('');
const corpusList = ref([]);
const createModalVisible = ref(false);
const editModalVisible = ref(false);
const uploadModalVisible = ref(false);
const synthesizeModalVisible = ref(false);
const recordModalVisible = ref(false); // 录音模态框的可见性
const createForm = ref(null);
const editForm = ref(null);
const uploadForm = ref(null);
const synthesizeForm = ref(null);
const audio_list = ref([]);
const file_list = ref([]);
const importModalVisible = ref(false);
const selectedRowKeys = ref([]); // 选中的行ID
const isSynthesizing = ref(false);
const generalizeModalVisible = ref(false);
const generalizeText = ref('');
const batchTableModalVisible = ref(false);
const recordText = ref(''); // 录音模态框中的文本
const recordCorpusId = ref('');

const showImportModal = () => {
    importModalVisible.value = true;
}

const playAudio = (record) => {
    const audioPath = record.audio_path;
    if (!audioPath) {
        ElMessage.warning('音频路径不存在');
        return;
    }
    const newPath = record.audio_path.replaceAll('\\', '/').split('/backend')?.[1];
    const audio = new Audio(newPath);
    audio.play();
};

const handleCancelImport = () => {
    importModalVisible.value = false;
}

const showExcel = () => {
    window.electron.ipcRenderer.send('open-demo-xlsx', 'test_corpus_demo.xlsx');
}

const handleGeneralizeSuccess = (data: any) => {
    console.log(data);
    alert('泛化成功');
    batchData.value = data;
    batchTableModalVisible.value = true;
};

const handleGeneralizeError = () => {
    alert('泛化失败');
};

const filter = reactive({
    test_type: undefined,
    test_scenario: undefined,
    language: undefined,
    evaluation_metric: undefined,
    speaker: undefined,
    car_function: undefined,
});

const createFormData = reactive({
    text: '',
    test_type: 'speech-recognition',
    test_scenario: 'speech-recognition-interaction',
    speaker: 'male',
    language: '1',
    car_function: 'audio-video',
    label: '',
    expect_result: '',
});

const editFormData = reactive({
    corpus_id: '',
    text: '',
    test_type: 'speech-recognition',
    test_scenario: 'speech-recognition-interaction',
    speaker: 'male',
    language: '1',
    car_function: 'audio-video',
    label: '',
    expect_result: ''
});

const uploadFormData = reactive({
    corpus_id: '',
    audio_url: '',
    aud_id: '',
    pinyin: '',
    audio_duration: '',
    text: '',
});

const synthesizeFormData = reactive({
    label: '',
    is_tone: false,
});

const columns = [
    { title: '序号', dataIndex: 'corpus_id' },
    { title: '语料文本', dataIndex: 'text', width: '24%', },
    { title: '测试场景', dataIndex: 'test_scenario', key: 'test_scenario' },
    { title: '语料音频', key: 'audio', scopedSlots: { customRender: 'audio' } },
    { title: '发声人', dataIndex: 'speaker', key: 'speaker' },
    { title: '语种', dataIndex: 'language', key: 'language' },
    { title: '标签', key: 'label' },
    { title: '对应车机功能', dataIndex: 'car_function', key: 'car_function' },
    { title: '预期结果', dataIndex: 'expect_result', key: 'expect_result' },
    {
        title: '操作',
        key: 'action',
        width: '18%',
        scopedSlots: { customRender: 'action' },
    },
];

const paginationConfig = reactive({
    total: 1000,
    pageSize: 100,
    current: 1,
    onChange: (page, pageSize) => {
        paginationConfig.current = page;
        paginationConfig.pageSize = pageSize;
        fetchCorpusList();
    },
});

const languageOptions = ref([]);

const handleSpeakerChange = (value) => {
    languageOptions.value = getLanguageOptions(value);
    if (languageOptions.value.length > 0) {
        filter.language = languageOptions.value[0].value;
    }
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

onMounted(() => {
    fetchCorpusList();
    handleTestTypeChange(filter.test_type); // 初始化 test_scenario 选项
    handleCreateTestTypeChange(createFormData.test_type); // 初始化 createFormData 的 test_scenario 选项
    handleEditTestTypeChange(editFormData.test_type); // 初始化 editFormData 的 test_scenario 选项
    handleSpeakerChange(filter.speaker); // 初始化 language 选项
});

const fetchCorpusList = async () => {
    const params = {
        text: searchText.value || void 0,
        test_type: filter.test_type,
        test_scenario: filter.test_scenario,
        language: filter.language,
        evaluation_metric: filter.evaluation_metric,
        speaker: filter.speaker,
        car_function: filter.car_function,
    };
    const data = await http.post('/corpus/get_test_corpus_list', params);
    corpusList.value = data.data;
    paginationConfig.total = data.total;
};

const showCreateModal = () => {
    createModalVisible.value = true;
    createFormData.text = '';
    // createFormData.test_type = 'speech-recognition';
    // createFormData.test_scenario = 'speech-recognition-interaction';
    createFormData.speaker = 'male';
    createFormData.language = '1';
    createFormData.car_function = 'audio-video';
    createFormData.label = '';
    createFormData.expect_result = '';
    audio_list.value = [];
};

const showEditModal = (record) => {
    editFormData.corpus_id = record.corpus_id;
    editFormData.text = record.text;
    editFormData.test_type = record.test_type;
    nextTick(() => {
        editFormData.test_scenario = record.test_scenario;
    })
    editFormData.speaker = record.speaker;
    editFormData.language = record.language;
    editFormData.car_function = record.car_function;
    editFormData.label = record.label;
    editFormData.expect_result = record.expect_result;
    audio_list.value = [{ name: record.audio_url, url: record.audio_url }];
    editModalVisible.value = true;
};

const showUploadModal = (record) => {
    uploadFormData.corpus_id = record.corpus_id;
    uploadFormData.audio_url = record.audio_url;
    uploadFormData.text = record.text;
    if (record.audio_url) {
        audio_list.value = [{ name: record.audio_url, url: record.audio_url }];
    } else {
        audio_list.value = [];
    }

    uploadModalVisible.value = true;
};

const showSynthesizeModal = () => {
    if (selectedRowKeys.value.length === 0) {
        ElMessage.warning('请选择要合成的语料');
        return;
    }
    synthesizeModalVisible.value = true;
};

const showRecordModal = (record) => {
    recordText.value = record.text;
    recordCorpusId.value = record.corpus_id;
    recordModalVisible.value = true;
};

const createCorpus = () => {
    createForm.value.validate().then(async () => {
        await http.post('/corpus/create_test_corpus', createFormData);
        createModalVisible.value = false;
        fetchCorpusList();
    });
};

const updateCorpus = () => {
    editForm.value.validate().then(async () => {
        await http.post('/corpus/update_test_corpus', editFormData);
        editModalVisible.value = false;
        fetchCorpusList();
    });
};

const handleUpload = () => {
    uploadForm.value.validate().then(async () => {
        await http.post('/corpus/upload_test_corpus', uploadFormData);
        uploadModalVisible.value = false;
        fetchCorpusList();
    });
};

const deleteCorpus = async (id) => {
    const confirmResult = await ElMessageBox.confirm(
        '确定要删除该语料吗？',
        '警告',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    );

    if (confirmResult) {
        await http.post('/corpus/delete_test_corpus', { corpus_id: id });
        fetchCorpusList();
    }
};

const handleCancel = () => {
    createModalVisible.value = false;
    editModalVisible.value = false;
    uploadModalVisible.value = false;
    synthesizeModalVisible.value = false;
    recordModalVisible.value = false; // 关闭录音模态框
};

const table_height = window.innerHeight * 0.55;

const rules = {
    text: [{ required: true, message: '请填写语料文本', trigger: 'change' }],
};

const onBeforeUploadAudio: UploadProps['onChange'] = async (file) => {
    console.log(file);
    const formData = new FormData();
    formData.append('info', JSON.stringify({ category: 'audio', text: uploadFormData.text }));
    formData.append('file', file.raw);
    try {
        const response = await http.post(`/corpus/upload_audio_file`, formData);

        if (response) {
            uploadFormData.audio_url = file.name;
            uploadFormData.pinyin = response.pinyin;
            uploadFormData.audio_duration = response.audio_duration;
            uploadFormData.aud_id = response.aud_id;
        }
    } catch (error) {
        console.error("Upload failed: ", error);
    }
};

const getTestScenarioTextForTable = (test_type, test_scenario) => {
    const map = {
        'speech-recognition-interaction': '语音识别交互',
        'speech-recognition-ability': '语音识别能力',
        'single-command-interaction': '单指令交互',
        'continuous-dialogue-interaction': '连续对话交互',
        'multi-command-interaction': '多指令交互',
        'fuzzy-command-interaction': '模糊指令交互',
        'multi-topic-cross-execution': '多话题交叉执行',
        'wake-up-free': '免唤醒',
    };
    return map[test_scenario] || test_scenario;
};

const getEvaluationMetricText = (value) => {
    const map = {
        'speech-recognition-rate': '语音识别成功率',
        'intelligent-interaction-rate': '交互成功率',
        'conversational-success-rate': '连续对话成功率',
    };
    return map[value] || value;
};

const getSpeakerText = (value) => {
    const map = {
        'male': '男声',
        'female': '女声',
        'boy': '男童声',
        'girl': '女童声',
    };
    return map[value] || value;
};

const getLanguageTextForTable = (value, speaker) => {
    let map = {}
    if (speaker === 'male') {
        map = {
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
    } else {
        map = {
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
        }
    }

    return map[value] || value;
};

const getCarFunctionText = (value) => {
    const map = {
        'audio-video': '音视频',
        'navigation-travel': '导航与出行',
        'communication': '通讯',
        'vehicle-settings-info-query': '车辆设置与信息查询',
        'vehicle-control-command': '车辆控制指令',
        'ai-assistant': 'AI助手',
        'security-privacy': '安全与隐私',
    };
    return map[value] || value;
};

const testScenarioOptions = ref([]);
const createTestScenarioOptions = ref([]);
const editTestScenarioOptions = ref([]);

const handleTestTypeChange = (value) => {
    testScenarioOptions.value = getTestScenarioOptions(value);
    if (testScenarioOptions.value.length > 0) {
        filter.test_scenario = testScenarioOptions.value[0].value;
    }
};

const handleCreateTestTypeChange = (value) => {
    createTestScenarioOptions.value = getTestScenarioOptions(value);
    console.log(createTestScenarioOptions.value);
    if (createTestScenarioOptions.value.length > 0) {
        createFormData.test_scenario = createTestScenarioOptions.value[0].value;
    }
};

const handleEditTestTypeChange = (value) => {
    editTestScenarioOptions.value = getTestScenarioOptions(value);
    if (editTestScenarioOptions.value.length > 0) {
        editFormData.test_scenario = editTestScenarioOptions.value[0].value;
    }
};

const batchImport: UploadProps['onChange'] = async (file) => {
    const formData = new FormData();
    formData.append('info', JSON.stringify({ category: 'test_corpus' }));
    formData.append('file', file.raw);
    try {
        const response = await http.post(`/corpus/batch_import`, formData);
        if (response.status === 'success') {
            ElMessage.success('导入成功，请等待批量处理')
        }
    } catch (error) {
        console.error("Upload failed: ", error);
    } finally {
        fetchCorpusList();
        handleCancelImport();
    }
};

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

// 表格选择功能
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

// 批量删除
const batchDeleteCorpus = async () => {
    if (selectedRowKeys.value.length === 0) {
        ElMessage.warning('请选择要删除的语料');
        return;
    }

    const confirmResult = await ElMessageBox.confirm(
        '确定要删除选中的语料吗？',
        '警告',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    );

    if (confirmResult) {
        const result = await http.post('/corpus/batch_delete_test_corpus', { corpus_ids: selectedRowKeys.value });
        if (result.status === 'error') {
            ElMessage.error('删除语料失败, 语料id为' + result.error_list.join(','));
            return;
        } else {
            ElMessage.success('删除语料成功');
        }
        fetchCorpusList();
        selectedRowKeys.value = [];
    }
};

// 合成语料
const handleSynthesize = () => {
    synthesizeForm.value.validate().then(async () => {
        const params = {
            corpus_ids: selectedRowKeys.value,
            ...synthesizeFormData,
        };
        const loadingInstance = ElLoading.service({ target: '.container', text: '合成中...' });
        try {
            const result = await http.post('/corpus/synthesize_test_corpus', params);
            if (result.status === 'success') {
                ElMessage.success('合成成功');
            }
        } finally {
            loadingInstance.close();
        }

        synthesizeModalVisible.value = false;
        fetchCorpusList();
        selectedRowKeys.value = [];
    });
};

const batchData = ref([
    { text: '', voice: '1', language: '1', type: '1', label: 'tts', expect_result: '' }, // 添加 expect_result 字段
]);

const showGeneralizeModal = (record) => {
    generalizeText.value = record.text;
    console.log(record.text);
    generalizeModalVisible.value = true;
};

const batchSynthesizeSuccess = () => {
    fetchCorpusList();
}

const handleRecordSuccess = (data) => {
    console.log('录音上传成功', data);
    fetchCorpusList();
};

const handleRecordError = (error) => {
    console.error('录音上传失败', error);
};

const updateRecordCorpus = async (data) => {
    const loadingInstance = ElLoading.service({ target: '.container', text: '更新中...' });
    try {
        const result = await http.post('/corpus/upload_test_corpus', { ...data });
        if (result.status === 'success') {
            recordModalVisible.value = false;
            fetchCorpusList();
            ElMessage.success('更新成功');
        }
    } finally {
        loadingInstance.close();
    }
}
</script>

<style scoped>
.modal-form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-gap: 20px;
}

.upload-container {
    display: flex;
    justify-content: center;
    align-items: center;
    border: 1px dashed #d9d9d9;
    border-radius: 4px;
    height: 100px;
    cursor: pointer;
}

.upload-container:hover {
    border-color: #1890ff;
}

.upload-text {
    margin-top: 8px;
}

:deep(.el-upload__input) {
    display: none !important;
}
</style>