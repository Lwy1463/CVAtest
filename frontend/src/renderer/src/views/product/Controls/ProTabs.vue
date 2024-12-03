<script lang="ts" setup>
import { Close, Plus } from '@element-plus/icons-vue'
import { useTagsStore } from '@renderer/stores/useTagsStore'
import { useRoute, useRouter } from 'vue-router'
import AddOrUpdate from '@renderer/views/product/AddOrUpdate.vue'
import { useProductFetch } from '../useProductFetch'
import { ref } from 'vue'

const router = useRouter()
const route = useRoute()
const store = useTagsStore()

const onClickItem = (item: any) => {
  router.push('/controls')
  store.current = item
}
const onClickClose = () => {
  store.removeTag()
  if (store.tags.length == 0) {
    router.push('/')
  }
}
const dialogVisible = ref(false)
const { handler } = useProductFetch()

const onCreated = () => {
  handler.List().then((list) => {
    handler.Detail(list[0]._id.$oid).then((detail) => {
      store.addTag(detail)
      router.push('/controls')
    })
  })
}
</script>

<template>
  <div class="pro-nav">
    <div
      v-for="tag in store.tags"
      :key="tag._id.$oid"
      :class="{
        'is-active': store.current?._id.$oid === tag._id.$oid && route.name === 'controls'
      }"
      class="tag-item no-drag"
      @click.stop="onClickItem(tag)"
    >
      <span class="clamp-1">{{ tag.name }}</span>
      <el-icon @click.stop="onClickClose"><Close /></el-icon>
    </div>
    <el-icon class="text-[#4E5969] cursor-pointer no-drag" size="18" @click="dialogVisible = true"
      ><Plus
    /></el-icon>
  </div>
  <el-dialog v-model="dialogVisible" destroy-on-close title="创建项目" width="540">
    <AddOrUpdate @on-close="dialogVisible = false" @on-success="onCreated" />
  </el-dialog>
</template>

<style lang="scss" scoped>
.pro-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 1000;
  .tag-item {
    flex-shrink: 0;
    width: 130px;
    height: 40px;
    border-radius: 4px;
    background: #343844;
    display: inline-flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 10px;
    color: rgba(255, 255, 255, 0.4);
    cursor: pointer;
    .el-icon {
      display: inline-block;
    }

    &.is-active {
      background: #000;
      color: #fff;
    }
  }
}
</style>
