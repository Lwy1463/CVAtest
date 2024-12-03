<template>
    <div class="container">
        <a-breadcrumb style="margin-bottom: 20px;">
            <a-breadcrumb-item @click="gotoSynthesize"><a>合成语料</a></a-breadcrumb-item>
            <a-breadcrumb-item>批量合成</a-breadcrumb-item>
        </a-breadcrumb>
        <a-card title="批量合成音频" class="card" style="height: calc(100vh - 12rem)">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div></div>
                <a-button type="primary" @click="showGeneralizeModal">泛化</a-button>
            </div>
            <div class="table-header">
                <div class="table-cell" style="flex: 0.35">序号</div>
                <div class="table-cell">语料文本</div>
                <div class="table-cell">发声人</div>
                <div class="table-cell">语种</div>
                <div class="table-cell">类型</div>
                <div class="table-cell">标签</div>
                <div class="table-cell">预期结果</div> <!-- 新增列 -->
                <div class="table-cell">是否添加语气助词</div> <!-- 新增列 -->
                <div class="table-cell">操作</div>
            </div>
            <div class="table-content">
                <div v-for="(item, index) in batchData" :key="index" class="table-row">
                    <div class="table-cell" style="flex: 0.35">{{ index + 1 }}</div>
                    <div class="table-cell">
                        <a-input v-model:value="item.text" placeholder="请输入语料文本" />
                    </div>
                    <div class="table-cell">
                        <a-select v-model:value="item.voice" style="width: 100%" @change="handleVoiceChange(index)">
                            <a-select-option value="1">男声</a-select-option>
                            <a-select-option value="2">女声</a-select-option>
                        </a-select>
                    </div>
                    <div class="table-cell">
                        <a-select v-model:value="item.language" style="width: 100%">
                            <a-select-option v-for="option in getLanguageOptions(item.voice)" :key="option.value" :value="option.value">{{ option.label }}</a-select-option>
                        </a-select>
                    </div>
                    <div class="table-cell">
                        <a-select v-model:value="item.type" style="width: 100%">
                            <a-select-option value="1">测试语料</a-select-option>
                            <a-select-option value="2">唤醒语料</a-select-option>
                            <a-select-option value="3">干扰语料</a-select-option>
                        </a-select>
                    </div>
                    <div class="table-cell">
                        <a-input v-model:value="item.label" placeholder="标签" />
                    </div>
                    <div class="table-cell">
                        <a-input v-model:value="item.expect_result" placeholder="预期结果" /> <!-- 新增列 -->
                    </div>
                    <div class="table-cell">
                        <a-select v-model:value="item.is_tone" style="width: 100%"> <!-- 新增列 -->
                            <a-select-option :value="true">是</a-select-option>
                            <a-select-option :value="false">否</a-select-option>
                        </a-select>
                    </div>
                    <div class="table-cell">
                        <a-button type="primary" @click="removeRow(index)" shape="circle">-</a-button>
                        <a-button type="primary" @click="addRow(index)" shape="circle" style="margin-left: 10px;">+</a-button>
                    </div>
                </div>
            </div>
            <a-button type="primary" @click="synthesizeBatchAudio" :loading="isSynthesizing" style="margin-top: 20px;">确定</a-button>
        </a-card>

        <!-- 泛化弹窗 -->
        <a-modal v-model:visible="generalizeModalVisible" title="泛化" @ok="handleGeneralizeOk">
            <a-form layout="vertical">
                <a-form-item label="泛化文本">
                    <a-input v-model:value="generalizeText" placeholder="请输入泛化文本" />
                </a-form-item>
                <a-form-item label="发声人">
                    <a-select v-model:value="generalizeVoice" style="width: 100%;">
                        <a-select-option value="1">男声</a-select-option>
                        <a-select-option value="2">女声</a-select-option>
                    </a-select>
                </a-form-item>
                <a-form-item label="语种">
                    <a-select v-model:value="generalizeLanguage" style="width: 100%;">
                        <a-select-option v-for="option in getLanguageOptions(generalizeVoice)" :key="option.value" :value="option.value">{{ option.label }}</a-select-option>
                    </a-select>
                </a-form-item>
                <a-form-item label="类型">
                    <a-select v-model:value="generalizeType" style="width: 100%;">
                        <a-select-option value="1">测试语料</a-select-option>
                        <a-select-option value="2">唤醒语料</a-select-option>
                        <a-select-option value="3">干扰语料</a-select-option>
                    </a-select>
                </a-form-item>
                <a-form-item label="标签">
                    <a-input v-model:value="generalizeLabel" placeholder="标签" />
                </a-form-item>
                <a-form-item label="预期结果">
                    <a-input v-model:value="generalizeExpectResult" placeholder="预期结果" /> <!-- 新增列 -->
                </a-form-item>
                <a-form-item label="是否添加语气助词">
                    <a-select v-model:value="generalizeIsTone" style="width: 100%;"> <!-- 新增列 -->
                        <a-select-option :value="true">是</a-select-option>
                        <a-select-option :value="false">否</a-select-option>
                    </a-select>
                </a-form-item>
            </a-form>
        </a-modal>
    </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import { http } from '@renderer/http';
import { v4 as uuidv4 } from 'uuid';
import { ElLoading } from 'element-plus';
import { useRouter } from 'vue-router';

const router = useRouter();

const batchData = ref([
    { text: '', voice: '1', language: '1', type: '1', label: 'tts', expect_result: '', is_tone: false }, // 添加 expect_result 和 is_tone 字段
]);

const isSynthesizing = ref(false);
const generalizeModalVisible = ref(false);
const generalizeText = ref('');
const generalizeVoice = ref('1');
const generalizeLanguage = ref('1');
const generalizeType = ref('1');
const generalizeLabel = ref('tts');
const generalizeExpectResult = ref(''); // 新增 generalizeExpectResult 字段
const generalizeIsTone = ref(false); // 新增 generalizeIsTone 字段

const femaleVoiceOptions = [
    { value: '1', label: '女声1' },
    { value: '2', label: '女声2' },
    { value: '3', label: '女声3' },
    { value: '4', label: '女声4' },
    { value: '5', label: '女声5' },
    { value: '6', label: '女声6' },
    { value: '7', label: '女声7' },
    { value: '8', label: '童声' },
    { value: '9', label: '东北话'},
    { value: '10', label: '天津话'}
];

const maleVoiceOptions = [
    { value: '1', label: '男声1' },
    { value: '2', label: '男声2' },
    { value: '3', label: '男声3' },
    { value: '4', label: '男声4' },
    { value: '5', label: '男声5' },
    { value: '6', label: '男声6' },
    { value: '7', label: '童声' },
    { value: '8', label: '东北话'},
    { value: '9', label: '天津话'}
];

const getLanguageOptions = computed(() => (voice: string) => {
    return voice === '1' ? maleVoiceOptions : femaleVoiceOptions;
});

const addRow = (index: number) => {
    batchData.value.splice(index + 1, 0, { text: '', voice: '1', language: '1', type: '1', label: 'tts', expect_result: '', is_tone: false }); // 添加 expect_result 和 is_tone 字段
};

const removeRow = (index: number) => {
    batchData.value.splice(index, 1);
};

const handleVoiceChange = (index: number) => {
    const item = batchData.value[index];
    item.language = item.voice === '1' ? '1' : '1'; // 默认选择第一个选项
};

const synthesizeBatchAudio = async () => {
    const batchDataList = batchData.value.map(item => ({
        text: item.text,
        voice: parseInt(item.voice),
        language: parseInt(item.language),
        type: item.type,
        label: item.label, // 添加 label 字段
        expect_result: item.expect_result, // 添加 expect_result 字段
        is_tone: item.is_tone, // 添加 is_tone 字段
        name: uuidv4().replace(/-/g, '').substring(0, 16) // 生成16位字母的UUID
    }));

    if (batchDataList.some(item => !item.text)) {
        alert('请填写所有语料文本');
        return;
    }

    isSynthesizing.value = true;

    try {
        const response = await http.post('/synthesize/batch_process_synthesize', { list: batchDataList });

        if (response.success) {
            alert('批量合成成功');
            batchData.value = [{ text: '', voice: '1', language: '1', type: '1', label: 'tts', expect_result: '', is_tone: false }]; // 重置数据
        } else {
            alert('批量合成失败');
        }
    } catch (error) {
        console.error('Failed to batch synthesize audio:', error);
        alert('批量合成失败');
    } finally {
        isSynthesizing.value = false;
    }
};

const showGeneralizeModal = () => {
    generalizeModalVisible.value = true;
};

const handleGeneralizeOk = async () => {
    if (!generalizeText.value) {
        alert('请输入泛化文本');
        return;
    }

    // 显示全局 loading
    const loadingInstance = ElLoading.service({ target: '.container', text: '泛化中...' });

    try {
        const response = await http.post('/synthesize/corpus_generalizate', { text: generalizeText.value });

        if (response.list) {
            const generalizedList = response.list.map((text: string) => ({
                text,
                voice: generalizeVoice.value,
                language: generalizeLanguage.value,
                type: generalizeType.value,
                label: generalizeLabel.value,
                expect_result: generalizeExpectResult.value, // 添加 expect_result 字段
                is_tone: generalizeIsTone.value // 添加 is_tone 字段
            }));

            batchData.value = [...generalizedList];
            alert('泛化成功');
        } else {
            alert('泛化失败');
        }
    } catch (error) {
        console.error('Failed to generalize corpus:', error);
        alert('泛化失败');
    } finally {
        generalizeModalVisible.value = false;
        // 关闭全局 loading
        loadingInstance.close();
    }
};

const gotoSynthesize = () => {
    router.push('/synthesize');
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

.table-header .table-cell {
    font-weight: bold;
}

.table-content {
    max-height: calc(100vh - 24rem);
    overflow-y: auto;
}
</style>