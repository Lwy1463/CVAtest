<template>
  <div style="display: flex; flex-direction: column; height: 100vh;">
    <!-- 面包屑导航 -->
    <a-breadcrumb style="margin: 1rem;">
      <a-breadcrumb-item>
        <a @click="goToExecution">项目执行</a>
      </a-breadcrumb-item>
      <a-breadcrumb-item>执行结果</a-breadcrumb-item>
    </a-breadcrumb>

    <div style="display: flex; flex: 1;">
      <!-- 左侧表格 -->
      <div style="flex: 2; padding: 1rem;">
        <a-card :bordered="false" class="review-card">
          <div class="review-header">
            测试结果
          </div>
          <InteractionTableWithTime v-if="['rouse', 'false-rouse', 'interaction'].includes(currentType)" :seekVideo="seekVideo" :preview-image="previewImage" :testResults="testResults"></InteractionTableWithTime>
          <InteractionMultiTable v-if="currentType === 'interaction-multi'" :testResults="testResults" :preview-image="previewImage"></InteractionMultiTable>
        </a-card>
      </div>
      <!-- 右侧视频播放器 -->
      <div style="flex: 1; padding: 1rem;">
        <a-card :bordered="false" class="video-card">
          <div class="video-header">
            视频播放
          </div>
          <video ref="videoPlayer" class="video-js" width="640" height="264"></video>
        </a-card>
      </div>
    </div>
    <!-- 图片预览模态框 -->
    <a-modal v-model:visible="imagePreviewVisible" :footer="null" @cancel="imagePreviewVisible = false">
      <img alt="图片错误" style="width: 100%" :src="imagePreviewUrl" />
    </a-modal>
    <!-- 复核结果模态框 -->
    <a-modal v-model:visible="reviewModalVisible" title="复核结果" @ok="handleReviewOk" @cancel="reviewModalVisible = false">
      <a-radio-group v-model:value="reviewResult">
        <a-radio value="通过">通过</a-radio>
        <a-radio value="不通过">不通过</a-radio>
        <a-radio value="不确定">不确定</a-radio>
      </a-radio-group>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { http } from '@renderer/http';
import { useProjectStore } from '@renderer/stores/useProject';
import { storeToRefs } from 'pinia';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import InteractionTableWithTime from './InteractionTableWithTime.vue';
import InteractionMultiTable from './InteractionMultiTable.vue';
import test from 'node:test';


const route = useRoute();
const router = useRouter();
const projectStore = useProjectStore();
const { projectDetail } = storeToRefs(projectStore);


const testResults = ref([]);
const videoUrl = ref('');
const videoPlayer = ref(null);
const imagePreviewVisible = ref(false);
const imagePreviewUrl = ref('');
const reviewModalVisible = ref(false);
const reviewResult = ref('');
const currentRecord = ref(null);
const currentType = ref('');

const columns = [
  { title: '时间', dataIndex: 'time', key: 'time', align: 'center' },

  { title: '语料场景', dataIndex: 'scene', key: 'scene', align: 'center' },
  { title: '语料文本', dataIndex: 'text', key: 'text', align: 'center' },
  { title: '语音转文字识别结果', dataIndex: 'asr_result', key: 'asr_result', align: 'center' },
  { title: 'OCR 图片', dataIndex: 'ocr_pic_url', key: 'ocr_pic_url', align: 'center' },
  { title: 'OCR 结果', dataIndex: 'ocr_result', key: 'ocr_result', align: 'center' },
  { title: 'OCR 准确率', dataIndex: 'ocr_accuracy_rate', key: 'ocr_accuracy_rate', align: 'center' },
  { title: '测试结果', dataIndex: 'result', key: 'result', align: 'center' },
  { title: '结果图片', dataIndex: 'image', key: 'image', align: 'center' },
  { title: '得分', dataIndex: 'score', key: 'score', align: 'center' },
  { title: '响应时间', dataIndex: 'response_time', key: 'response_time', align: 'center' },
  { title: '预期结果', dataIndex: 'expect_result', key: 'expect_result', align: 'center' },
  { title: '操作', key: 'operation', align: 'center' },
];

onMounted(async () => {
  const resultId = route.params.resultId;
  const response = await http.post('/test_project/get_test_info', { project_id: projectDetail.value.project_id, turn_id: localStorage.getItem('turn_id'), plan_id: localStorage.getItem('plan_id') });
  testResults.value = response.result_list || [];
  if (process.env.NODE_ENV === 'production') {
    videoUrl.value = `/static/${projectDetail.value.project_id}_${localStorage.getItem('turn_id')}.mp4`;
  } else {
    videoUrl.value = `http://127.0.0.1:8080/static/${projectDetail.value.project_id}_${localStorage.getItem('turn_id')}.mp4`;
  }

  if (videoUrl.value) {
    initVideoPlayer();
  }

  // 监听 showpic 事件
  window.electron.ipcRenderer.on('showpic', (event, { data }) => {
    const blob = new Blob([data], { type: 'image/jpeg' });
    const url = URL.createObjectURL(blob);
    imagePreviewUrl.value = url;
    imagePreviewVisible.value = true;
  });
  console.log(localStorage.getItem('result_type'));
  currentType.value = localStorage.getItem('result_type');
});

onUnmounted(() => {
  window.electron.ipcRenderer.removeAllListeners('showpic');
});

const initVideoPlayer = () => {
  if (videoPlayer.value) {
    const player = videojs(videoPlayer.value, {
      autoplay: true,
      controls: true,
      innerWidth: 480,
      innerHeight: 270,
      sources: [
        {
          src: videoUrl.value,
          type: 'video/mp4',
        },
      ],
      fluid: true, // 使视频播放器自适应容器大小
    });

    player.ready(() => {
      console.log('Player is ready');
    });
  }
};

const previewImage = (filePath) => {
  window.electron.ipcRenderer.send('getImage', filePath);
};



const seekVideo = (seconds) => {
  if (videoPlayer.value) {
    const player = videojs(videoPlayer.value);
    player.currentTime(seconds);
  }
};

const goToExecution = () => {
  router.push('/execution');
};

const showReviewModal = (record) => {
  currentRecord.value = record;
  reviewModalVisible.value = true;
};

const handleReviewOk = async () => {
  const { project_id } = projectDetail.value;
  const turn_id = localStorage.getItem('turn_id');
  const result_id = currentRecord.value.result_id;
  const result = reviewResult.value;

  try {
    const response = await http.post('/test_project/result_check', {
      project_id,
      turn_id,
      result_id,
      result,
    });

    if (response.success) {
      // 更新表格中的结果
      currentRecord.value.result = result;
      reviewModalVisible.value = false;
    } else {
      console.error('复核失败:', response.message);
    }
  } catch (error) {
    console.error('复核失败:', error);
  }
};
</script>

<style scoped>
.review-card,
.video-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-height: 300px;
  /* 设置最小高度 */
  margin: 10px;
}

.review-header,
.video-header {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 1rem;
}

.review-table {
  width: 100%;
  table-layout: fixed;
}

.review-table th,
.review-table td {
  padding: 12px;
  text-align: center;
}

.review-table th {
  background-color: #fafafa;
  font-weight: bold;
}

.review-table tr:nth-child(even) {
  background-color: #fafafa;
}

.review-table tr:hover {
  background-color: #f0f5ff;
}

.video-js {
  width: 100%;
  height: auto;
}
</style>