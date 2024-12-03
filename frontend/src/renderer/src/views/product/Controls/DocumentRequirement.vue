<script lang="ts" setup>
import 'quill/dist/quill.snow.css'
import { onMounted, onUnmounted, ref } from 'vue'
import { ElMessage, ElMessageBox, UploadProps } from 'element-plus'
import { Delete, Download, Loading, Upload, Warning } from '@element-plus/icons-vue'
import SmtEmpty from '@renderer/components/SmtEmpty.vue'
import { DocumentWordEdit } from './DocumentWordEdit'
import { useProductFetch } from '../useProductFetch'
import { useTagsStore } from '../../../stores/useTagsStore'
import HTMLtoDOCX from 'html-to-docx';
//@ts-ignore

const store = useTagsStore()

const currentFile = ref()
const uploadRef = ref()

const { handler, DownloadFileLocal } = useProductFetch()

const downloadLoading = ref(false)
const downloadFileLocal = () => {
  downloadLoading.value = true
  DownloadFileLocal(
    store.current!._id.$oid,
    store.current!.files.main_docx.object_name,
    store.current!.files.main_docx.file_name,
    store.current!.download_path
  )
    .then(() => {
      ElMessage.success(`下载成功, 文件已保存到${store.current!.download_path}`)
    })
    .catch(() => {
      ElMessage.error('下载失败')
    })
    .finally(() => {
      downloadLoading.value = false
    })
}

const onBeforeUpload: UploadProps['onChange'] = async (file) => {
  const formData = new FormData()
  const info = new Blob([
    JSON.stringify({ db_id: store.current!['_id']['$oid'], category: 'main_docx' })
  ])
  formData.append('user_file', file.raw as File)
  formData.append('info', info)
  await handler.UploadFile(formData)
  handler.Detail(store.current!._id.$oid).then((detail) => {
    store.addTag(detail)
  })
}

const quillEditorRef = ref()
let documentWordEdit: DocumentWordEdit
onMounted(() => {
  documentWordEdit = new DocumentWordEdit(quillEditorRef.value)
})

//
const fileLoading = ref(false)
const onClickPreviewFile = (f: any) => {
  if (store.current?.status?.test_cases == 1) return
  if (fileLoading.value) return
  if (f.is_table === true) {
    return
  }
  fileLoading.value = true
  handler
    .DownloadFile(store.current!._id.$oid, f.url || f.object_name)
    .then((stream: any) => {
      const blob = new Blob([stream], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      })
      const file = new File([blob], f.name)
      documentWordEdit.docxToQuill(file)
      currentFile.value = f
    })
    .finally(() => {
      fileLoading.value = false
    })
}

const onSaveContent = () => {
  ElMessageBox.confirm('保存后会覆盖文件，是否确定？', '覆盖提示', {
    confirmButtonText: '是',
    cancelButtonText: '否',
    type: 'warning'
  }).then(() => {
    // documentWordEdit.quill.getSemanticHTML()
    HTMLtoDOCX(documentWordEdit.quill.getSemanticHTML()).then((data) => {
      const file = new File([data], currentFile.value.file_name, {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      })
      const formData = new FormData()
      const info = new Blob([
        JSON.stringify({
          db_id: store.current!['_id']['$oid'],
          category: 'split_docx',
          chunk_index: currentFile.value.chunk_index
        })
      ])

      formData.append('user_file', file)
      formData.append('info', info)
      handler.UploadFile(formData).then((res) => {
        if (res) {
          ElMessage.success('保存成功')
          handler.Detail(store.current!._id.$oid).then((detail) => {
            store.addTag(detail)
          })
        } else {
          ElMessage.error('保存失败')
        }
      })
    })
  })
}
window.electron.ipcRenderer.on('finish-download', (_, __, tab) => {
  if (tab === 'maindocx') {
    ElMessage.success('下载完成')
    downloadLoading.value = false
  }
})

// 解析按钮
const parseLoading = ref(false)
const onParseDocument = () => {
  if (parseLoading.value) return
  parseLoading.value = true
  handler
    .ParseDocument(store.current!._id.$oid)
    .then((res) => {
      if (res) {
        handler.Detail(store.current!._id.$oid).then((detail) => {
          store.addTag(detail)
        })
        ElMessage.success('解析成功')
      } else {
        ElMessage.error('解析失败')
      }
    })
    .finally(() => {
      parseLoading.value = false
    })
}
const deleteFile = (type: string, chunkIndex?: number) => {
  if (store.current?.status?.test_cases == 1) return
  ElMessageBox.confirm('是否删除该文件？', '提示', {
    confirmButtonText: '是',
    cancelButtonText: '否',
    type: 'warning'
  }).then(async () => {
    const res = await handler.DeleteFile(store.current!._id.$oid, type, chunkIndex)
    if (res) {
      ElMessage.success('删除成功')
      handler.Detail(store.current!._id.$oid).then((detail) => {
        store.addTag(detail)
      })
    }
  })
}
onUnmounted(() => {
  window.electron.ipcRenderer.removeAllListeners('finish-download')
})
</script>

<template>
  <div class="word-document-container">
    <div class="w-[240px] flex-shrink-0 text-[14px] text-[#333] py-[20px] flex flex-col">
      <div class="px-[20px]">
        <h2 class="text-[14px]! mb-[4px]">上传功能定义文档</h2>
        <p class="text-[#999] mb-[16px]">支持doc .docx .pdf ,支持多个文件上传</p>
        <el-upload ref="uploadRef" :auto-upload="false" :on-change="onBeforeUpload" :show-file-list="false"
          accept=".doc,.docx,.pdf">
          <template #trigger>
            <el-button>
              <el-icon class="mr-[5px]">
                <Upload />
              </el-icon>
              上传文件
            </el-button>
          </template>
        </el-upload>
        <div class="document-file">
          <h2 class="text-[14px]">
            功能定义文档({{
              store.current!._requirementFileList[0]?.object_name
                ? store.current!._requirementFileList.length
                : 0
            }})
          </h2>
          <div v-for="file in store.current!._requirementFileList"
            v-if="store.current!._requirementFileList[0]?.object_name" :key="file.name" class="document-file-item">
            <div class="flex items-center gap-[5px]">
              <img alt="" src="/svgs/doc.svg" />
              <el-tooltip :content="file.name" effect="light" placement="top">
                <p class="clamp-1 w-[130px]">{{ file.name }}</p>
              </el-tooltip>
            </div>
            <template v-if="!downloadLoading">
              <el-icon class="cursor-pointer" @click="deleteFile('main_docx')">
                <Delete />
              </el-icon>
              <el-icon class="cursor-pointer" @click="downloadFileLocal">
                <Download />
              </el-icon>
            </template>
            <el-icon v-else>
              <Loading class="animate-spin" />
            </el-icon>
          </div>
        </div>
        <el-button :disabled="parseLoading" :type="parseLoading ? 'info' : 'primary'" class="w-full mt-[24px]"
          @click="onParseDocument()">
          {{ parseLoading ? '解析中...' : '解析' }}
          <el-icon v-if="parseLoading">
            <Loading class="animate-spin" />
          </el-icon>
        </el-button>
        <div class="split-line"></div>
      </div>

      <h2 class="text-[14px] mb-[6px] px-[20px]">
        功能定义解析文档({{ store.current!.files.main_docx?.split_files.length || 0 }})
      </h2>
      <div class="w-full overflow-y-auto pl-[12px] box-border">
        <div v-for="file in store.current!.files.main_docx?.split_files || []" :key="file" :class="{
          'is-active': currentFile?.chunk_index === file.chunk_index,
          'is-disabled': store.current?.status?.test_cases == 1
        }" class="split-file-item">
          <div class="flex items-center gap-[5px] cursor-pointer" @click="onClickPreviewFile(file)">
            <img alt="" src="/svgs/doc.svg" />
            <el-tooltip :content="file.object_name.split('/').slice(1).join('/')" effect="light" placement="left-start">
              <p class="clamp-1 w-[140px] clamp-1">{{ file.object_name.split('/').slice(1).join('/') }}</p>
            </el-tooltip>


          </div>

          <el-icon class="cursor-pointer">
            <Delete @click="deleteFile('main_docx_chunk', file.chunk_index)"></Delete>
          </el-icon>
          <el-tooltip content="该文档包含表格 暂时不支持渲染">
            <el-icon class="cursor-pointer">
              <Warning v-if="file.is_table" />
            </el-icon>
          </el-tooltip>
        </div>
      </div>
    </div>
    <div class="w-full h-[99.9%] bg-[#fff] border-l border-l-style-solid b-[#ebebeb]">
      <template v-if="currentFile">
        <div
          class="no-drag border-b border-b-style-solid b-[#EBEBEB] h-[32px] flex items-center justify-between gap-[14px] px-[16px]">
          <p class="font-500 text-[14px] text-[#333]">{{ currentFile?.file_name }}</p>
          <div class="cursor-pointer">
            <el-button class="cursor-pointer" size="small" @click="onSaveContent">保存</el-button>
          </div>
        </div>
      </template>
      <div v-else v-loading="fileLoading" class="h-full flex items-center justify-center">
        <SmtEmpty v-if="store.current!._requirementFileList.length === 0" description="请先上传功能定义文档开始后在线查看、编辑" />
        <p v-else class="text-[12px] text-[#999]">请点击运行后在线查看、编辑</p>
      </div>
      <div v-show="currentFile" class="editor-container">
        <div ref="quillEditorRef" class="docx-editor" />
      </div>
    </div>
  </div>
</template>

<style lang="scss">
.word-document-container {
  height: calc(100% - 1px);
  display: flex;
  background: #fff;

  .document-file {
    margin-top: 20px;

    .document-file-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 14px;
      margin-top: 5px;
      height: 32px;
      padding: 0 0 0 12px;

      &:hover {
        background: rgba(153, 153, 153, 0.09);
      }
    }
  }

  .ql-toolbar.ql-snow {
    border: none;
  }

  .editor-container {
    height: calc(100% - 80px);
  }

  .docx-editor {
    border: none;
  }

  .split-line {
    height: 1px;
    background: #ebebeb;
    margin: 25px 0;
  }

  .split-file-item {
    height: 40px;
    padding: 0 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    cursor: pointer;

    &.is-disabled {
      .cursor-pointer {
        cursor: not-allowed;
        color: #ccc;
      }
    }

    &:hover,
    &.is-active {
      background: rgba(213, 104, 207, 0.1);

      &:before {
        content: '';
        position: absolute;
        right: 0;
        top: 0;
        height: 100%;
        width: 4px;
        background: rgba(213, 104, 207, 1);
      }
    }
  }
}
</style>
