<template>
  <div ref="container" class="univer-container"></div>
</template>

<script lang="ts" setup>
import '@univerjs/design/lib/index.css'
import '@univerjs/ui/lib/index.css'
import '@univerjs/sheets-ui/lib/index.css'
import '@univerjs/sheets-formula/lib/index.css'

import { Univer } from '@univerjs/core'
import { defaultTheme } from '@univerjs/design'
import { UniverDocsPlugin } from '@univerjs/docs'
import { UniverDocsUIPlugin } from '@univerjs/docs-ui'
import { UniverFormulaEnginePlugin } from '@univerjs/engine-formula'
import { UniverRenderEnginePlugin } from '@univerjs/engine-render'
import { UniverSheetsPlugin } from '@univerjs/sheets'
import { UniverSheetsFormulaPlugin } from '@univerjs/sheets-formula'
import { UniverSheetsUIPlugin } from '@univerjs/sheets-ui'
import { UniverUIPlugin } from '@univerjs/ui'
import { FUniver, FWorkbook } from '@univerjs/facade'
import { onBeforeUnmount, onMounted, ref, shallowRef } from 'vue'
import xlsx from 'xlsx'

const { data } = defineProps({
  // workbook data
  data: {
    type: Object,
    default: () => ({})
  }
})

const univerRef = shallowRef<Univer | null>(null)
const workbook = shallowRef<FWorkbook | null>(null)
const container = ref<HTMLElement | null>(null)
const univerAPI = shallowRef<FUniver | null>(null)

onMounted(() => {
  init(data)
})

onBeforeUnmount(() => {
  destroyUniver()
})

/**
 * Initialize univer instance and workbook instance
 * @param data {IWorkbookData} document see https://univer.work/api/core/interfaces/IWorkbookData.html
 */
const init = (data = {}) => {
  const univer = new Univer({
    theme: defaultTheme
  })

  univerRef.value = univer

  // core plugins
  univer.registerPlugin(UniverRenderEnginePlugin)
  univer.registerPlugin(UniverFormulaEnginePlugin)
  univer.registerPlugin(UniverUIPlugin, {
    container: container.value!,
    header: true,
    footer: true
  })

  // doc plugins
  univer.registerPlugin(UniverDocsPlugin, {
    hasScroll: false
  })
  univer.registerPlugin(UniverDocsUIPlugin)

  // sheet plugins
  univer.registerPlugin(UniverSheetsPlugin)
  univer.registerPlugin(UniverSheetsUIPlugin)
  univer.registerPlugin(UniverSheetsFormulaPlugin)

  univerAPI.value = FUniver.newAPI(univer)
  // create workbook instance
  workbook.value = univerAPI.value.createUniverSheet({})
}

function parseCSVToUniverData(csv: string[][]) {
  return csv.map((row) => {
    return row.map((cell) => {
      return {
        v: cell.replaceAll('\n', '') || ''
      }
    })
  })
}

function univerToCsv(univerData) {
  // 创建一个 CSV 字符串，用于存储所有行的数据
  let csv = ''

  // 遍历 univerData 中的每个对象
  univerData.forEach((row) => {
    // 遍历每个对象的每个属性
    Object.values(row).forEach((value) => {
      // 将每个值转换为字符串，并添加到 CSV 字符串中
      csv += `${value.v},`
    })
    // 添加换行符
    csv += '\n'
  })

  // 返回转换后的 CSV 字符串
  return csv
}

/**
 * Destroy univer instance and workbook instance
 */
const destroyUniver = () => {
  univerRef.value?.dispose()
  univerRef.value = null
  workbook.value = null
}

/**
 * Get workbook data
 */
// const getData = () => {
//   if (!workbook.value) {
//     throw new Error("Workbook is not initialized");
//   }
//   return workbook.value.save();
// };

/**
 * 设置 sheet 数据
 * @param data csv json 化之后的数据
 */
 const setSheetData = async (data: any[]) => {
  console.log(workbook.value);
  if (!workbook.value) {
    throw new Error('Workbook is not initialized');
  }

  const activeWorkbook = univerAPI.value!.getActiveWorkbook();

  // 获取 Sheet0
  const sheet0 = activeWorkbook?.getActiveSheet();
  if (!sheet0) {
    throw new Error('Sheet0 does not exist');
  }

  const colsCount = data.reduce((max, row) => Math.max(max, row.length), 0);
  const sheetValue = parseCSVToUniverData(data);

  // 更新 Sheet0
  sheet0.getRange(0, 0, data.length, colsCount).setWrap(true);
  sheet0.getRange(0, 0, data.length, colsCount).setWrapStrategy(3);
  sheet0.setColumnWidths(0, colsCount, 250);
  sheet0.getRange(0, 0, sheetValue.length, colsCount).setValues(sheetValue);
};

const converteSheet2File = () => {
  const workbook = univerAPI.value!.getActiveWorkbook()
  const snapshot = workbook!.getSnapshot()
  const activeWorkbook = univerAPI.value!.getActiveWorkbook()
  const sheets = activeWorkbook!.getSnapshot().sheets
  const newSheetName = 'Sheet' + Object.keys(sheets).length
  const sheetData = Object.values(snapshot.sheets).find((sheet) => {
    return sheet.name === newSheetName
  })

  const csv = univerToCsv(Object.values(sheetData?.cellData ?? {}))
  const jsonArr = csv.split('\n').map((row) => {
    return row.split(',').map((cell) => {
      // 这里你可以处理特殊字符，例如逗号或引号
      return cell.replace(/"/g, '').replace(/,/g, '')
    })
  })
  // 处理删除后 undefined 的情况
  jsonArr.forEach((row) => {
    row.forEach((cell, index) => {
      if (cell === 'undefined') {
        row[index] = ''
      }
    })
  })
  const workbook2 = xlsx.utils.book_new()
  const sheet2 = xlsx.utils.aoa_to_sheet(jsonArr)
  xlsx.utils.book_append_sheet(workbook2, sheet2, newSheetName)
  const bin = xlsx.write(workbook2, { type: 'binary', bookType: 'xlsx' })
  return bin
}

defineExpose({
  setSheetData,
  converteSheet2File
})
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.univer-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

/* Also hide the menubar */
:global(.univer-menubar) {
  display: none;
}
</style>
