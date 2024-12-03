<template>
    <a-table :columns="columns" :dataSource="pagedSubResults" :rowKey="record => record.result_id" bordered size="small" class="test-results-table" :pagination="false" :expand-column-width="50">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'time'">
          {{ new Date(record.time).toLocaleString() }}
        </template>
        <template v-else-if="column.key === 'result'">
          {{ record.result }}
        </template>
        <template v-else-if="column.key === 'action'">
          <a-button type="link" @click="handleAction(record)">详情</a-button>
        </template>
      </template>
    </a-table>
    <a-pagination v-model:current="currentPage" :total="totalResults" :pageSize="pageSize" show-less-items @change="onPageChange" style="margin-top: 20px; text-align: center;" />
  
    <!-- 弹窗 -->
    <a-modal v-model:visible="visible" title="详细信息" @ok="handleOk" width="60%" height="60vh">
      <div style="max-height: 60vh; overflow: auto;">
        <a-card v-for="(item, index) in currentSublist" :key="index" style="margin-bottom: 20px;" :title="'第' + (index + 1) + '轮'">
          <div style="display: flex; gap: 2rem">
            <a-image :src="getStaticPictureUrl(item.image)" alt="图片" style="max-height: 200px; max-width: 50%; height: auto;" :preview="true" />
            <audio :src="getStaticAudioUrl(item.mic_audio_url)" controls style="max-width: 100%; height: auto;"></audio>
            <a-col :span="6">
              <a-statistic title="测试结果" :precision="2" :value="item.result" />
            </a-col>
          </div>
        </a-card>
      </div>
    </a-modal>
  </template>
  
  <script setup lang="ts">
  import { ref, computed, toRef } from 'vue';
  
  const defaultData = [
    {
      "project_id": "project_1",
      "plan_id": "plan_1",
      "multicorpus_id": "EnN3q2",
      "turn_id": 1,
      "result": null,
      "reason": null,
      "success_rate": null,
      "time": "2024-12-02T14:45:05.271751",
      "sub_result": [
        {
          "result_id": "result_1",
          "time": "2024-12-02T14:44:26.699237",
          "corpus_id": "testcorpus_1",
          "test_scenario": "continuous-dialogue-interaction",
          "text": "你好",
          "result": null,
          "image": "/Users/luotianyou/CVAtest/backend/photo/xQ9rEJ/制作武侠立绘.png",
          "score": -1,
          "asr_result": "你好",
          "mic_audio_url": "/Users/dlh/Desktop/zhaoshang/CVAtest/backend/mic_audio/project_1/1/plan_1/testcorpus_1/testcorpus_1_mic_0_full.wav",
          "ocr_pic_url": "",
          "ocr_result": "",
          "ocr_accuracy_rate": 1.0,
          "relative_interval": 2,
          "response_time": 2.363,
          "expect_result": "你好"
        },
        {
          "result_id": "result_2",
          "time": "2024-12-02T14:45:05.268328",
          "corpus_id": "testcorpus_2",
          "test_scenario": "continuous-dialogue-interaction",
          "text": "我很好",
          "result": null,
          "image": "/Users/luotianyou/CVAtest/backend/photo/xQ9rEJ/制作武侠立绘.png",
          "score": -1,
          "asr_result": "",
          "mic_audio_url": "/Users/dlh/Desktop/zhaoshang/CVAtest/backend/mic_audio/project_1/1/plan_1/testcorpus_2/testcorpus_2_mic_0_full.wav",
          "ocr_pic_url": "",
          "ocr_result": "",
          "ocr_accuracy_rate": 1.0,
          "relative_interval": 2,
          "response_time": 0.299,
          "expect_result": "我很好"
        },
        {
          "result_id": "result_1",
          "time": "2024-12-02T14:44:26.699237",
          "corpus_id": "testcorpus_1",
          "test_scenario": "continuous-dialogue-interaction",
          "text": "你好",
          "result": null,
          "image": "/Users/luotianyou/CVAtest/backend/photo/xQ9rEJ/制作武侠立绘.png",
          "score": -1,
          "asr_result": "你好",
          "mic_audio_url": "/Users/dlh/Desktop/zhaoshang/CVAtest/backend/mic_audio/project_1/1/plan_1/testcorpus_1/testcorpus_1_mic_0_full.wav",
          "ocr_pic_url": "",
          "ocr_result": "",
          "ocr_accuracy_rate": 1.0,
          "relative_interval": 2,
          "response_time": 2.363,
          "expect_result": "你好"
        },
        {
          "result_id": "result_2",
          "time": "2024-12-02T14:45:05.268328",
          "corpus_id": "testcorpus_2",
          "test_scenario": "continuous-dialogue-interaction",
          "text": "我很好",
          "result": null,
          "image": "/Users/luotianyou/CVAtest/backend/photo/xQ9rEJ/制作武侠立绘.png",
          "score": -1,
          "asr_result": "",
          "mic_audio_url": "/Users/dlh/Desktop/zhaoshang/CVAtest/backend/mic_audio/project_1/1/plan_1/testcorpus_2/testcorpus_2_mic_0_full.wav",
          "ocr_pic_url": "",
          "ocr_result": "",
          "ocr_accuracy_rate": 1.0,
          "relative_interval": 2,
          "response_time": 0.299,
          "expect_result": "我很好"
        }
      ]
    }
  ]
  
  const currentPage = ref(1);
  const pageSize = ref(6);
  const visible = ref(false);
  const currentSublist = ref([]);
  
  const props = defineProps({
    testResults: {
      type: Array,
      required: true
    },
    previewImage: {
      type: Function,
      required: true
    },
  });
  const testResults = toRef(props, 'testResults');
  
  const sub_result_list = computed(() => {
    return testResults.value.flatMap((testResult, index) => {
      const subResults = (testResult?.sub_result || []).map((subResult, subIndex) => {
        return {
          ...subResult,
          index: index + 1, // 分配 index，从 1 开始
          rowSpan: subIndex === 0 ? (testResult?.sub_result || []).length : 0 // 计算 rowSpan
        };
      });
      return subResults;
    });
  });
  
  const totalResults = computed(() => sub_result_list.value.length);
  
  const pagedSubResults = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value;
    const end = start + pageSize.value;
    return sub_result_list.value.slice(start, end);
  });
  
  const onPageChange = (page: number) => {
    currentPage.value = page;
  };
  
  const handleAction = (record) => {
    const sublist = testResults.value.find(result => result.sub_result[0].result_id === record.result_id)?.sub_result;
    currentSublist.value = sublist;
    visible.value = true;
  };
  
  const handleOk = () => {
    visible.value = false;
  };
  
  const columns = [
    { title: '时间', dataIndex: 'time', key: 'time', align: 'center', customCell: (record, index) => ({ rowSpan: record.rowSpan }) },
    { title: '语料文本', dataIndex: 'text', key: 'text', align: 'center' },
    { title: '语音响应', dataIndex: 'asr_result', key: 'asr_result', align: 'center' },
    { title: '测试结果', dataIndex: 'result', key: 'result', align: 'center', customCell: (record, index) => ({ rowSpan: record.rowSpan }) },
    { title: '操作', dataIndex: 'action', key: 'action', align: 'center', customCell: (record, index) => ({ rowSpan: record.rowSpan }) },
  ];
  
  const getStaticAudioUrl = (url) => {
    if (process.env.NODE_ENV === 'production') {
      return '/mic_static/' + (url.replaceAll('\\', '/').split('mic_audio')?.[1] || '').replace('.pcm', '.wav');
    } else {
      return 'http://127.0.0.1:8080/mic_static/' + (url.replaceAll('\\', '/').split('mic_audio')?.[1] || '').replace('.pcm', '.wav');
    }
  }
  
  const getStaticPictureUrl = (url) => {
    if (process.env.NODE_ENV === 'production') {
      return '/photo/' + (url.replaceAll('\\', '/').split('photo')?.[1] || '');
    } else {
      return 'http://127.0.0.1:8080/photo/' + (url.replaceAll('\\', '/').split('photo')?.[1] || '');
    }
  }
  </script>