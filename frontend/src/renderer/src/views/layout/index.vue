<script lang="ts" setup>
import Nav from '@renderer/views/layout/Nav.vue'
import Header from '@renderer/views/layout/Header.vue'
</script>

<template>
  <div class="layout-container">
    <Nav></Nav>
    <div class="layout-content">
      <router-view v-slot="{ Component }">
        <component :is="Component" />
      </router-view>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.layout-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  .layout-header {
    background: #fff;
    flex-shrink: 0;
  }
  .layout-content {
    height: 100%;
    background: #eee;
    overflow: auto;
  }
}
</style>
