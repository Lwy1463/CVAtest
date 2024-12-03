<script lang="ts" setup>
const props = defineProps<{
  description?: string
}>()
</script>

<template>
  <el-empty :description="description || '暂无数据'">
    <template #image>
      <img alt="" class="w-[100px]!" src="/images/empty.png" />
    </template>
  </el-empty>
</template>

<style lang="scss" scoped></style>
