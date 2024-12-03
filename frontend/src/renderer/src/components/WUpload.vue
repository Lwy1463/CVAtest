<template>
  <el-upload
    ref="uploadRef"
    :auto-upload="false"
    :on-change="onBeforeUpload"
    :show-file-list="false"
    :accept="acceptType"
  >
    <template #trigger>
      <el-button plain>
        <el-icon class="mr-[5px]">
          <Upload />
        </el-icon>
        <slot> 上传文件 </slot>
      </el-button>
    </template>
  </el-upload>
</template>

<script setup lang="ts">
import { PropType } from 'vue'
import { ElMessage, UploadProps, UploadUserFile, ElButton } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { useProductFetch } from '../views/product/useProductFetch'

const props = defineProps({
  acceptType: {
    type: String,
    default: '.doc,.docx,.pdf'
  },
  projInfo: {
    type: Object,
    default: () => ({})
  },
  category: {
    type: String as PropType<
      'main_docx' | 'dbc_data' | 'mappings_1' | 'mappings_2' | 'mappings_3' | 'testcase'
    >,
    default: 'main_docx'
  }
})

const emit = defineEmits(['on-upload'])

const { handler } = useProductFetch()
const onBeforeUpload: UploadProps['onChange'] = async (file) => {
  const formData = new FormData()
  const info = new Blob([
    JSON.stringify({ db_id: props.projInfo['_id']['$oid'], category: props.category })
  ])
  formData.append('user_file', file.raw as File)
  formData.append('info', info)
  const res: any = await handler.UploadFile(formData)
  emit('on-upload', res, file)
}
</script>

<style scoped></style>
