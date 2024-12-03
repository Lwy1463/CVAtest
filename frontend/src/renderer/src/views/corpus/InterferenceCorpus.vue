<template>
    <div style="margin: 20px;">
        <a-page-header title="干扰语料管理" />
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <a-input-search v-model:value="searchText" placeholder="请输入干扰语料文本" style="width: 200px"
                @search="fetchInterferenceCorpusList" />
            <a-button type="primary" @click="showCreateModal"> 新增干扰语料 </a-button>
        </div>

        <!-- 新增的搜索过滤项 -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div style="display: flex; gap: 10px;">
                <a-select v-model:value="filter.language" placeholder="语种" style="width: 120px">
                    <a-select-option value="mandarin">普通话</a-select-option>
                    <a-select-option value="cantonese">粤语</a-select-option>
                    <a-select-option value="english">英文</a-select-option>
                </a-select>
                <a-select v-model:value="filter.evaluation_metric" placeholder="所属评价指标" style="width: 150px">
                    <a-select-option value="speech-recognition-rate">语音识别成功率</a-select-option>
                    <a-select-option value="intelligent-interaction-rate">交互成功率</a-select-option>
                    <a-select-option value="conversational-success-rate">连续对话成功率</a-select-option>
                </a-select>
                <a-select v-model:value="filter.speaker" placeholder="发声人" style="width: 120px">
                    <a-select-option value="male">男声</a-select-option>
                    <a-select-option value="female">女声</a-select-option>
                    <a-select-option value="boy">男童声</a-select-option>
                    <a-select-option value="girl">女童声</a-select-option>
                </a-select>
            </div>
            <a-button type="primary" @click="fetchInterferenceCorpusList">搜索</a-button>
        </div>

        <a-table :columns="columns" :dataSource="interferenceCorpusList" :rowKey="record => record.id"
            :pagination="paginationConfig" :scroll="{ y: table_height }">
            <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'action'">
                    <a-button style="color: #de8dcc" type="link" @click="showEditModal(record)">编辑</a-button>
                    <a-button style="color: #de8dcc" type="link" @click="deleteInterferenceCorpus(record.corpus_id)">删除</a-button>
                </template>
                <template v-else-if="column.key === 'audio'">
                    {{ record.audio_url }}
                </template>
                <template v-else-if="column.key === 'evaluation_metric'">
                    {{ getEvaluationMetricText(record.evaluation_metric) }}
                </template>
                <template v-else-if="column.key === 'speaker'">
                    {{ getSpeakerText(record.speaker) }}
                </template>
                <template v-else-if="column.key === 'language'">
                    {{ getLanguageText(record.language) }}
                </template>
            </template>
        </a-table>

        <a-modal title="新增干扰语料" v-model:visible="createModalVisible" @ok="createInterferenceCorpus" @cancel="handleCancel" okText="确定"
            cancelText="取消" width="60%">
            <a-form ref="createForm" :model="createFormData" :rules="rules">
                <div class="modal-form-grid">
                    <a-form-item label="干扰语料文本" name="text">
                        <a-input v-model:value="createFormData.text" />
                    </a-form-item>
                    <a-form-item label="文本拼音" name="pinyin">
                        <a-input v-model:value="createFormData.pinyin" disabled/>
                    </a-form-item>
                    <a-form-item label="所属评价指标" name="evaluation_metric">
                        <a-select v-model:value="createFormData.evaluation_metric">
                            <a-select-option value="speech-recognition-rate">语音识别成功率</a-select-option>
                            <a-select-option value="intelligent-interaction-rate">交互成功率</a-select-option>
                            <a-select-option value="conversational-success-rate">连续对话成功率</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="干扰语料音频" name="audio_url">
                        <el-upload ref="uploadRef" :auto-upload="false" :on-change="onBeforeUploadAudio" v-model:file-list="audio_list"
                            accept=".mp3,.wav">
                            <template #trigger>
                                <el-button>上传文件</el-button>
                            </template>
                        </el-upload>
                    </a-form-item>
                    <a-form-item label="音频时长" name="audio_duration">
                        <a-input v-model:value="createFormData.audio_duration" disabled />
                    </a-form-item>
                    <a-form-item label="发声人" name="speaker">
                        <a-select v-model:value="createFormData.speaker">
                            <a-select-option value="male">男声</a-select-option>
                            <a-select-option value="female">女声</a-select-option>
                            <a-select-option value="boy">男童声</a-select-option>
                            <a-select-option value="girl">女童声</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="语种" name="language">
                        <a-select v-model:value="createFormData.language">
                            <a-select-option value="mandarin">普通话</a-select-option>
                            <a-select-option value="cantonese">粤语</a-select-option>
                            <a-select-option value="english">英文</a-select-option>
                        </a-select>
                    </a-form-item>
                </div>
            </a-form>
        </a-modal>

        <a-modal title="编辑干扰语料" v-model:visible="editModalVisible" @ok="updateInterferenceCorpus" @cancel="handleCancel" okText="确定"
            cancelText="取消" width="60%">
            <a-form ref="editForm" :model="editFormData" :rules="rules">
                <div class="modal-form-grid">
                    <a-form-item label="干扰语料文本" name="text">
                        <a-input v-model:value="editFormData.text" />
                    </a-form-item>
                    <a-form-item label="文本拼音" name="pinyin">
                        <a-input v-model:value="editFormData.pinyin" disabled/>
                    </a-form-item>
                    <a-form-item label="所属评价指标" name="evaluation_metric">
                        <a-select v-model:value="editFormData.evaluation_metric">
                            <a-select-option value="speech-recognition-rate">语音识别成功率</a-select-option>
                            <a-select-option value="intelligent-interaction-rate">交互成功率</a-select-option>
                            <a-select-option value="conversational-success-rate">连续对话成功率</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="干扰语料音频" name="audio_url">
                        <el-upload ref="uploadRef" :auto-upload="false" :on-change="onBeforeUploadAudio" v-model:file-list="audio_list"
                            accept=".mp3,.wav">
                            <template #trigger>
                                <el-button>上传文件</el-button>
                            </template>
                        </el-upload>
                    </a-form-item>
                    <a-form-item label="音频时长" name="audio_duration">
                        <a-input v-model:value="editFormData.audio_duration" disabled />
                    </a-form-item>
                    <a-form-item label="发声人" name="speaker">
                        <a-select v-model:value="editFormData.speaker">
                            <a-select-option value="male">男声</a-select-option>
                            <a-select-option value="female">女声</a-select-option>
                            <a-select-option value="boy">男童声</a-select-option>
                            <a-select-option value="girl">女童声</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="语种" name="language">
                        <a-select v-model:value="editFormData.language">
                            <a-select-option value="mandarin">普通话</a-select-option>
                            <a-select-option value="cantonese">粤语</a-select-option>
                            <a-select-option value="english">英文</a-select-option>
                        </a-select>
                    </a-form-item>
                </div>
            </a-form>
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { http } from '@renderer/http';
import { ElMessage, ElMessageBox, UploadProps } from 'element-plus';

const searchText = ref('');
const interferenceCorpusList = ref([]);
const createModalVisible = ref(false);
const editModalVisible = ref(false);
const createForm = ref(null);
const editForm = ref(null);
const audio_list = ref([]);

const filter = reactive({
    language: undefined,
    evaluation_metric: undefined,
    speaker: undefined,
});

const createFormData = reactive({
    text: '',
    pinyin: '',
    evaluation_metric: 'speech-recognition-rate',
    audio_url: '',
    audio_duration: '',
    speaker: 'male',
    language: 'mandarin',
    aud_id: '',
});

const editFormData = reactive({
    corpus_id: '',
    text: '',
    pinyin: '',
    evaluation_metric: 'speech-recognition-rate',
    audio_url: '',
    aud_id: '',
    audio_duration: '',
    speaker: 'male',
    language: 'mandarin',
});

const columns = [
    { title: '序号', dataIndex: 'corpus_id' },
    { title: '干扰语料文本', dataIndex: 'text' },
    { title: '文本拼音', dataIndex: 'pinyin' },
    { title: '所属评价指标', dataIndex: 'evaluation_metric', key: 'evaluation_metric' },
    { title: '干扰语料音频', key: 'audio', scopedSlots: { customRender: 'audio' } },
    { title: '音频时长(s)', dataIndex: 'audio_duration' },
    { title: '发声人', dataIndex: 'speaker', key: 'speaker' },
    { title: '语种', dataIndex: 'language', key: 'language' },
    {
        title: '操作',
        key: 'action',
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
        fetchInterferenceCorpusList();
    },
});

onMounted(() => {
    fetchInterferenceCorpusList();
});

const fetchInterferenceCorpusList = async () => {
    const params = {
        text: searchText.value || void 0,
        language: filter.language,
        evaluation_metric: filter.evaluation_metric,
        speaker: filter.speaker,
    };
    const data = await http.post('/corpus/get_disturb_corpus_list', params);
    interferenceCorpusList.value = data.data;
    paginationConfig.total = data.total;
};

const showCreateModal = () => {
    createModalVisible.value = true;
    createFormData.text = '';
    createFormData.pinyin = '';
    createFormData.evaluation_metric = 'speech-recognition-rate';
    createFormData.audio_url = '';
    createFormData.audio_duration = '';
    createFormData.speaker = 'male';
    createFormData.language = 'mandarin';
    audio_list.value = [];
};

const showEditModal = (record) => {
    editFormData.id = record.id;
    editFormData.text = record.text;
    editFormData.pinyin = record.pinyin;
    editFormData.evaluation_metric = record.evaluation_metric;
    editFormData.audio_url = record.audio_url;
    editFormData.audio_duration = record.audio_duration;
    editFormData.speaker = record.speaker;
    editFormData.language = record.language;
    audio_list.value = [{ name: record.audio_url, url: record.audio_url }];
    editModalVisible.value = true;
};

const createInterferenceCorpus = () => {
    if (!createFormData.text) {
        ElMessage.error('请填写干扰语料文本');
        return;
    }
    
    createForm.value.validate().then(async () => {
        await http.post('/corpus/create_disturb_corpus', createFormData);
        createModalVisible.value = false;
        fetchInterferenceCorpusList();
    });
};

const updateInterferenceCorpus = () => {
    if (!editFormData.text) {
        ElMessage.error('请填写干扰语料文本');
        return;
    }
    editForm.value.validate().then(async () => {
        await http.post('/corpus/update_disturb_corpus', editFormData);
        editModalVisible.value = false;
        fetchInterferenceCorpusList();
    });
};

const deleteInterferenceCorpus = async (id) => {
    const confirmResult = await ElMessageBox.confirm(
        '确定要删除该干扰语料吗？',
        '警告',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    );

    if (confirmResult) {
        await http.post('/corpus/delete_disturb_corpus', { corpus_id: id });
        fetchInterferenceCorpusList();
    }
};

const handleCancel = () => {
    createModalVisible.value = false;
    editModalVisible.value = false;
};

const table_height = window.innerHeight * 0.55;

const rules = {
    text: [{ required: true, message: '请填写干扰语料文本', trigger: 'change' }],
};

const onBeforeUploadAudio: UploadProps['onChange'] = async (file) => {
    const formData = new FormData();

    if (!createFormData.text) {
        ElMessage.error('请填写干扰语料文本');
        return false;
    }
    formData.append('info', JSON.stringify({ category: 'audio', text: createFormData.text }));
    formData.append('file', file.raw);
    try {
        const response = await http.post(`/corpus/upload_audio_file`, formData);

        if (response) {
            if (createModalVisible.value) {
                createFormData.audio_url = file.name;
            } else {
                editFormData.audio_url = file.name;
            }
            createFormData.pinyin = response.pinyin;
            createFormData.audio_duration = response.audio_duration;
            createFormData.aud_id = response.aud_id;
        }
    } catch (error) {
        console.error("Upload failed: ", error);
    }
};

// 转换函数
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

const getLanguageText = (value) => {
    const map = {
        'mandarin': '普通话',
        'cantonese': '粤语',
        'english': '英文',
    };
    return map[value] || value;
};
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