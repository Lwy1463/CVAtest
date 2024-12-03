<script lang="ts" setup>
import { Download } from '@element-plus/icons-vue'
import { useProductFetch } from '../useProductFetch'
import { ElMessage } from 'element-plus'
import { useTagsStore } from '../../../stores/useTagsStore'

const store = useTagsStore()

const { DownloadFileLocal } = useProductFetch()
const downloadFile = (files: any = []) => {
  Promise.all(
    files.map((f: any) =>
      DownloadFileLocal(
        store.current!._id.$oid,
        f?.object_name,
        f?.file_name,
        store.current!.download_path
      )
    )
  )
    .then((responses) => {
      ElMessage.success(`下载${responses.length}个文件，保存到${store.current!.download_path}`)
    })
    .catch(() => {
      ElMessage.error('下载失败')
    })
}
</script>

<template>
  <template v-if="store.current?.files">
    <div class="flex items-center justify-between">
      <p>测试文档下载({{ store.current!._allFile.length }})</p>
      <el-icon class="cursor-pointer" @click="downloadFile(store.current?._allFile || [])">
        <Download />
      </el-icon>
    </div>
    <div class="flex items-center justify-between mt-[10px] text-[#666]">
      <p class="text-[12px]">
        需求文档下载({{ store.current!.files?.main_docx?.split_files.length || 0 }})
      </p>
      <el-icon
        class="cursor-pointer"
        @click="downloadFile(store.current!.files.main_docx?.split_files || [])"
      >
        <Download />
      </el-icon>
    </div>
    <div class="flex items-center justify-between mt-[10px] text-[#666]">
      <p class="text-[12px]">用例文档下载({{ store.current!._exampleFileList.length }})</p>
      <el-icon class="cursor-pointer" @click="downloadFile(store.current!._exampleFileList)">
        <Download />
      </el-icon>
    </div>
    <div class="flex items-center justify-between mt-[10px] text-[#666]">
      <p class="text-[12px]">脚本文档下载({{ store.current!._scriptFileList.length }})</p>
      <el-icon class="cursor-pointer" @click="downloadFile(store.current!._scriptFileList)">
        <Download />
      </el-icon>
    </div>
  </template>
</template>

<style lang="scss" scoped></style>
