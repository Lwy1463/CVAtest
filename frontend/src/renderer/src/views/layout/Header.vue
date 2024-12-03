<script lang="ts" setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="header-container">
    <div class="header-left">
      <!--      <img alt="logo" src="/svgs/logo.svg" />-->
      <!--      <div class="w-[1px] h-[18px] bg-[#ccc]"></div>-->
      <!--      <h1 class="text-[#333] text-[24px]">Genesis for test</h1>-->
      <img alt="" src="/svgs/title.svg" />
    </div>
    <div class="header-right"></div>
  </div>
</template>

<style lang="scss" scoped>
.header-container {
  height: 54px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 36px;
  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;
  }
}
</style>
