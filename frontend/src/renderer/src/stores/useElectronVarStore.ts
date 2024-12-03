import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useElectronVar = defineStore('electronVar', () => {
  // electron 应用当前的操作系统
  const platform = ref(window.platform)

  return {
    platform
  }
})
