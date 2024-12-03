<template>
  <div>
    <a-button type="primary" @click="showModal">生成报告</a-button>
    <a-modal
      v-model:visible="visible"
      title="生成测试报告"
      @ok="handleOk"
      @cancel="handleCancel"
      okText="生成"
      cancelText="取消"
    >
      <a-form :model="formData" :rules="rules" ref="formRef">
        <a-form-item label="报告名称" name="report_name">
          <a-input v-model:value="formData.report_name" />
        </a-form-item>
        <a-form-item label="报告编号" name="report_number">
          <a-input v-model:value="formData.report_number" />
        </a-form-item>
        <a-form-item label="检测单位" name="test_agency">
          <a-input v-model:value="formData.test_agency" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, defineProps, defineEmits } from 'vue';
import { useProjectStore } from '@renderer/stores/useProject';
import { storeToRefs } from 'pinia';
import { http } from '@renderer/http';
import { message } from 'ant-design-vue';

const props = defineProps({
  projectDetail: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['reportGenerated']);

const projectStore = useProjectStore();
const { projectDetail } = storeToRefs(projectStore);

const visible = ref(false);
const formRef = ref(null);

const formData = reactive({
  report_name: '',
  report_number: '',
  test_agency: '',
});

const rules = {
  report_name: [{ required: true, message: '请输入报告名称', trigger: 'blur' }],
  report_number: [{ required: true, message: '请输入报告编号', trigger: 'blur' }],
  test_agency: [{ required: true, message: '请输入检测单位', trigger: 'blur' }],
};

const showModal = () => {
  visible.value = true;
};

const handleOk = () => {
  formRef.value.validate().then(async () => {
    const payload = {
      project_id: props.projectDetail.project_id,
      project_name: props.projectDetail.project_name,
      report_name: formData.report_name,
      report_number: formData.report_number,
      test_agency: formData.test_agency,
    };

    try {
      const response = await http.post('/report/generate_report', payload);
      message.success('报告生成成功');
      emit('reportGenerated', response.data.report_url);
      visible.value = false;
      formRef.value.resetFields();
    } catch (error) {
      message.error('报告生成失败，请重试');
    }
  }).catch(() => {
    message.error('请填写完整信息');
  });
};

const handleCancel = () => {
  visible.value = false;
  formRef.value.resetFields();
};
</script>

<style scoped>
/* 样式优化 */
.ant-form-item {
  margin-bottom: 16px;
}
</style>