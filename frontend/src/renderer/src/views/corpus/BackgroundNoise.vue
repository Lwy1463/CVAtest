<template>
    <div style="margin: 20px;">
        <a-page-header title="背景噪声管理" />
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <a-input-search v-model:value="searchText" placeholder="请输入背景噪声文本" style="width: 200px"
                @search="fetchBackgroundNoiseList" />
            <a-button type="primary" @click="showCreateModal"> 新增背景噪声 </a-button>
        </div>

        <!-- 新增的搜索过滤项 -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div style="display: flex; gap: 10px;">
                <a-select v-model:value="filter.noise_environ" placeholder="噪声环境" style="width: 120px">
                    <a-select-option value="highway">高速</a-select-option>
                    <a-select-option value="downtown">闹市</a-select-option>
                    <a-select-option value="quiet">安静</a-select-option>
                </a-select>
            </div>
            <a-button type="primary" @click="fetchBackgroundNoiseList">搜索</a-button>
        </div>

        <a-table :columns="columns" :dataSource="backgroundNoiseList" :rowKey="record => record.corpus_id"
            pagination="paginationConfig" :scroll="{ y: table_height }">
            <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'action'">
                    <a-button style="color: #de8dcc" type="link" @click="showEditModal(record)">编辑</a-button>
                    <a-button style="color: #de8dcc" type="link" @click="deleteBackgroundNoise(record)">删除</a-button>
                </template>
                <template v-else-if="column.key === 'audio'">
                    {{ record.audio_url }}
                </template>
            </template>
        </a-table>

        <a-modal title="新增背景噪声" v-model:visible="createModalVisible" @ok="createBackgroundNoise" @cancel="handleCancel" okText="确定"
            cancelText="取消" width="60%">
            <a-form ref="createForm" :model="createFormData" :rules="rules">
                <div class="modal-form-grid">
                    <a-form-item label="背景噪声文本" name="text">
                        <a-input v-model:value="createFormData.text" />
                    </a-form-item>
                    <a-form-item label="噪声环境" name="noise_environ">
                        <a-select v-model:value="createFormData.noise_environ">
                            <a-select-option value="highway">高速</a-select-option>
                            <a-select-option value="downtown">闹市</a-select-option>
                            <a-select-option value="quiet">安静</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="背景噪声音频" name="audio_url">
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
                </div>
            </a-form>
        </a-modal>

        <a-modal title="编辑背景噪声" v-model:visible="editModalVisible" @ok="updateBackgroundNoise" @cancel="handleCancel" okText="确定"
            cancelText="取消" width="60%">
            <a-form ref="editForm" :model="editFormData" :rules="rules">
                <div class="modal-form-grid">
                    <a-form-item label="背景噪声文本" name="text">
                        <a-input v-model:value="editFormData.text" />
                    </a-form-item>
                    <a-form-item label="噪声环境" name="noise_environ">
                        <a-select v-model:value="editFormData.noise_environ">
                            <a-select-option value="highway">高速</a-select-option>
                            <a-select-option value="downtown">闹市</a-select-option>
                            <a-select-option value="quiet">安静</a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item label="背景噪声音频" name="audio_url">
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
const backgroundNoiseList = ref([]);
const createModalVisible = ref(false);
const editModalVisible = ref(false);
const createForm = ref(null);
const editForm = ref(null);
const audio_list = ref([]);

const filter = reactive({
    noise_environ: undefined,
});

const createFormData = reactive({
    text: '',
    noise_environ: 'highway',
    audio_url: '',
    audio_duration: '',
});

const editFormData = reactive({
    id: '',
    text: '',
    noise_environ: 'highway',
    audio_url: '',
    audio_duration: '',
});

const columns = [
    { title: '序号', dataIndex: 'corpus_id' },
    { title: '背景噪声文本', dataIndex: 'text' },
    { title: '噪声环境', dataIndex: 'noise_environ' },
    { title: '背景噪声音频', key: 'audio', scopedSlots: { customRender: 'audio' } },
    { title: '音频时长(s)', dataIndex: 'audio_duration' },
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
        fetchBackgroundNoiseList();
    },
});

onMounted(() => {
    fetchBackgroundNoiseList();
});

const fetchBackgroundNoiseList = async () => {
    const params = {
        text: searchText.value || void 0,
        noise_environ: filter.noise_environ,
    };
    const data = await http.post('/corpus/get_background_noise_list', params);
    backgroundNoiseList.value = data.data;
    paginationConfig.total = data.total;
};

const showCreateModal = () => {
    createModalVisible.value = true;
    createFormData.text = '';
    createFormData.noise_environ = 'highway';
    createFormData.audio_url = '';
    createFormData.audio_duration = '';
    createFormData.aud_id = '';
    audio_list.value = [];
};

const showEditModal = (record) => {
    editFormData.id = record.id;
    editFormData.text = record.text;
    editFormData.noise_environ = record.noise_environ;
    editFormData.audio_url = record.audio_url;
    editFormData.audio_duration = record.audio_duration;
    editFormData.aud_id = record.aud_id;
    audio_list.value = [{ name: record.audio_url, url: record.audio_url }];
    editModalVisible.value = true;
};

const createBackgroundNoise = () => {
    if (!createFormData.text) {
        ElMessage.error('请填写背景噪声文本');
        return;
    }
    
    createForm.value.validate().then(async () => {
        await http.post('/corpus/create_background_noise', createFormData);
        createModalVisible.value = false;
        fetchBackgroundNoiseList();
    });
};

const updateBackgroundNoise = () => {
    if (!editFormData.text) {
        ElMessage.error('请填写背景噪声文本');
        return;
    }
    editForm.value.validate().then(async () => {
        await http.post('/corpus/update_background_noise', editFormData);
        editModalVisible.value = false;
        fetchBackgroundNoiseList();
    });
};

const deleteBackgroundNoise = async (record) => {
    console.log(record);
    const confirmResult = await ElMessageBox.confirm(
        '确定要删除该背景噪声吗？',
        '警告',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    );

    if (confirmResult) {
        await http.post('/corpus/delete_background_noise', { corpus_id: record.corpus_id });
        fetchBackgroundNoiseList();
    }
};

const handleCancel = () => {
    createModalVisible.value = false;
    editModalVisible.value = false;
};

const table_height = window.innerHeight * 0.55;

const rules = {
    text: [{ required: true, message: '请填写背景噪声文本', trigger: 'change' }],
};

const onBeforeUploadAudio: UploadProps['onChange'] = async (file) => {
    const formData = new FormData();

    if (!createFormData.text) {
        ElMessage.error('请填写背景噪声文本');
        return false;
    }
    formData.append('info', JSON.stringify({ category: 'audio', text: createFormData.text }));
    formData.append('file', file.raw);
    try {
        const response = await http.post(`/corpus/upload_audio_file`, formData);

        if (response) {
            if (createModalVisible.value) {
                createFormData.audio_url = file.name;
                createFormData.aud_id = response.audio_id;
                createFormData.audio_duration = response.audio_duration;
            } else {
                editFormData.audio_url = file.name;
                editFormData.aud_id = response.audio_id;
                editFormData.audio_duration = response.audio_duration;
            }
            
        }
    } catch (error) {
        console.error("Upload failed: ", error);
    }
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