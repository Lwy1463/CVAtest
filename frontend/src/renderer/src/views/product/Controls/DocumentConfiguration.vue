<script lang="ts" setup>
import {
  computed,
  inject,
  onBeforeUnmount,
  onUnmounted,
  reactive,
  Ref,
  ref,
  watchEffect
} from 'vue'
import UniverSheet from '@renderer/components/UniverSheet/index.vue'
import { ElMessage, ElMessageBox, ElProgress, ElTag } from 'element-plus'
import { Delete, Download, Loading } from '@element-plus/icons-vue'
import { useTagsStore } from '@renderer/stores/useTagsStore'
import { useProductFetch } from '../useProductFetch'
import { useIntervalFn } from '@vueuse/core'
import WUUpload from '@renderer/components/WUpload.vue'
import UploadMappingExcel from '@renderer/components/UploadMappingExcel.vue'
import { read, utils as xlsxUtils } from 'xlsx'
import { v4 as uuidv4 } from 'uuid'

const store = useTagsStore()
const { handler, DownloadFileLocal } = useProductFetch()
const acceptType = '.xls,.xlsx,.csv'
const datas = ref()
const testcaseWay = ref('1') // radio
const previewType = ref('') // 记录点击哪个生成表

const currentTabIdx: Ref<number> | undefined = inject('currentTabIdx')
const univerRef = ref<InstanceType<typeof UniverSheet> | null>(null)

// watchEffect(() => {
//   if (currentTabIdx?.value == 1) return
//   if (store.current.status.test_requirements !== 2) {
//     testcaseWay.value = '2'
//   } else {
//     testcaseWay.value = '1'
//   }
// })

const exampleFile = reactive({
  testFile: {
    text: '*请上传测试用例文档'
  },
  mapFile: {
    text: '请上传映射关联文档'
  },
  dbcFile: {
    text: '请上传DBC文档'
  }
})
const testcaseStatusMap = {
  0: {
    text: '未生成',
    type: 'info'
  },
  1: {
    text: '生成中',
    type: 'primary'
  },
  2: {
    text: '已完成',
    type: 'success'
  },
  4: {
    text: '生成失败',
    type: 'danger'
  },
  5: {
    text: '已完成',
    type: 'success'
  }
}

const downloadLoading = ref(false)
const downloadFileLocal = () => {
  downloadLoading.value = true
  DownloadFileLocal(
    store.current!._id.$oid,
    store.current!.files.testcase.object_name,
    store.current!.files.testcase.file_name,
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

const canUseAiGenerate = computed(() => {
  return (store.current as any).status.test_requirements === 2 // 需求已处理完
})

const currentGenerateProgress = computed(() => {
  // const progress =
  //   (Object.keys((store.current as any).files?.split_testcases ?? {})?.length ?? 0) /
  //   ((store.current as any).files?.main_docx?.split_files?.length ?? 0)

  const progress = store.current?.testcases_completion

  return +((isNaN(progress) ? 0 : progress) * 100).toFixed(2)
})

// NOTE: 状态是 1 则轮训去获取 info 获取最新处理进度
const loopUpdateDetailInfo = () => {
  if (currentTabIdx.value !== 1) {
    return
  }
  if ((store.current as any).status.test_cases === 1) {
    // 如果是处理中状态，持续更新最新项目 info
    handler.Detail((store.current as any)._id.$oid).then((detail) => {
      store.addTag(detail)
    })
  } else {
    // 如果是已完成状态，不再轮训
    handlePreviewSheet()
    pause()
  }
}
const { resume, pause } = useIntervalFn(loopUpdateDetailInfo, 1000)
watchEffect(() => {
  if ((store.current as any).status.test_cases === 1) {
    resume()
  }
})
onBeforeUnmount(() => pause())

// 下载上传的文件结束提示
const uuid = uuidv4()
window.electron.ipcRenderer.on('finish-download', (_, path, tab, id) => {
  if (uuid !== id) return
  if (tab === 'testcase') {
    downloadLoading.value = false
  } else if (tab === 'mapping_1') {
    downloadLoading1.value = false
  } else if (tab === 'mapping_2') {
    downloadLoading2.value = false
  } else if (tab === 'mapping_3') {
    downloadLoading3.value = false
  } else if (tab === 'dbc_data') {
    downloadLoading_dbc.value = false
  } else if (tab === 'testcase_generate') {
    downloadLoading_testcaseg.value = false
  }
  ElMessage.success(`下载完成, 文件已保存到:${store.current?.download_path}`)
})

// 上传文件后的处理
const handleUpload = () => {
  handler.Detail((store.current as any)._id.$oid).then((detail) => {
    store.addTag(detail)
  })
}

const emits = defineEmits(['goto-req'])
const handleGotoReq = () => {
  emits('goto-req')
}

// 生成用例按钮
const generateTestcaseLoading = ref(false)
const handleGenerateTestcase = () => {
  generateTestcaseLoading.value = true
  handler
    .GenerateTestcase((store.current as any)._id.$oid, +testcaseWay.value)
    .then((res) => {
      if (res) {
        handler.Detail((store.current as any)._id.$oid).then((detail) => {
          store.addTag(detail)
        })
        resume() // 更新进度信息
      }
    })
    .catch((err) => {
      console.log('handleGenerateTestcase:', err)
    })
    .finally(() => {
      generateTestcaseLoading.value = false
    })
}

/**
 * 预览并编辑用例表
 */
const handlePreviewSheet = () => {
  if ((store.current as any).status.test_cases == 2) {
    previewType.value = 'testcase'
    handler
      .DownloadFile(
        (store.current as any)._id.$oid,
        (store.current as any).files?.testcase?.object_name
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
          const csv = xlsxUtils.sheet_to_csv(sheet, {
            FS: '\\', // Field Separator
            RS: '|||', // Record Separator, replace newlines with '|||'
          })

          const jsonArr = csv.split('|||').map((row) => {
            return row.split('\\').map((cell) => {
              // 将特殊字符替换回换行符，并处理特殊字符，例如逗号或引号
              return cell.replace(/"/g, '').replace(/@@@/g, '\n')
            })
          })
          console.log(jsonArr)
          univerRef.value?.setSheetData(jsonArr)
        }
      })
  }
}
/**
 * 预览并编辑映射表
 */
const handlePreviewMappings = () => {
  if ((store.current as any).files?.generated_mappings) {
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

const updaloadLoading_testcase = ref(false)
const downloadLoading_testcaseg = ref(false)

// 上传编辑后的用例表
const handleReUploadExcel = async () => {
  updaloadLoading_testcase.value = true
  const bin = univerRef.value?.converteSheet2File()
  // 文件名
  let fileName = 'unknow.xlsx'
  let objectName = ''
  if (previewType.value === 'testcase') {
    fileName = (store.current as any).files?.testcase?.file_name ?? 'testcase.xlsx'
    objectName = (store.current as any).files?.testcase?.object_name ?? ''
  } else {
    fileName =
      (store.current as any).files?.generated_mappings?.file_name ?? 'generated_mappings.xlsx'
    objectName = (store.current as any).files?.generated_mappings?.object_name ?? ''
  }
  // 将输出转换为Blob
  const blob = new Blob([s2ab(bin)], { type: 'application/octet-stream' })
  const formData = new FormData()
  const info = new Blob([
    JSON.stringify({ db_id: (store.current as any)['_id']['$oid'], object_name: objectName })
  ])
  // 使用Blob和文件名创建一个File对象
  const file = new File([blob], fileName, {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  })
  formData.append('updated_file', file)
  formData.append('info', info)
  try {
    const res: any = await handler.ReplaceFile(formData)
    if (res) {
      handler.Detail((store.current as any)._id.$oid).then((detail) => {
        store.addTag(detail)
      })
      ElMessage.success('上传成功')
    } else {
      ElMessage.error('上传失败')
    }
  } catch (error) {
    ElMessage.error('上传失败')
  } finally {
    updaloadLoading_testcase.value = false
  }
}

// 下载用例表到本地

const handleDownloadExcel = () => {
  downloadLoading_testcaseg.value = true
  let fileName = 'unknow.xlsx'
  if (previewType.value === 'testcase') {
    fileName = (store.current as any).files?.testcase?.file_name ?? 'testcase.xlsx'
  } else {
    fileName =
      (store.current as any).files?.generated_mappings?.file_name ?? 'generated_mappings.xlsx'
  }
  const bin = univerRef.value?.converteSheet2File()
  // 将输出转换为Blob
  const blob = new Blob([s2ab(bin)], { type: 'application/octet-stream' })
  blobToBase64(blob as any as Blob).then((base64String) => {
    window.electron.ipcRenderer.send(
      'start-download',
      base64String,
      store.current!.download_path,
      fileName,
      'testcase_generate',
      uuid
    )
  })
}

onUnmounted(() => {
  window.electron.ipcRenderer.removeAllListeners('finish-download')
})

function blobToBase64(blob: Blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => {
      const base64String = reader.result
      resolve(base64String)
    }
    reader.onerror = reject
    reader.readAsDataURL(blob)
  })
}

// 转换为Blob
function s2ab(s) {
  const buf = new ArrayBuffer(s.length)
  const view = new Uint8Array(buf)
  for (let i = 0; i !== s.length; ++i) view[i] = s.charCodeAt(i) & 0xff
  return buf
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
</script>

<template>
  <div class="excel-document-container">
    <div class="w-[240px] flex-shrink-0 text-[14px] text-[#333] p-[20px] relative">
      <div class="overflow-y-auto h-[calc(100%-90px)] hide-scrollbar">
        <!-- <el-radio-group v-model="testcaseWay">
          <el-popover
            ref="popoverRef"
            :disabled="canUseAiGenerate"
            :show-after="200"
            :teleported="false"
            placement="top"
            trigger="hover"
            width="auto"
          >
            <template #reference>
              <el-button style="margin-right: 16px">Click to activate</el-button>
              <el-radio :disabled="!canUseAiGenerate" value="1"
                >AI智能生成测试用例(基于测试需求)</el-radio
              >
            </template>
<div class="flex-between">
  <div>需求配置已处理的情况下可选</div>
  <span class="ml-[5px] text-[#9A4596] cursor-pointer" @click="handleGotoReq">去配置</span>
</div>
</el-popover>

<el-radio value="2">基于测试用例文档</el-radio>
</el-radio-group> -->
        <div class="position-relative">
          <div v-if="store.current.status.test_requirements !== 2 || testcaseWay == '2'" class="upload-area mb-[10px]">
            <div class="flex-between">
              <div>
                <!-- <span class="text-[#D90000]">*</span> -->
                请上传测试用例文档
              </div>
              <!-- TODO -->
              <!-- <a href="#" class="text-[#C833C1]" @click="downloadTemp($event)">下载模版</a> -->
            </div>
            <WUUpload :acceptType="acceptType" :category="'testcase'" :proj-info="store.current"
              class="mt-[10px] mb-[20px]" @on-upload="handleUpload"></WUUpload>
            <div v-if="store.current.files?.testcase" class="flex-between">
              <div class="flex items-center gap-[5px]">
                <img alt="" src="/svgs/excel.svg" />
                <p class="line-clamp-1 w-[150px]">
                  {{ store.current.files?.testcase?.file_name ?? '' }}
                </p>
              </div>
              <template v-if="!downloadLoading">
                <el-icon class="cursor-pointer">
                  <Delete />
                </el-icon>
                <el-icon class="cursor-pointer" @click="downloadFileLocal">
                  <Download />
                </el-icon>
              </template>
              <el-icon v-else class="cursor-pointer">
                <Loading class="animate-spin" />
              </el-icon>
            </div>
          </div>
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
            <!-- <span class="text-[#f00]">*</span> -->
            <span>请上传DBC文档</span>
            <WUUpload :acceptType="'.dbc'" :category="'dbc_data'" :proj-info="store.current" class="mt-[10px] mb-[20px]"
              @on-upload="handleUpload"></WUUpload>
            <div v-if="store.current.files?.dbc_data" class="flex-between">
              <div class="flex items-center gap-[5px]">
                <p class="clamp-1 w-[170px]">
                  {{ store.current.files?.dbc_data?.file_name ?? '' }}
                </p>
              </div>
              <div v-if="!downloadLoading_dbc" :class="{ 'is-disabled': store.current?.status?.test_cases == 1 }"
                class="flex items-center gap-[4px]">
                <el-icon class="cursor-pointer" @click="deleteFile('dbc_data')">
                  <Delete></Delete>
                </el-icon>
                <el-icon class="cursor-pointer" @click="downloadFileLocal_dbc">
                  <Download />
                </el-icon>
              </div>
              <el-icon v-else class="cursor-pointer">
                <Download />
                <Loading class="animate-spin" />
              </el-icon>
            </div>
          </div>
          <!-- <el-button
            :disabled="
              generateTestcaseLoading ||
              store.current.status?.test_cases == 1 ||
              (store.current.status?.test_requirements != 2 && !store.current?.files?.testcase) ||
              !store.current?.files?.dbc_data
            "
            class="w-full mt-[24px] h-[32px]"
            type="primary"
            @click="handleGenerateTestcase"
            >生成用例</el-button
          > -->
          <el-button
            :disabled="generateTestcaseLoading || store.current.status.test_cases === 1 || store.current.status.test_requirements != 2"
            class="w-full mt-[24px] h-[32px]" type="primary" @click="handleGenerateTestcase">生成用例</el-button>
          <div v-if="!canUseAiGenerate && testcaseWay != '2'"
            class="mask w-full h-full bg-[#fff]/50 pos-absolute top-0 left-0">
          </div>
        </div>
      </div>
      <!-- 生成的表文件 -->
      <div class="position-absolute bottom-0 left-0 w-full bg-[#fff]">
        <div :class="{ 'is-active': previewType === 'testcase' }" class="preview-item" @click="handlePreviewSheet">
          <img alt="" class="w-[20px] h-[20px]" src="/svgs/yl.svg" />
          <span class="ml-[5px] text-[#333333]">用例表</span>
          <el-tag :type="testcaseStatusMap[store.current.status?.test_cases ?? '0']?.type ?? 'info'" class="ml-[6px]">{{
            testcaseStatusMap[store.current.status?.test_cases ?? '0']?.text ?? '未知状态'
          }}</el-tag>
        </div>
      </div>
    </div>
    <div class="w-full h-full bg-[#fff] border-l border-l-style-solid b-[#ebebeb] relative">
      <div v-if="store.current.status.test_cases == 0 && !previewType"
        class="w-full h-full bg-[#fff] absolute z-99 left-0 top-0 text-[#333333] flex-center">
        请点击生成后在线查看、编辑
      </div>
      <div v-if="store.current.status.test_cases == 4 && !previewType"
        class="w-full h-full bg-[#fff] absolute z-99 left-0 top-0 text-[#333333] flex-center">
        {{ store.current.status?.test_cases_error ?? '未知错误' }}
      </div>
      <div v-if="store.current!.status.test_cases == 1"
        class="w-full h-full bg-[#fff] absolute z-99 left-0 top-0 text-[#333333] flex-center flex-col">
        <div class="flex items-center gap-[10px] mb-[10px]">
          <el-progress :duration="10" :percentage="currentGenerateProgress" class="w-[500px]" color="#D568CF" striped
            striped-flow />
          <el-button size="small" type="danger"
            @click="onStopTask(store.current!._id.$oid, store.current?.status.test_cases_job_id)">终止</el-button>
        </div>

        <span class="progress-text">
          正在智能生成，
          预计剩余时长
          {{
            store.current?.testcases_seconds_remaining === -1
              ? '未知'
              : store.current?.testcases_seconds_remaining < 60 ? (store.current?.testcases_seconds_remaining ||
                0).toFixed(2) : ((store.current?.testcases_seconds_remaining ?? 0) / 60).toFixed(2) }}分钟... </span>
      </div>

      <div v-if="currentTabIdx || previewType" class="h-full w-full">
        <div class="sheet-header h-[40px] flex-between b-b border-b-style-solid b-[#EBEBEB] px-[20px]">
          <span></span>
          <div>
            <el-button :disabled="updaloadLoading_testcase" size="small" @click="handleReUploadExcel">保存</el-button>
            <el-button :disabled="downloadLoading_testcaseg" size="small" @click="handleDownloadExcel">下载</el-button>
          </div>
        </div>
        <UniverSheet ref="univerRef" :data="datas" class="!h-[calc(100%-40px)]" />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.excel-document-container {
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
    background-color: #fff;
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

  .is-disabled {
    color: #ccc;
  }
}
</style>
