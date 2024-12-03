<template>
  <p style="font-weight: bold; margin-bottom: 1rem">请先上传知识文档</p>
  <div class="upload-mapping-excel-container">
    <p class="text-[#999] mb-[16px]">支持.pdf文件上传</p>
    <WUpload
      :acceptType="acceptType"
      :projInfo="projInfo"
      category="mappings_1"
      class="mt-[6px] mb-2"
      @on-upload="handleUpload"
      >上传知识文档</WUpload
    >
    <div v-if="projInfo.files?.mappings_1" class="flex-between">
      <div class="flex items-center gap-[5px]">
        <img alt="" src="/svgs/pdf.svg" />
        <el-tooltip :content="projInfo.files?.mappings_1?.file_name ?? ''" effect="light">
          <p class="line-clamp-1 w-[150px]">{{ projInfo.files?.mappings_1?.file_name ?? '' }}</p>
        </el-tooltip>

      </div>
      <slot name="download1">
        <el-icon class="cursor-pointer">
          <Download />
        </el-icon>
      </slot>
    </div>
    <div v-if="projInfo.files?.mappings_3" class="flex-between">
      <div class="flex items-center gap-[5px]">
        <img alt="" src="/svgs/excel.svg" />
        <p class="line-clamp-1 w-[150px]">{{ projInfo.files?.mappings_3?.file_name ?? '' }}</p>
      </div>
      <slot name="download3">
        <el-icon class="cursor-pointer">
          <Download />
        </el-icon>
      </slot>
    </div>
    <div class="divider"></div>
    <!-- <ElButton :disabled="!canSubmit" type="primary" @click="generateMappingTable"
      >生成映射表</ElButton
    > -->
  </div>
</template>

<script lang="ts" setup>
import { Download } from '@element-plus/icons-vue'
import { ElButton, ElMessage } from 'element-plus'
import WUpload from './WUpload.vue'
import { computed, ref } from 'vue'
import { useTagsStore } from '@renderer/stores/useTagsStore'
import { useProductFetch } from '../views/product/useProductFetch'

const props = defineProps({
  projInfo: {
    type: Object,
    default: () => ({})
  },
  // 是否需要上传所有映射表
  isRequire: {
    type: Boolean,
    default: false
  }
})

const store = useTagsStore()
const emits = defineEmits(['on-upload'])

const { handler } = useProductFetch()

const acceptType = '.pdf'

const canSubmit = computed(() => {
  if (props.isRequire) {
    return (
      (store.current as any).files?.mappings_1 &&
      (store.current as any).files?.mappings_2 &&
      (store.current as any).files?.mappings_3
    )
  } else {
    return true
  }
})

const downloadTempLoading = ref(false)
const downloadTemp = async (e) => {
  if (downloadTempLoading.value) return
  e.preventDefault()
  downloadTempLoading.value = true
  handler
    .DownloadTemplate(store.current!.download_path)
    .then(() => {
      ElMessage.success(`下载成功, 文件已保存到${store.current!.download_path}`)
    })
    .catch(() => {
      ElMessage.error('下载失败')
    })
    .finally(() => {
      downloadTempLoading.value = false
    })
}

const handleUpload = (status: string, file) => {
  if (status === 'OK') {
    emits('on-upload', status, file)
  }
}

// 生成映射表
const generateMappingTable = () => {
  handler.generateMappings(props.projInfo['_id']['$oid']).then((res: any) => {
    if (res?.code == 200) {
      handler.Detail((store.current as any)._id.$oid).then((detail) => {
        store.addTag(detail)
      })
      ElMessage.success('生成成功')
    } else {
      ElMessage.error('生成失败')
    }
  })
}
</script>

<style lang="scss" scoped>
.upload-mapping-excel-container {
  border-radius: 2px;
  border: 1px solid #ececec;
  background-color: #fff;
  padding: 7px 10px;
}

.divider {
  width: 100%;
  height: 1px;
  background-color: #ebebeb;
  margin-top: 10px;
  margin-bottom: 5px;
}
</style>
