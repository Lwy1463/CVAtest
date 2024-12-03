<template>
    <div class="container">
        <a-row justify="center" style="margin-bottom: 20px;">
            <a-col :span="12">
                <a-card title="选择音频文件保存位置" class="card">
                    <a-input-group compact>
                        <a-input v-model:value="savePath" placeholder="选择保存路径" style="width: calc(100% - 100px);" readonly />
                        <a-button type="primary" @click="selectSavePath">选择路径</a-button>
                    </a-input-group>
                </a-card>
            </a-col>
        </a-row>
        <a-row justify="center" style="margin-bottom: 20px;">
            <a-col :span="12">
                <a-card title="音频文件列表" class="card">
                    <a-table :columns="columns" :dataSource="paginatedWavFiles" :pagination="false" bordered size="small">
                        <template #bodyCell="{ column, record }">
                            <template v-if="column.key === 'name'">
                                {{ record.name }}
                            </template>
                        </template>
                    </a-table>
                    <a-pagination
                        v-model:current="currentPage"
                        :total="wavFiles.length"
                        :pageSize="pageSize"
                        show-less-items
                        @change="handlePageChange"
                        style="margin-top: 20px;"
                    />
                </a-card>
            </a-col>
        </a-row>
        <a-row justify="center">
            <a-col :span="12">
                <a-card title="操作" class="card">
                    <a-button type="primary" @click="startRecording" :disabled="isRecording" class="action-button">开始录制</a-button>
                    <a-button type="primary" @click="stopRecording" :disabled="!isRecording" class="action-button">停止录制</a-button>
                </a-card>
            </a-col>
        </a-row>
        <a-modal v-model:visible="permissionModalVisible" title="麦克风权限提示" @ok="openSystemPreferences">
            <p>请在系统设置中授予麦克风权限。</p>
        </a-modal>
    </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const savePath = ref(localStorage.getItem('savePath') || '');
const isRecording = ref(false);
const permissionModalVisible = ref(false);
const wavFiles = ref([]);
const currentPage = ref(1);
const pageSize = 5;

const columns = [
    { title: '文件名', dataIndex: 'name', key: 'name' },
];

const paginatedWavFiles = computed(() => {
    const start = (currentPage.value - 1) * pageSize;
    const end = start + pageSize;
    return wavFiles.value.slice(start, end);
});

const selectSavePath = () => {
    window.electron.ipcRenderer.send('select-save-path');
};

const startRecording = () => {
    if (savePath.value) {
        window.electron.ipcRenderer.send('show-save-dialog');
    } else {
        alert('请先选择保存路径');
    }
};

const stopRecording = () => {
    isRecording.value = false;
    window.electron.ipcRenderer.send('stop-recording');
};

const handleSavePathSelected = (event, path) => {
    savePath.value = path;
    localStorage.setItem('savePath', path);
    window.electron.ipcRenderer.send('list-wav-files', path);
};

const handleWavFilesListed = (event, files) => {
    wavFiles.value = files.map(file => ({ name: file }));
    currentPage.value = 1; // Reset to the first page when new files are listed
};

const handleRecordingError = () => {
    isRecording.value = false;
    permissionModalVisible.value = true;
};

const handleRecordingCompleted = () => {
    window.electron.ipcRenderer.send('list-wav-files', savePath.value);
};

const openSystemPreferences = () => {
    window.electron.ipcRenderer.send('open-system-preferences');
    permissionModalVisible.value = false;
};

const handlePageChange = (page: number) => {
    currentPage.value = page;
};

onMounted(() => {
    window.electron.ipcRenderer.on('save-path-selected', handleSavePathSelected);
    window.electron.ipcRenderer.on('wav-files-listed', handleWavFilesListed);
    window.electron.ipcRenderer.on('recording-error', handleRecordingError);
    window.electron.ipcRenderer.on('recording-completed', handleRecordingCompleted);
    window.electron.ipcRenderer.on('start-recording', (event, fileName) => {
        isRecording.value = true;
        window.electron.ipcRenderer.send('start-recording', `${savePath.value}/${fileName}`);
    });

    if (savePath.value) {
        window.electron.ipcRenderer.send('list-wav-files', savePath.value);
    }
});

onUnmounted(() => {
    window.electron.ipcRenderer.removeListener('save-path-selected', handleSavePathSelected);
    window.electron.ipcRenderer.removeListener('wav-files-listed', handleWavFilesListed);
    window.electron.ipcRenderer.removeListener('recording-error', handleRecordingError);
    window.electron.ipcRenderer.removeListener('recording-completed', handleRecordingCompleted);
    window.electron.ipcRenderer.removeListener('start-recording', (event, fileName) => {
        isRecording.value = true;
        window.electron.ipcRenderer.send('start-recording', `${savePath.value}/${fileName}`);
    });
});
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

.action-button {
    margin-right: 10px;
}
</style>