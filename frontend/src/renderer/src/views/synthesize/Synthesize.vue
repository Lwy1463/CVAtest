<template>
    <div class="container">
        <a-row :gutter="24">
            <a-col :span="12">
                <a-card title="合成音频" class="card" style="height: calc(100vh - 8rem); overflow-y: auto;">
                    <a-form layout="vertical">
                        <a-form-item label="语料文本">
                            <a-textarea v-model:value="text" placeholder="请输入语料文本" :rows="2" />
                        </a-form-item>
                        <a-form-item label="发声人">
                            <a-radio-group v-model:value="voice">
                                <a-radio value="1">男声</a-radio>
                                <a-radio value="2">女声</a-radio>
                            </a-radio-group>
                        </a-form-item>
                        <a-form-item label="语种">
                            <a-radio-group v-model:value="language" v-if="voice === '2'">
                                <a-radio value="1">女声1</a-radio>
                                <a-radio value="2">女声2</a-radio>
                                <a-radio value="3">女声3</a-radio>
                                <a-radio value="4">女声4</a-radio>
                                <a-radio value="5">女声5</a-radio>
                                <a-radio value="6">女声6</a-radio>
                                <a-radio value="7">女声7</a-radio>
                                <a-radio value="8">童声</a-radio>
                                <a-radio value="9">四川话</a-radio>
                                <a-radio value="10">粤语</a-radio>
                                <a-radio value="11">东北话</a-radio>
                            </a-radio-group>
                            <a-radio-group v-model:value="language" v-if="voice === '1'">
                                <a-radio value="1">男声1</a-radio>
                                <a-radio value="2">男声2</a-radio>
                                <a-radio value="3">男声3</a-radio>
                                <a-radio value="4">男声4</a-radio>
                                <a-radio value="5">男声5</a-radio>
                                <a-radio value="6">男声6</a-radio>
                                <a-radio value="7">童声</a-radio>
                                <a-radio value="8">东北话</a-radio>
                                <a-radio value="9">天津话</a-radio>
                            </a-radio-group>
                        </a-form-item>
                        <a-form-item label="添加到语料">
                            <a-radio-group v-model:value="type">
                                <a-radio value="1">测试语料</a-radio>
                                <a-radio value="2">唤醒语料</a-radio>
                                <a-radio value="3">干扰语料</a-radio>
                            </a-radio-group>
                        </a-form-item>
                        <a-form-item label="标签">
                            <a-input v-model:value="label" placeholder="请输入标签" />
                        </a-form-item>
                        <a-form-item label="预期结果">
                            <a-input v-model:value="expectResult" placeholder="请输入预期结果" />
                        </a-form-item>
                        <a-form-item label="是否添加语气助词">
                            <a-select v-model:value="is_tone">
                                <a-select-option :value="true">是</a-select-option>
                                <a-select-option :value="false">否</a-select-option>
                            </a-select>
                        </a-form-item>
                        <a-form-item>
                            <a-button type="primary" @click="synthesizeAudio" :loading="isSynthesizing">合成</a-button>
                        </a-form-item>
                    </a-form>
                </a-card>
            </a-col>
            <a-col :span="12">
                <a-card title="合成音频列表" class="card" style="height: calc(100vh - 8rem); overflow-y: auto;">
                    <div class="flex flex-end gap-[1rem]">
                        <a-button type="primary" @click="gotoBatch" style="margin-bottom: 1rem;">批量合成</a-button>
                        <el-upload ref="uploadRef" :auto-upload="false" :on-change="batchImport"
                            v-model:file-list="file_list" limit="1" :show-file-list="false" accept=".xls, .xlsx, .csv">
                            <template #trigger>
                                <a-button type="primary" style="transform: translateY(-8px);">从文件导入</a-button>
                            </template>
                        </el-upload>
                    </div>

                    <a-table :columns="columns" :dataSource="synthesizedAudios" :pagination="{ pageSize: 10 }" bordered
                        size="small">
                        <template #bodyCell="{ column, record }">
                            <template v-if="column.key === 'action'">
                                <a-button type="link" style="color: #de8dcc" @click="playAudio(record)">试听</a-button>
                            </template>
                            <template v-if="column.key === 'id'">
                                {{ record.corpus_id }}
                            </template>
                            <template v-else-if="column.key === 'text'">
                                <a-tooltip>
                                    <div
                                        style="font-weight: bold;  width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                        {{ record.text }}
                                    </div>
                                    <template #title>{{ record.text }}</template>
                                </a-tooltip>

                            </template>
                            <template v-else-if="column.key === 'audio_url'">
                                <div style="max-width: 300px; text-overflow: ellipsis;">
                                    {{ record.audio_url }}
                                </div>
                            </template>
                            <template v-else-if="column.key === 'expect_result'">
                                {{ record.expect_result }}
                            </template>
                        </template>
                    </a-table>
                </a-card>
            </a-col>
        </a-row>
    </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { http } from '@renderer/http';
import { useRouter } from 'vue-router';
import { ElMessage, UploadProps } from 'element-plus';
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
const router = useRouter();
const text = ref('');
const voice = ref('1'); // 默认选中第一个选项
const language = ref('1'); // 默认选中第一个选项
const type = ref('1');
const is_tone = ref(false); // 新增 is_tone 字段
const label = ref('tts');
const expectResult = ref(''); // 新增 expectResult 字段
const isSynthesizing = ref(false);
const synthesizedAudios = ref([]);
const file_list = ref([]);


const gotoBatch = () => {
    router.push('/batchSynthesize');
}

const columns = [
    { title: 'ID', dataIndex: 'corpus_id', key: 'id' },
    { title: '文本', dataIndex: 'text', key: 'text' },
    { title: '音频URL', dataIndex: 'audio_url', key: 'audio_url' },
    { title: '预期结果', dataIndex: 'expect_result', key: 'expect_result' }, // 新增列
    {
        title: '操作',
        key: 'action',
        width: '18%',
        scopedSlots: { customRender: 'action' },
    },
];

const fetchSynthesizedAudios = async () => {
    try {
        const response = await http.post('/synthesize/synthesize_list', {});
        synthesizedAudios.value = response.data;
    } catch (error) {
        console.error('Failed to fetch synthesized audios:', error);
    }
};

const synthesizeAudio = async () => {
    if (!text.value) {
        alert('请填写语料文本');
        return;
    }

    isSynthesizing.value = true;

    try {
        const response = await http.post('/synthesize/process_synthesize', {
            text: text.value,
            voice: parseInt(voice.value),
            language: parseInt(language.value),
            type: type.value,
            name: String(Date.now()),
            label: label.value,
            is_tone: is_tone.value, // 新增 is_tone 字段
            expect_result: expectResult.value, // 新增 expect_result 字段
        });

        if (response.success) {
            fetchSynthesizedAudios();
        } else {
            alert('合成失败');
        }
    } catch (error) {
        console.error('Failed to synthesize audio:', error);
        alert('合成失败');
    } finally {
        isSynthesizing.value = false;
    }
};

onMounted(() => {
    fetchSynthesizedAudios();
});

const batchImport: UploadProps['onChange'] = async (file) => {
    const formData = new FormData();
    formData.append('info', JSON.stringify({ category: 'synthesize' }));
    formData.append('file', file.raw);
    try {
        const response = await http.post(`/synthesize/batch_import`, formData);

        if (response.status === 'success') {
            ElMessage.success('导入成功，请等待批量处理');
        }
    } catch (error) {
        console.error("Upload failed: ", error);
    }
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
</style>