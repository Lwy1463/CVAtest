<script lang="ts" setup>
import { provide, ref } from 'vue'
import DocumentRequirement from '@renderer/views/product/Controls/DocumentRequirement.vue'
import DocumentConfiguration from '@renderer/views/product/Controls/DocumentConfiguration.vue'
import DocumentScript from '@renderer/views/product/Controls/DocumentScript.vue'
import DownloadFileCard from './DownloadFileCard.vue'
import { useTagsStore } from '../../../stores/useTagsStore'

const store = useTagsStore()

const currentTabIdx = ref(0)
provide('currentTabIdx', currentTabIdx)
const controlsTabs = ref([
  {
    title: '需求配置',
    statusKey: 'test_requirements',
    list: ['未上传', '已上传', '已处理']
  },
  {
    title: '用例配置',
    statusKey: 'test_cases',
    list: ['未处理', '处理中', '已处理', '未知错误', '已取消']
  },
  // {
  //   title: '脚本配置',
  //   statusKey: 'test_scripts',
  //   list: ['未处理', '处理中', '已处理', '待处理', '出错了', '已取消']
  // }
])

const formData = ref({
  storage_path: store.current!.storage_path.split('/'),
  isEditStoragePath: false
})

const onOpenDir = (dir: string) => {
  window.electron.ipcRenderer.send('open-path', dir)
}

const isFold = ref(false)
</script>

<template>
  <div class="controls-inner">
    <div :class="{ 'is-fold': isFold }" class="controls-left">
      <div class="flex items-center gap-[12px]">
        <img alt="" class="w-[48px]" src="/images/product-icon.png" />
        <div>
          <p class="text-[16px] clamp-1">{{ store.current!.name }}</p>
          <div class="text-[#666] flex">
            <p>ID：</p>
            <p class="w-[100px] clamp-1">{{ store.current!.display_id }}</p>
          </div>
        </div>
      </div>
      <div class="gutter-line"></div>
      <div class="text-[14px] text-[#333] w-full">
        <!--        <div class="flex items-center gap-[16px]">-->
        <!--          <p class="text-[#999] whitespace-nowrap">项目存储路径</p>-->
        <!--          <div-->
        <!--            class="flex items-center gap-[2px] cursor-pointer"-->
        <!--            @click="onOpenDir(store.current!.storage_path)"-->
        <!--          >-->
        <!--            <el-icon><FolderOpened /></el-icon>-->

        <!--            <p class="clamp-1 w-[130px]">{{ store.current!.storage_path }}</p>-->
        <!--          </div>-->
        <!--        </div>-->
        <!--        <div class="flex items-center gap-[16px]">-->
        <!--          <p class="text-[#999] whitespace-nowrap">项目下载路径</p>-->
        <!--          <div-->
        <!--            class="flex items-center gap-[2px] cursor-pointer"-->
        <!--            @click="onOpenDir(store.current!.download_path)"-->
        <!--          >-->
        <!--            <el-icon><FolderOpened /></el-icon>-->
        <!--            <p class="clamp-1 w-[130px]">{{ store.current!.download_path }}</p>-->
        <!--          </div>-->
        <!--        </div>-->
        <div class="flex items-center gap-[16px] mb-[10px]">
          <p class="text-[#999]">创建时间</p>
          <p>{{ store.current!._create_at }}</p>
        </div>
        <div class="flex items-center gap-[16px]">
          <p class="text-[#999]">更新时间</p>
          <p>{{ store.current!._update_at }}</p>
        </div>
      </div>
      <div class="gutter-line"></div>
      <p class="font-bold">项目描述</p>
      <p class="text-[#666] mt-[6px] whitespace-normal">
        {{ store.current!.notes || '暂无描述' }}
      </p>
      <div class="gutter-line mt-[40px]! mb-[20px]!"></div>
      <DownloadFileCard />
    </div>
    <div :class="{ 'is-fold': isFold }" class="controls-right">
      <img alt="" class="fold-icon" src="/svgs/fold.svg" @click="isFold = !isFold" />
      <div class="controls-box">
        <div class="controls-tabs">
          <div
            v-for="(tab, index) in controlsTabs"
            :key="index"
            :class="{ 'is-active': currentTabIdx === index }"
            class="controls-tabs-item"
            @click="currentTabIdx = index"
          >
            <p class="text-title">{{ tab.title }}</p>
            <p
              :class="{ 'is-success': [1, 2].includes(+store.current!.status[tab.statusKey]) }"
              class="text-tag"
            >
              {{ tab.list[+store.current!.status[tab.statusKey]] || '生成错误' }}
            </p>
          </div>
        </div>
        <div class="controls-panel">
          <DocumentRequirement v-show="currentTabIdx === 0" />
          <DocumentConfiguration
            v-show="currentTabIdx === 1"
            @goto-req="() => (currentTabIdx = 0)"
          />
          <DocumentScript v-show="currentTabIdx === 2" />
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.controls-inner {
  display: flex;
  background: #f3f3f3;
  height: 100%;

  .controls-left {
    width: 280px;
    flex-shrink: 0;
    padding: 16px 20px;
    box-sizing: border-box;
    font-size: 14px;
    color: #333;
    overflow: hidden;
    position: relative;
    white-space: nowrap;
    transition: width 0.3s;

    .gutter-line {
      width: 100%;
      height: 1px;
      background: #ebebeb;
      margin: 16px 0;
    }
    &.is-fold {
      width: 0;
      padding: 16px 0;
      margin-right: 16px;
    }
  }

  .controls-right {
    width: 100%;
    position: relative;
    .fold-icon {
      position: absolute;
      top: 50%;
      left: -11px;
      cursor: pointer;
    }
    &.is-fold {
      .fold-icon {
        transform: rotate(180deg);
        left: -16px;
      }
    }
  }

  .controls-box {
    border: 1px #ddd solid;
    border-radius: 4px;
    height: calc(100% - 32px);
    margin: 16px 16px 16px 0;
    box-sizing: border-box;
    overflow: hidden;
    .controls-tabs {
      height: 44px;
      display: flex;
      align-items: center;
      background: #fff;
      border-bottom: 1px #ebebeb solid;
      box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.1);
      position: relative;
      z-index: 999;
      &-item {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        width: 158px;
        gap: 8px;
        cursor: pointer;
        position: relative;
        .text-title {
          font-size: 14px;
          font-style: normal;
          font-weight: 500;
          line-height: normal;
          color: #333;
        }

        .text-tag {
          padding: 2px 6px;
          border-radius: 2px;
          font-size: 12px;
          background: #f2f3f5;
          color: #86909c;
          &.is-success {
            background: #e8ffea;
            color: #00b42a;
          }
        }

        &.is-active {
          color: #333;
          background: rgba(213, 104, 207, 0.1);
          .text-title {
            color: #c833c1;
            font-family: 'PingFang SC';
          }
          .text-tag {
            background: #fff;
            color: #86909c;
            &.is-success {
              background: #e8ffea;
              color: #00b42a;
            }
          }

          &:before {
            content: '';
            position: absolute;
            bottom: 0px;
            left: 0;
            width: 100%;
            height: 3px;
            background: #c833c1;
          }
        }
      }
    }

    .controls-panel {
      height: calc(100% - 44px);
    }
  }
}
</style>
