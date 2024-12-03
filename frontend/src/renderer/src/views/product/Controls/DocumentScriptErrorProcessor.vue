<script lang="ts" setup>
import { ElMessage } from 'element-plus'
import { Delete, Plus } from '@element-plus/icons-vue'
import { computed, inject, ref, Ref, watchEffect } from 'vue'
import { useProductFetch } from '../useProductFetch'
import { useTagsStore } from '@renderer/stores/useTagsStore'
import { v4 as uuidv4 } from 'uuid'

//@ts-ignore
const arraySpanMethod = ({ row, column, rowIndex, columnIndex }) => {
  if (columnIndex === 0) {
    if (row.rowspan > 0) {
      return [row.rowspan, row.colspan]
    } else {
      return [0, 0]
    }
  }
}
const currentTabIdx: Ref<number> | undefined = inject('currentTabIdx')
const tableData = ref<any[]>([])
const { handler } = useProductFetch()
const store = useTagsStore()
watchEffect(() => {
  if (currentTabIdx.value != 2) return
  if ((store.current as any).status.test_scripts === 3) {
    handler.getGenerationErrors((store.current as any)._id.$oid).then((res) => {
      tableData.value = Object.keys(res)
        .map((key, index) => ({
          id: index,
          name: key,
          _name: key.length > 10 ? key.slice(0, 10) + '...' : key,
          value: res[key].join('、'),
          key: uuidv4(),
          logical_action: '',
          status: '',
          mapping: ''
        }))
        .sort((a, b) => a.id - b.id)
    })
  }
})

const handlerTableData = computed(() => {
  const marge = new Map()
  tableData.value.forEach((item) => {
    const key = item.id
    if (marge.has(key)) {
      marge.set(key, {
        rowspan: marge.get(key).rowspan + 1,
        colspan: 1,
        count: marge.get(key).count + 1
      })
    } else {
      marge.set(key, {
        rowspan: 1,
        colspan: 1,
        count: 1
      })
    }
  })
  return tableData.value.map((item) => {
    const { rowspan, colspan, count, isDelete } = marge.get(item.id)
    marge.set(item.id, {
      rowspan: 0,
      colspan: 0,
      count,
      isDelete: true
    })
    return {
      ...item,
      rowspan,
      colspan,
      count,
      isDelete
    }
  })
})

const onAdd = (row) => {
  tableData.value.push({
    id: row.id,
    key: uuidv4(),
    name: row.name,
    logical_action: '',
    status: '',
    mapping: ''
  })
  tableData.value = tableData.value.sort((a, b) => a.id - b.id)
}

const onDelete = (row: any) => {
  const index = tableData.value.findIndex((item) => item.key === row.key)
  if (index > -1 && row.count > 1) {
    tableData.value.splice(index, 1)
  } else {
    ElMessage.error('至少保留一行')
  }
}

const onSave = () => {
  const formMap = new Map()
  tableData.value.forEach((it) => {
    if (!formMap.has(it.id))
      formMap.set(it.id, {
        name: it.name,
        result: {
          ['功能']: {
            ['逻辑动作']: [],
            ['状态']: [],
            ['板卡映射']: []
          },
          ['总线']: {
            ['异常变量']: [],
            ['DBC信号映射']: []
          },
          ['代码']: {
            ['字符串']: []
          }
        }
      })
    if (it.type == 1) {
      formMap.get(it.id).result['功能']['逻辑动作'].push(it.logical_action)
      formMap.get(it.id).result['功能']['状态'].push(it.status)
      formMap.get(it.id).result['功能']['板卡映射'].push(it.mapping)
    } else if (it.type == 2) {
      formMap.get(it.id).result['总线']['异常变量'].push(it.exception)
      formMap.get(it.id).result['总线']['DBC信号映射'].push(it.dbc_mapping)
    } else if (it.type == 3) {
      formMap.get(it.id).result['代码']['字符串'].push(it.code)
    }
  })
  const formData = Array.from(formMap.keys()).map((key) => {
    return {
      functionality: {
        name: formMap.get(key).name,
        ...formMap.get(key).result
      }
    }
  })
  handler.updateGenerationErrors((store.current as any)._id.$oid, formData).then(() => {
    ElMessage.success('保存成功')
  })
}
</script>

<template>
  <div class="script-processor-container">
    <p class="font-500 text-[14px] text-[#333]">脚本配置文件</p>
    <div class="cursor-pointer">
      <el-button class="cursor-pointer" size="small" @click="onSave">保存</el-button>
    </div>
  </div>
  <div class="script-processor">
    <el-table
      :data="handlerTableData"
      :span-method="arraySpanMethod"
      border
      style="width: 100%; height: 100%"
    >
      <el-table-column fixed label="功能" prop="name" width="180">
        <template #default="{ row }">
          <el-tooltip :content="row.value" effect="dark" placement="top-start">
            <span>{{ row._name }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column align="center" label="操作" prop="amount3" width="80">
        <template #default="{ row }">
          <div class="flex items-center justify-between w-[40px] mx-[auto]">
            <el-icon class="mr-[4px] cursor-pointer" @click="onAdd(row)"><Plus></Plus></el-icon>
            <el-icon v-if="row.isDelete" class="mr-[4px] cursor-pointer" @click="onDelete(row)"
              ><Delete></Delete
            ></el-icon>
          </div>
          <!--          <el-button size="small" text @click="onDelete(row)">-->
          <!--                     -->
          <!--            删除-->
          <!--          </el-button>-->
          <!--          <el-button class="m-0!" size="small" text @click="onAdd(row)">-->
          <!--                    -->
          <!--            添加-->
          <!--          </el-button>-->
        </template>
      </el-table-column>
      <el-table-column label="类型" prop="amount1" width="140">
        <template #default="{ row, $index }">
          <el-select v-model="tableData[$index]['type']" placeholder="自定义类型">
            <el-option label="功能" value="1" />
            <el-option label="总线" value="2" />
            <el-option label="代码" value="3" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="逻辑动作" prop="amount1" width="180">
        <template #default="{ row, $index }">
          <el-input
            v-model="tableData[$index]['logical_action']"
            :disabled="row['type'] != 1"
            placeholder="自定义填写内容"
          ></el-input>
        </template>
      </el-table-column>
      <el-table-column label="状态" prop="amount2" width="180">
        <template #default="{ row, $index }">
          <el-input
            v-model="tableData[$index]['status']"
            :disabled="row['type'] != 1"
            placeholder="自定义填写内容"
          ></el-input>
        </template>
      </el-table-column>
      <el-table-column label="板卡映射" prop="amount3" width="180">
        <template #default="{ row, $index }">
          <el-input
            v-model="tableData[$index]['mapping']"
            :disabled="row['type'] != 1"
            placeholder="自定义填写内容"
          ></el-input>
        </template>
      </el-table-column>
      <el-table-column label="异常变量" prop="amount4" width="180">
        <template #default="{ row, $index }">
          <el-input
            v-model="tableData[$index]['exception']"
            :disabled="row['type'] != 2"
            placeholder="自定义填写内容"
          ></el-input>
        </template>
      </el-table-column>
      <el-table-column label="DBC信号映射" prop="amount5" width="180">
        <template #default="{ row, $index }">
          <el-input
            v-model="tableData[$index]['dbc_mapping']"
            :disabled="row['type'] != 2"
            placeholder="自定义填写内容"
          ></el-input>
        </template>
      </el-table-column>
      <el-table-column label="代码" prop="amount6" width="180">
        <template #default="{ row, $index }">
          <el-input
            v-model="tableData[$index]['code']"
            :disabled="row['type'] != 3"
            placeholder="自定义填写内容"
          ></el-input>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style lang="scss" scoped>
.script-processor-container {
  border-bottom: 1px solid #ebebeb;
  height: 32px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  position: relative;
}
.script-processor {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  padding: 16px;
  position: absolute;
  left: 0;
  top: 30px;
}
</style>
