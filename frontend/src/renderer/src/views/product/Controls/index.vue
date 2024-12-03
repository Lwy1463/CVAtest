<script lang="ts" setup>
import { useTagsStore } from '@renderer/stores/useTagsStore'
import DocumentInner from '@renderer/views/product/Controls/DocumentInner.vue'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const store = useTagsStore()
const router = useRouter()

onMounted(() => {
  if (store.tags.length === 0) {
    router.push('/product')
  }
})
</script>

<template>
  <div class="controls-container">
    <div
      v-for="pro in store.tags"
      v-show="pro._id.$oid === store.current!._id.$oid"
      :key="pro._id.$oid"
      class="pro-item"
    >
      <DocumentInner />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.controls-container {
  position: fixed;
  top: 53px;
  left: 0;
  right: 0;
  bottom: 0;
  background: #f7f7fb;
  .pro-item {
    //height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
  }
}
</style>
