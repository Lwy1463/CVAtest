<template>
    <a-modal v-model:visible="modalVisible" title="泛化结果处理" width="80vw" height="80vh" :footer="null">
        <div style="margin-bottom: 20px;">
            <a-radio-group v-model:value="synthesisOption">
                <a-radio value="synthesize">合成音频</a-radio>
                <a-radio value="no_synthesize">不合成音频，只创建语料</a-radio>
            </a-radio-group>
        </div>
        <div class="table-header">
            <div class="table-cell" style="flex: 0.35">序号</div>
            <div class="table-cell" style="flex: 1.65">语料文本</div>
            <div class="table-cell">发声人</div>
            <div class="table-cell">语种</div>
            <div class="table-cell">类型</div>
            <div class="table-cell">标签</div>
            <div class="table-cell">预期结果</div> <!-- 新增列 -->
            <div class="table-cell">操作</div>
        </div>
        <div class="table-content">
            <div v-for="(item, index) in batchData" :key="index" class="table-row">
                <div class="table-cell" style="flex: 0.35">{{ index + 1 }}</div>
                <div class="table-cell" style="flex: 1.65">
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
                    <a-button type="primary" @click="removeRow(index)" shape="circle">-</a-button>
                    <a-button type="primary" @click="addRow(index)" shape="circle" style="margin-left: 10px;">+</a-button>
                </div>
            </div>
        </div>

        <a-button type="primary" @click="synthesizeBatchAudio" :loading="isSynthesizing" style="margin-top: 20px;">确定</a-button>
    </a-modal>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue';
import { http } from '@renderer/http';
import { v4 as uuidv4 } from 'uuid';
import { ElLoading } from 'element-plus';

const props = defineProps<{
    visible: boolean;
    batchData: Array<{ text: string; voice: string; language: string; type: string; label: string; expect_result: string }>;
}>();

const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'update:batchData', value: Array<{ text: string; voice: string; language: string; type: string; label: string; expect_result: string }>): void;
    (e: 'synthesize'): void;
}>();

const modalVisible = ref(props.visible);
const isSynthesizing = ref(false);
const synthesisOption = ref('synthesize'); // 默认选择合成音频

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
    props.batchData.splice(index + 1, 0, { text: '', voice: '1', language: '1', type: '1', label: 'tts', expect_result: '' }); // 添加 expect_result 字段
    emit('update:batchData', props.batchData);
};

const removeRow = (index: number) => {
    props.batchData.splice(index, 1);
    emit('update:batchData', props.batchData);
};

const handleVoiceChange = (index: number) => {
    const item = props.batchData[index];
    item.language = item.voice === '1' ? '1' : '1'; // 默认选择第一个选项
    emit('update:batchData', props.batchData);
};

const synthesizeBatchAudio = async () => {
    const batchDataList = props.batchData.map(item => ({
        text: item.text,
        voice: parseInt(item.voice),
        language: parseInt(item.language),
        type: item.type,
        label: item.label, // 添加 label 字段
        expect_result: item.expect_result, // 添加 expect_result 字段
        name: uuidv4().replace(/-/g, '').substring(0, 16) // 生成16位字母的UUID
    }));

    if (batchDataList.some(item => !item.text)) {
        alert('请填写所有语料文本');
        return;
    }

    isSynthesizing.value = true;

    try {
        const response = await http.post('/synthesize/batch_process_synthesize', { list: batchDataList, synthesisOption: synthesisOption.value });

        if (response.success) {
            alert('批量合成成功');
            emit('update:batchData', [{ text: '', voice: '1', language: '1', type: '1', label: 'tts', expect_result: '' }]); // 重置数据
            modalVisible.value = false;
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

watch(() => props.visible, (newVal) => {
    modalVisible.value = newVal;
});

watch(modalVisible, (newVal) => {
    emit('update:visible', newVal);
});
</script>

<style scoped>
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