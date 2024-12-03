<script lang="ts" setup>
import { useFormData } from '@renderer/hooks/useFormData'
import DirectionTreeNode from '../../components/DirectionTreeNode/index.vue'
import { useProductFetch } from './useProductFetch'
import { ArrowRight } from '@element-plus/icons-vue'

const emit = defineEmits(['on-close', 'on-success'])

const { formData, formDataRef, formDataRules } = useFormData(
  {
    name: '',
    kind: '',
    storage_path: [],
    download_path: [],
    notes: ''
  },
  {
    name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
    kind: [{ required: true, message: '请输入项目类型', trigger: 'change' }],
    storage_path: [{ required: true, message: '请输入保存路径', trigger: 'change' }],
    // download_path: [{ required: true, message: '请输入下载路径', trigger: 'change' }],
    description: [{ required: true, message: '请输入项目描述', trigger: 'blur' }]
  }
)

const { handler } = useProductFetch()
const onSubmitFormData = () => {
  formDataRef.value?.validate((valid, fields) => {
    if (valid) {
      const params = {
        ...formData
      }
      handler.Create(params).then(() => {
        emit('on-success')
        emit('on-close')
      })
    } else {
      console.log('error submit!!')
      return false
    }
  })
}
</script>

<template>
  <div class="cu-container">
    <el-form ref="formDataRef" :model="formData" :rules="formDataRules" label-width="120">
      <el-form-item label="项目名称" prop="name">
        <el-input
          v-model="formData.name"
          maxlength="20"
          placeholder="输入项目名称，最多20字符"
        ></el-input>
      </el-form-item>
      <el-form-item label="项目类型" prop="kind">
        <el-select v-model="formData.kind" placeholder="请输入项目类型">
          <el-option label="VT" value="VT" />
          <el-option label="NI" value="NI" />
          <el-option label="eSPACE" value="eSPACE" />
        </el-select>
      </el-form-item>
      <el-form-item label="项目保存路径" prop="storage_path">
        <DirectionTreeNode
          v-model="formData.storage_path"
          :suffix-icon="ArrowRight"
          class="w-full!"
          kind="storage_path"
        />
      </el-form-item>
      <el-form-item label="下载文件路径" prop="download_path">
        <DirectionTreeNode
          v-model="formData.download_path"
          :suffix-icon="ArrowRight"
          class="w-full!"
          kind="download_path"
        />
      </el-form-item>
      <el-form-item label="项目描述" prop="notes">
        <el-input
          v-model="formData.notes"
          maxlength="50"
          placeholder="请输入项目描述，最多不超过50字。"
          type="textarea"
        ></el-input>
      </el-form-item>
    </el-form>
    <div class="flex-end">
      <!--      <el-button @click="emit('on-close')">取消</el-button>-->
      <el-button type="primary" @click="onSubmitFormData">提交创建</el-button>
    </div>
  </div>
</template>

<style lang="scss">
.cu-container {
  .el-input__wrapper,
  .el-select__wrapper,
  .el-textarea__inner {
    padding: 1px 14px;
    box-shadow: none;
    background: #f2f3f5;
  }
}
</style>
