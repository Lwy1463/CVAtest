<script lang="ts" setup>
import { onBeforeMount } from 'vue'
import { Close, Lock, Message } from '@element-plus/icons-vue'
import { http } from '@renderer/http'
import { useRouter } from 'vue-router'
import { useFormData } from '@renderer/hooks/useFormData'
import { ElMessage } from 'element-plus'
import { quitApp, unmaximizeApp } from '@renderer/utils/tools'
import { useElectronVar } from '../stores/useElectronVarStore'

const { platform } = useElectronVar()
const { formData, formDataRef, formDataRules } = useFormData(
  {
    email: window.localStorage.getItem('email') || '',
    password: window.localStorage.getItem('password') || '',
    remember_me: true
  },
  {
    email: [
      { required: true, message: '请输入邮箱', trigger: 'blur' },
      {
        pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        message: '邮箱格式有误',
        trigger: 'blur'
      }
    ],
    password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
  }
)

const router = useRouter()
const onSubmitFormData = () => {
  formDataRef.value?.validate((valid: boolean) => {
    if (valid) {
      loginFetch()
    } else {
      return false
    }
  })
}

const loginFetch = async () => {
  try {
    const res: any = await http.post('/auth/login', formData)
    if (res.status === 'success') {
      window.localStorage.setItem('email', formData.email)
      if (formData.remember_me) {
        window.localStorage.setItem('password', formData.password)
      } else {
        window.localStorage.removeItem('password')
      }
      window.localStorage.setItem('token', res.access_token)
      router.replace('/').then(() => {
        window.electron.ipcRenderer.send('set-window-size', 1440, 900)
      })
    } else {
      ElMessage.error(res.message)
    }
  } catch (error) {
    console.log(error)
  }
}

onBeforeMount(() => {
  unmaximizeApp()
  window.electron.ipcRenderer.send('set-window-size', 720, 480)
})
</script>

<template>
  <div class="login-container flex-between">
    <div class="w-[38%] h-dvh pos-relative">
      <img alt="logo" class="logo-img" src="/svgs/logo.svg" />
      <img class="login-img" src="/images/login-bg.png" />
      <img class="logo-area" src="/images/login-bg-mask.png" />
    </div>
    <div class="login-form w-[62%] h-vh">
      <h1 class="mt-[100px] mb-[40px] m-0 text-5 line-height-[28px] text-[#333]">
        欢迎使用 GENESIS FOR TEST
      </h1>
      <el-form ref="formDataRef" :model="formData" :rules="formDataRules" class="no-drag">
        <el-form-item prop="email">
          <el-input v-model="formData.email" placeholder="邮箱" @keydown.enter="onSubmitFormData">
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
            placeholder="密码"
            show-password
            type="password"
            @keydown.enter="onSubmitFormData"
          >
            <template #prefix>
              <el-icon size="24">
                <Lock />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="remember_me">
          <el-checkbox v-model="formData.remember_me" label="记住密码"></el-checkbox>
        </el-form-item>
        <el-button class="login-btn" type="primary" @click="onSubmitFormData">登录</el-button>
      </el-form>
    </div>
    <div v-if="platform === 'win32'" class="quit-app" @click="quitApp">
      <el-icon size="24">
        <Close />
      </el-icon>
    </div>
  </div>
</template>

<style lang="scss">
.login-container {
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

  .login-img {
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

  .login-form {
    position: relative;
    padding: 0 70px;
    box-sizing: border-box;
    background: #fff;
    text-align: left;

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

    .login-btn {
      width: 100%;
      height: 46px;
      font-size: 16px;
      margin-top: 8px;
    }
  }
}
.quit-app {
  position: fixed;
  top: 20px;
  right: 20px;
  color: #666;
  z-index: 999;
  cursor: pointer;
  -webkit-app-region: no-drag;
}
.title-bar-overlay {
  display: none;
}
</style>
