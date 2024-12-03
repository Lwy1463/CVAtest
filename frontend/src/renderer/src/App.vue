<script lang="ts" setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  router.push('/project')
})

// const ipcHandle = () => window.electron.ipcRenderer.send('ping')
</script>

<template>
  <a-config-provider
    :theme="{
      token: {
        // colorPrimary: '#db4aeb',
        // colorPrimary: '#68397b'
        // colorPrimary: '#8f3d8b'
        wireframe: false,
        colorPrimary: '#edb4f7'
      },
    }"
  >
  <router-view></router-view>
</a-config-provider>

</template>

<style>
:deep(.ant-btn) {
  color: purple !important;
}
</style>
