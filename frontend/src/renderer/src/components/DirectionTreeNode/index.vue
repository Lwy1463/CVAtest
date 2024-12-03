<script lang="ts" setup>
import { onUnmounted } from 'vue'
import { useVModel } from '@vueuse/core'

const props = defineProps<{
  modelValue: string
  kind: string
}>()
const emit = defineEmits(['update:modelValue', 'node-click'])

const selected = useVModel(props, 'modelValue', emit)

// let resolveFn: Function
// const currentPath = ref<string>()
// const currentPath = ref<string[]>([])
// window.electron.ipcRenderer.on('direction', (_, dir, kind) => {
//   if (props.kind === kind) {
//     resolveFn(
//       dir.map((x) => {
//         return {
//           label: x,
//           value: x,
//           children: []
//         }
//       })
//     )
//   }
// })
//
// const cascaderProps: CascaderProps = {
//   // multiple: true,
//   checkStrictly: true,
//   lazy: true,
//   lazyLoad(node, resolve) {
//     if (node.level === 1) currentPath.value = ['/']
//     if (node.level === currentPath.value.length - 1) {
//       currentPath.value[node.level] = `${node.data!.value || '/'}`
//     } else {
//       currentPath.value.push(`${node.data!.value || '/'}`)
//     }
//     resolveFn = resolve
//     window.electron.ipcRenderer.send(
//       'direction',
//       '/' + [...new Set(currentPath.value.slice(1))].join('/'),
//       props.kind
//     )
//   }
// }
// onUnmounted(() => {
//   window.electron.ipcRenderer.removeAllListeners('direction')
// })

window.electron.ipcRenderer.on('open-directory', (_, dir, kind) => {
  if (kind === props.kind && dir) {
    selected.value = dir
  }
})
const onClickOpenDir = () => {
  window.electron.ipcRenderer.send('open-directory', props.kind)
}

onUnmounted(() => {
  window.electron.ipcRenderer.removeAllListeners('open-directory')
})
</script>

<template>
  <!--  <el-cascader-->
  <!--    v-model="selected"-->
  <!--    :props="cascaderProps"-->
  <!--    placeholder="请选择下载路径"-->
  <!--    @change="emit('node-click', selected)"-->
  <!--  />-->
  <el-input v-model="selected" placeholder="请输入保存路径" readonly @click="onClickOpenDir" />
</template>

<style lang="scss" scoped></style>
