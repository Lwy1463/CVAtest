<template>
    <a-table :columns="columns" :dataSource="pagedTestResults" :rowKey="record => record.result_id" bordered
        size="small" class="test-results-table" :pagination="false" :expand-column-width="50">
        <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'time'">
                {{ new Date(record.time).toLocaleString() }}
            </template>
            <template v-else-if="column.key === 'result'">
                {{ record.result }}
            </template>
            <template v-else-if="column.key === 'ocr_pic_url'">
                <a @click="previewImage(record.ocr_pic_url)">图片</a>
            </template>
            <template v-else-if="column.key === 'image'">
                <a @click="previewImage(record.image)">图片</a>
            </template>
        </template>
        <template #expandedRowRender="{ record }">
            <a-row :gutter="16">
                <a-col :span="12">
                    <p><strong>OCR 结果:</strong> {{ record.ocr_result }}</p>
                    <p><strong>OCR 准确率:</strong> {{ String(record.ocr_accuracy_rate) }}</p>
                </a-col>
                <a-col :span="12">
                    <p><strong>得分:</strong> {{ record.score }}</p>
                    <p><strong>响应时间:</strong> {{ parseFloat(record.response_time) < 0 ? '未响应' : record.response_time
                            }}</p>
                            <p><strong>录音:</strong> <audio :src="getStaticUrl(record.mic_audio_url)" controls></audio>
                            </p>
                </a-col>
            </a-row>
        </template>
    </a-table>
    <a-pagination v-model:current="currentPage" :total="totalResults" :pageSize="pageSize" show-less-items
        @change="onPageChange" style="margin-top: 20px; text-align: center;" />
</template>
<script setup lang="ts">
import { ref, computed, toRef} from 'vue';
const currentPage = ref(1);
const pageSize = ref(6);

const props = defineProps({
    testResults: {
        type: Array,
        required: true
    },
    previewImage: {
        type: Function,
        required: true
    },
})

const testResults = toRef(props, 'testResults');
const totalResults = computed(() => testResults.value.length);

const pagedTestResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return testResults.value.slice(start, end);
});

const onPageChange = (page: number) => {
  currentPage.value = page;
};

const columns = [
  { title: '时间', dataIndex: 'time', key: 'time', align: 'center' },
  { title: '语料场景', dataIndex: 'scene', key: 'scene', align: 'center' },
  { title: '语料文本', dataIndex: 'text', key: 'text', align: 'center' },
  { title: '语音转文字识别结果', dataIndex: 'asr_result', key: 'asr_result', align: 'center' },
  { title: 'OCR 图片', dataIndex: 'ocr_pic_url', key: 'ocr_pic_url', align: 'center' },
  { title: '测试结果', dataIndex: 'result', key: 'result', align: 'center' },
  { title: '结果图片', dataIndex: 'image', key: 'image', align: 'center' },
  { title: '预期结果', dataIndex: 'expect_result', key: 'expect_result', align: 'center' }
];




const getStaticUrl = (url) => {
  if (process.env.NODE_ENV === 'production') {
    return '/mic_static/' + (url.replaceAll('\\', '/').split('mic_audio')?.[1] || '').replace('.pcm', '.wav');
  } else {
    return 'http://127.0.0.1:8080/mic_static/' + (url.replaceAll('\\', '/').split('mic_audio')?.[1] || '').replace('.pcm', '.wav');
  }
}
</script>