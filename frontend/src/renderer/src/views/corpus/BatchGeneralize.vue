<template>
    <a-modal v-model:visible="modalVisible" title="泛化" @ok="handleOk">
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
            <a-form-item label="标签">
                <a-input v-model:value="generalizeLabel" placeholder="标签" />
            </a-form-item>
        </a-form>
    </a-modal>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue';
import { http } from '@renderer/http';
import { ElLoading } from 'element-plus';

const props = defineProps<{
    visible: boolean;
    text: string;
    type: 'test' | 'wake'; // 新增 type 参数
}>();

const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'generalize-success', data: any): void;
    (e: 'generalize-error'): void;
}>();

const modalVisible = ref(props.visible);
const generalizeText = ref(props.text);
const generalizeVoice = ref('1');
const generalizeLanguage = ref('1');
const generalizeLabel = ref('tts');
const generalizeExpectResult = ref('');

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

watch(() => props.visible, (newVal) => {
    modalVisible.value = newVal;
});

watch(modalVisible, (newVal) => {
    emit('update:visible', newVal);
    if (newVal) {
        generalizeText.value = props.text;
    }
});

const typeMap = {
    'test': '1',
    'wake': '2'
}

const handleOk = async () => {
    if (!generalizeText.value) {
        alert('请输入泛化文本');
        return;
    }

    const loadingInstance = ElLoading.service({ target: '.container', text: '泛化中...' });

    try {
        const response = await http.post('/synthesize/corpus_generalizate', { text: generalizeText.value });

        if (response.list) {
            const generalizedList = response.list.map((text: string) => ({
                text,
                voice: generalizeVoice.value,
                language: generalizeLanguage.value,
                type: typeMap[props.type], // 使用传入的 type 参数
                label: generalizeLabel.value,
                expect_result: generalizeExpectResult.value
            }));

            emit('generalize-success', generalizedList);
        } else {
            emit('generalize-error');
        }
    } catch (error) {
        console.error('Failed to generalize corpus:', error);
        emit('generalize-error');
    } finally {
        modalVisible.value = false;
        loadingInstance.close();
    }
};
</script>