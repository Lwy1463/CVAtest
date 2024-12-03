<script lang="ts" setup>
import { onBeforeMount } from 'vue'
import { Lock, Message, User } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { http } from '@renderer/http'
import { useFormData } from '@renderer/hooks/useFormData'
import { ElMessage } from 'element-plus'

const { formData, formDataRef, formDataRules } = useFormData(
  {
    email: '',
    username: '',
    password: '',
    password2: '',
    affiliation: ''
  },
  {
    username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
    email: [
      { required: true, message: '请输入邮箱', trigger: 'blur' },
      {
        pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        message: '邮箱格式有误',
        trigger: 'blur'
      }
    ],
    password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
    password2: [
      {
        validator: (rule: any, value: any, callback: any) => {
          if (value === '') {
            callback(new Error('请再次输入密码'))
          } else if (value !== formData.password) {
            callback(new Error('两次输入密码不一致!'))
          } else {
            callback()
          }
        },
        trigger: 'blur'
      }
    ]
  }
)

const router = useRouter()
const onSubmitFormData = () => {
  formDataRef.value?.validate((valid: boolean) => {
    if (valid) {
      registryFetch()
    } else {
      return false
    }
  })
}

const registryFetch = async () => {
  try {
    const res: any = await http.post('/auth/register', formData)
    if (res.status === 'success') {
      router.replace('/login').then(() => {
        // TODO: 把注册成功的账号密码带到登录页面自动填充
      })
      ElMessage.success(res.message)
    } else {
      ElMessage.error(res.message)
    }
  } catch (error) {
    console.log(error)
  }
}

onBeforeMount(() => {
  window.electron.ipcRenderer.send('set-window-size', 720, 480)
})
</script>

<template>
  <div class="registry-container flex-between">
    <div class="w-[38%] h-vh pos-relative">
      <img alt="logo" class="logo-img" src="/svgs/logo.svg" />
      <img class="registry-img" src="/images/login-bg.png" />
      <img class="logo-area" src="/images/login-bg-mask.png" />
    </div>
    <div class="registry-form w-[62%] h-vh">
      <h1 class="mt-[50px] mb-[20px] m-0 text-5 line-height-[28px]">注册账号</h1>
      <el-form ref="formDataRef" :model="formData" :rules="formDataRules" class="no-drag">
        <el-form-item prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名称">
            <template #prefix>
              <el-icon size="24">
                <User />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="formData.email" placeholder="请输入有效邮箱">
            <template #prefix>
              <el-icon size="24">
                <Message />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="formData.password"
            placeholder="请输入密码"
            show-password
            type="password"
          >
            <template #prefix>
              <el-icon size="24">
                <Lock />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password2">
          <el-input
            v-model="formData.password2"
            placeholder="请再次输入密码"
            show-password
            type="password"
          >
            <template #prefix>
              <el-icon size="24">
                <Lock />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-button class="registry-btn" type="primary" @click="onSubmitFormData">注册</el-button>
      </el-form>
      <div class="flex-center mt-[20px]">
        <span class="mr-2">已有账号</span>
        <router-link class="no-drag text-[#DB22D9]" to="/login">登录</router-link>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
.registry-container {
  width: 100%;
  height: 100%;
  position: relative;
  background: #fff;
  -webkit-user-select: none;
  -webkit-app-region: drag;
  .el-icon {
    color: #333333;
  }
  .logo-img {
    position: absolute;
    width: 148px;
    height: 44px;
    top: 41px;
    left: 30px;
    padding: 18px 32px;
  }

  .registry-img {
    width: 200px;
    height: 225px;
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    margin-top: 67%;
  }

  .logo-area {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 1;
    width: 100%;
    height: 100%;
  }

  .el-form--container {
    -webkit-app-region: no-drag;
  }

  .registry-form {
    position: relative;
    padding: 0 70px;
    box-sizing: border-box;
    background: #fff;
    text-align: left;

    .el-form-item {
      // margin-bottom: 10px !important;
    }

    .el-input {
      --el-input-bg-color: #fbfbfb !important;

      .el-input__prefix {
        margin-right: 10px;
      }
      .el-input__wrapper {
        padding: 1px 20px;
        box-shadow: none;
      }
      .el-input__inner {
        height: 46px;
        font-size: 16px;
      }
    }

    .registry-btn {
      width: 100%;
      height: 46px;
      font-size: 16px;
      margin-top: 8px;
    }
  }
}
</style>
