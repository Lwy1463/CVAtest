<script lang="ts" setup>
import { computed, inject, onBeforeUnmount, reactive, Ref, ref, watchEffect } from 'vue'
import UniverSheet from '@renderer/components/UniverSheet/index.vue'
import { Delete, Download, Loading } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, ElProgress } from 'element-plus'
import DocumentScriptErrorProcessor from './DocumentScriptErrorProcessor.vue'
import { useTagsStore } from '@renderer/stores/useTagsStore'
import { useProductFetch } from '../useProductFetch'
import { useIntervalFn } from '@vueuse/core'
import WUUpload from '@renderer/components/WUpload.vue'
import UploadMappingExcel from '@renderer/components/UploadMappingExcel.vue'
import { read, utils as xlsxUtils } from 'xlsx'

const store = useTagsStore()
const currentTabIdx: Ref<number> | undefined = inject('currentTabIdx')
const datas = ref()
const univerRef = ref<InstanceType<typeof UniverSheet> | null>(null)
const previewType = ref('') // 记录点击哪个生成表
const testcaseWay = ref('1')
const canUseAiGenerate = computed(() => {
  return (store.current as any).status.test_requirements === 2 // 需求已处理完
})
const emits = defineEmits(['goto-req'])
const handleGotoReq = () => {
  emits('goto-req')
}

const exampleFile = reactive({
  testFile: {
    text: '*请上传测试用例文档'
  },
  dbcFile: {
    text: '*请上传DBC文档'
  }
})

// 是否所有必传文件都已经上传
const isFilesAllUpdated = computed(() => {
  const files: any = store.current?.files
  return files?.mappings_1 && files?.mappings_2 && files?.mappings_3 && files?.dbc_data
})

// 上传
const { handler, DownloadFileLocal } = useProductFetch()
const downloadLoading1 = ref(false)
const downloadFileLocal1 = () => {
  downloadLoading1.value = true
  DownloadFileLocal(
    store.current!._id.$oid,
    store.current!.files.mappings_1.object_name,
    store.current!.files.mappings_1.file_name,
    store.current!.download_path
  )
    .then(() => {
      ElMessage.success(`下载成功, 文件已保存到${store.current!.download_path}`)
    })
    .catch(() => {
      ElMessage.error('下载失败')
    })
    .finally(() => {
      downloadLoading1.value = false
    })
}
const downloadLoading2 = ref(false)
const downloadFileLocal2 = () => {
  downloadLoading2.value = true
  DownloadFileLocal(
    store.current!._id.$oid,
    store.current!.files.mappings_2.object_name,
    store.current!.files.mappings_2.file_name,
    store.current!.download_path
  )
    .then(() => {
      ElMessage.success(`下载成功, 文件已保存到${store.current!.download_path}`)
    })
    .catch(() => {
      ElMessage.error('下载失败')
    })
    .finally(() => {
      downloadLoading2.value = false
    })
}
const downloadLoading3 = ref(false)
const downloadFileLocal3 = () => {
  downloadLoading3.value = true
  DownloadFileLocal(
    store.current!._id.$oid,
    store.current!.files.mappings_3.object_name,
    store.current!.files.mappings_3.file_name,
    store.current!.download_path
  )
    .then(() => {
      ElMessage.success(`下载成功, 文件已保存到${store.current!.download_path}`)
    })
    .catch(() => {
      ElMessage.error('下载失败')
    })
    .finally(() => {
      downloadLoading3.value = false
    })
}
const downloadLoading_dbc = ref(false)
const downloadFileLocal_dbc = () => {
  if (store.current?.status?.test_cases == 1) return
  downloadLoading_dbc.value = true
  DownloadFileLocal(
    store.current!._id.$oid,
    store.current!.files.dbc_data.object_name,
    store.current!.files.dbc_data.file_name,
    store.current!.download_path
  )
    .then(() => {
      ElMessage.success(`下载成功, 文件已保存到${store.current!.download_path}`)
    })
    .catch(() => {
      ElMessage.error('下载失败')
    })
    .finally(() => {
      downloadLoading_dbc.value = false
    })
}

// 更新上传的文件数据后
const handleUpload = (index: number) => {
  handler.Detail((store.current as any)._id.$oid).then((detail) => {
    store.addTag(detail)
  })
}

/**
 * 预览并编辑映射表 (脚本正常生成后才能预览)
 */
const handlePreviewMappings = () => {
  if (previewType.value === 'mappings') {
    return
  }
  if (
    (store.current as any).files?.generated_mappings &&
    (store.current as any).status?.test_scripts === 2
  ) {
    previewType.value = 'mappings'
    handler
      .DownloadFile(
        (store.current as any)._id.$oid,
        (store.current as any).files?.generated_mappings?.object_name
      )
      .then((stream: any) => {
        const blob = new Blob([stream], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        // 使用 FileReader 读取 Blob 对象
        const fileReader = new FileReader()
        fileReader.readAsArrayBuffer(blob)
        fileReader.onload = (event: any) => {
          const arrayBuffer = event.target.result
          const data = new Uint8Array(arrayBuffer)
          const workbook = read(data, { type: 'array' })

          // 假设你想要读取第一个工作表
          const sheetName = workbook.SheetNames[0]
          const sheet = workbook.Sheets[sheetName]

          // 使用 xlsx-to-csv 将工作表转换为 CSV 格式
          const csv = xlsxUtils.sheet_to_csv(sheet)

          // const rows = csv.split(/\r\n|\n/);
          // const csvArr = rows.map((line) => line.split(","));
          const jsonArr = csv.split('\n').map((row) => {
            return row.split(',').map((cell) => {
              // 这里你可以处理特殊字符，例如逗号或引号
              return cell.replace(/"/g, '').replace(/,/g, '')
            })
          })
          univerRef.value?.setSheetData(jsonArr)
        }
      })
  }
}

// 生成脚本按钮
const generateScriptLoading = ref(false)
const handleGenerateScript = () => {
  generateScriptLoading.value = true
  handler
    .GenerateScript((store.current as any)._id.$oid)
    .then((res) => {
      if (res) {
        handler.Detail((store.current as any)._id.$oid).then((detail) => {
          store.addTag(detail)
        })
        resume() // 更新进度信息
      }
    })
    .finally(() => {
      generateScriptLoading.value = false
    })
}

// NOTE: 状态是 1 则轮训去获取 info 获取最新处理进度
const loopUpdateDetailInfo = () => {
  if (currentTabIdx.value !== 2) return
  if ((store.current as any).status.test_scripts === 1) {
    // 如果是处理中状态，持续更新最新项目 info
    handler.Detail((store.current as any)._id.$oid).then((detail) => {
      store.addTag(detail)
    })
  } else {
    pause()
  }
}
const { resume, pause } = useIntervalFn(loopUpdateDetailInfo, 1000)
pause()
onBeforeUnmount(() => pause())

const currentGenerateProgress = computed(() => {
  const progress =
    ((store.current as any)?.testscripts_progress?.completed ?? 0) /
    ((store.current as any).testscripts_progress?.total ?? 0)
  return +((isNaN(progress) ? 0 : progress) * 100).toFixed(2)
})

// 初始进入页面如果处理中，加载进度条
watchEffect(() => {
  if ((store.current as any).status.test_scripts === 1) {
    resume()
  } else if ((store.current as any).status.test_scripts !== 2) {
    previewType.value = ''
  }
})
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
const onStopTask = (id: string, jobId: string) => {
  ElMessageBox.confirm('确定要终止任务吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    handler
      .StopTask(id, jobId)
      .then((res) => {
        console.log(res)
        if (res.status == 5) {
          ElMessage.success('终止成功')
          handler.Detail((store.current as any)._id.$oid).then((detail) => {
            store.addTag(detail)
          })
        } else {
          ElMessage.error('终止失败')
        }
      })
      .catch(() => {
        ElMessage.error('终止失败')
      })
  })
}
</script>

<template>
  <div class="script-document-container">
    <div class="w-[240px] flex-shrink-0 text-[14px] text-[#333] p-[20px] relative">
      <div class="overflow-y-auto h-[calc(100%-45px)] hide-scrollbar">
        <!-- <el-radio-group v-model="testcaseWay">
          <el-popover ref="popoverRef" placement="top" :teleported="false" width="auto" :disabled="canUseAiGenerate"
            :show-after="200" trigger="hover">
            <template #reference>
              <el-radio label="1" :disabled="!canUseAiGenerate">AI智能生成测试用(基于测试需求)</el-radio>

            </template>
<div class="flex-between">
  <div>需求配置已处理的情况下可选</div>
  <span class="ml-[5px] text-[#9A4596] cursor-pointer" @click="handleGotoReq">去配置</span>
</div>
</el-popover>

<el-radio label="2">基于测试用例文档</el-radio>
</el-radio-group> -->
        <div class="text-[#333333] mb-[10px] font-500">AI智能生成测试用(基于测试用例)</div>
        <UploadMappingExcel :proj-info="store.current" is-require @on-upload="handleUpload">
          <!-- mapping_1 -->
          <template #download1>
            <div v-if="!downloadLoading1" class="flex items-center gap-[4px]">
              <el-icon class="cursor-pointer" @click="downloadFileLocal1">
                <Download />
              </el-icon>
              <el-icon class="cursor-pointer" @click="deleteFile('mappings_1')">
                <Delete />
              </el-icon>
            </div>
            <el-icon v-else class="cursor-pointer">
              <Loading class="animate-spin" />
            </el-icon>
          </template>
          <!-- mapping_2 -->
          <template #download2>
            <div v-if="!downloadLoading2" class="flex items-center gap-[4px]">
              <el-icon class="cursor-pointer" @click="downloadFileLocal2">
                <Download />
              </el-icon>
              <el-icon class="cursor-pointer" @click="deleteFile('mappings_2')">
                <Delete />
              </el-icon>
            </div>
            <el-icon v-else class="cursor-pointer">
              <Loading class="animate-spin" />
            </el-icon>
          </template>
          <!-- mapping_3 -->
          <template #download3>
            <div v-if="!downloadLoading3" class="flex items-center gap-[4px]">
              <el-icon class="cursor-pointer" @click="downloadFileLocal3">
                <Download />
              </el-icon>
              <el-icon class="cursor-pointer" @click="deleteFile('mappings_3')">
                <Delete />
              </el-icon>
            </div>
            <el-icon v-else class="cursor-pointer">
              <Loading class="animate-spin" />
            </el-icon>
          </template>
        </UploadMappingExcel>
        <div class="upload-area mt-[10px]">
          <span><span class="text-[#f00]">*</span>请上传DBC文档</span>
          <WUUpload
            :acceptType="'.dbc'"
            :category="'dbc_data'"
            :proj-info="store.current"
            class="mt-[10px] mb-[20px]"
            @on-upload="handleUpload"
          ></WUUpload>
          <div v-if="store.current.files?.dbc_data" class="flex-between">
            <div class="flex items-center gap-[5px]">
              <p class="clamp-1 w-[170px]">
                {{ store.current.files?.dbc_data?.file_name ?? '' }}
              </p>
            </div>
            <div
              v-if="!downloadLoading_dbc"
              :class="{ 'is-disabled': store.current?.status?.test_cases == 1 }"
              class="flex items-center gap-[4px]"
            >
              <el-icon class="cursor-pointer" @click="deleteFile('main_docx_chunk')">
                <Delete></Delete>
              </el-icon>
              <el-icon class="cursor-pointer" @click="downloadFileLocal_dbc">
                <Download />
              </el-icon>
            </div>
            <el-icon v-else class="cursor-pointer">
              <Loading class="animate-spin" />
            </el-icon>
          </div>
        </div>
        <el-button
          :disabled="
            generateScriptLoading ||
            store.current?.status?.test_cases == 1 ||
            store.current?.status?.test_scripts == 1 ||
            !isFilesAllUpdated
          "
          class="w-full mt-[24px] h-[32px]"
          type="primary"
          @click="handleGenerateScript"
          >生成脚本</el-button
        >
      </div>
      <!-- 生成的表文件 -->
      <div class="position-absolute bottom-0 left-0 w-full bg-[#fff]">
        <!-- <div class="flex-start border-t border-t-style-solid b-[#EBEBEB] py-[10px] px-[20px] cursor-pointer">
          <img class="w-[20px] h-[20px]" src="/svgs/ys.svg" alt="">
          <span class="ml-[5px] text-[#333333]">映射总表</span>

          <el-tag class="ml-[6px]" type="info">未生成</el-tag>
        </div> -->
        <div
          :class="{ 'is-active': previewType === 'mappings' }"
          class="preview-item flex-start border-t border-t-style-solid b-[#EBEBEB] py-[10px] px-[20px] cursor-pointer"
          @click="handlePreviewMappings"
        >
          <img alt="" class="w-[20px] h-[20px]" src="/svgs/ys.svg" />
          <span class="ml-[5px] text-[#333333]">映射总表</span>
          <el-tag
            :type="store.current.files?.generated_mappings ? 'success' : 'info'"
            class="ml-[6px]"
            >{{ store.current.files?.generated_mappings ? '已生成' : '未生成' }}</el-tag
          >
        </div>
      </div>
    </div>
    <div class="w-full h-full bg-[#fff] border-l border-l-style-solid b-[#ebebeb] relative">
      <div
        v-if="store.current.status.test_scripts == 0"
        class="w-full h-full bg-[#fff] absolute z-99 left-0 top-0 text-[#333333] flex-center"
      >
        请点击生成后在线查看、编辑
      </div>
      <div
        v-if="store.current.status.test_scripts == 4"
        class="w-full h-full bg-[#fff] absolute z-99 left-0 top-0 text-[#333333] flex-center"
      >
        脚本生成错误，请重新生成
      </div>
      <div
        v-if="store.current?.status.test_scripts == 1"
        class="w-full h-full bg-[#fff] absolute z-99 left-0 top-0 text-[#333333] flex-center flex-col"
      >
        <div class="flex items-center gap-[10px] mb-[10px]">
          <el-progress
            :duration="10"
            :percentage="currentGenerateProgress"
            class="w-[500px]"
            color="#D568CF"
            striped
            striped-flow
          />
          <el-button
            size="small"
            type="danger"
            @click="onStopTask(store.current!._id.$oid, store.current?.status.test_scripts_job_id)"
          >
            终止</el-button
          >
        </div>
        <span class="progress-text"
          >正在智能生成，预计剩余时长{{
            store.current?.testscripts_seconds_remaining < 60
              ? (store.current?.testcases_seconds_remaining || 0).toFixed(2)
              : ((store.current?.testscripts_seconds_remaining ?? 0) / 60).toFixed(2)
          }}分钟...
        </span>
      </div>
      <DocumentScriptErrorProcessor v-if="store.current.status?.test_scripts == 3" />
      <div
        v-if="store.current.status?.test_scripts == 2 && (previewType || currentTabIdx)"
        class="h-full w-full"
      >
        <div
          class="sheet-header h-[40px] flex-between b-b border-b-style-solid b-[#EBEBEB] px-[20px]"
        >
          <span></span>
          <!-- <div>
            <el-button
              :disabled="updaloadLoading_testcase"
              size="small"
              @click="handleReUploadExcel"
              >保存</el-button
            >
            <el-button
              :disabled="downloadLoading_testcaseg"
              size="small"
              @click="handleDownloadExcel"
              >下载</el-button
            >
          </div> -->
        </div>
        <UniverSheet ref="univerRef" :data="datas" class="!h-[calc(100%-40px)]" />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.script-document-container {
  height: calc(100% - 1px);
  display: flex;
  background: #fff;
  .upload-file {
    background: rgba(153, 153, 153, 0.09);
    border: 1px #ececec solid;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 20px;
  }

  .upload-area {
    border-radius: 2px;
    border: 1px solid #ececec;
    background-color: #f6f6f6;
    padding: 7px 10px;
  }
  .preview-item {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    padding: 10px 20px;
    border-top: 1px solid #ebebeb;
    cursor: pointer;
    position: relative;
    //&:hover,
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
  .el-icon.is-disabled {
    color: #fff !important;
  }
}
</style>
