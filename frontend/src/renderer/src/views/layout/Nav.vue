<template>
  <div class="nav-container" @click="dosomething">
    <div class="nav-mid">
      <div class="nav-items">
        <img :src="logo" class="logo">
        <div class="app-name">G-VoTest</div>
        <div> </div>
        <div
          v-for="item in navItems"
          :key="item.path"
          :class="route.path === item.path ? 'active' : ''"
          class="nav-item"
          @click="goToPath(item.path)"
        >
          {{ item.name }}
        </div>
      </div>
    </div>
    <div class="close-button" @click="minWindow">
      <span>-</span>
    </div>
    <div class="close-button" @click="closeWindow">
      <span>×</span>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { useElectronVar } from '@renderer/stores/useElectronVarStore';
import { onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import logo from './logoPurple.jpg'

const router = useRouter();
const route = useRoute();
const { platform } = useElectronVar();

const dosomething = () => {
  console.log(111);
};

const navItems = [
  { name: '测试项目', path: '/project' },
  // { name: '测试对象', path: '/test-object' },
  { name: '设备配置', path: '/device-config' },
  { name: '语料库', path: '/corpus' },
  // { name: '标签库', path: '/tag-library' },
  { name: '播放配置', path: '/playconfig' },
  // { name: '自定义方案', path: '/customPlan' },
  // { name: '录制音频', path: '/record' },
  { name: '合成语料', path: '/synthesize' },
  { name: '标签库', path: '/labelManage'}
];

const toHome = () => {
  router.push('/');
};

const goToPath = (path) => {
  console.log(path);
  router.push(path);
};

const closeWindow = () => {
  window.electron.ipcRenderer.send('app-quit');
};

const minWindow = () => {
  window.electron.ipcRenderer.send('app-minimize');
}

onMounted(() => {
  console.log(111);
});
</script>

<style lang="scss" scoped>
.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 62px;
  box-sizing: border-box;
  background: #F1E1FA; /* 修改背景颜色 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  position: relative;
  overflow: hidden;
  -webkit-app-region: drag;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, rgba(199, 47, 47, 0.1), rgba(62, 65, 168, 0.05) 50%, transparent 50%);
    z-index: 1;
    pointer-events: none;
  }

  .nav-mid {
    width: 100%;
    overflow: hidden;
    padding: 0 48px;
    box-sizing: border-box;
    display: flex;
    align-items: center;
  }

  .nav-items {
    display: flex;
    gap: 20px;
    position: relative;
    z-index: 2;
    align-items: center;

    .logo {
      height: 100%;
      width: 3rem;
      margin-right: -10px; /* 调整Logo和应用名称之间的间距 */
    }

    .app-name {
      font-family: 'Alibaba Sans', sans-serif; /* 修改字体 */
      font-size: 1rem;
      background: linear-gradient(90deg, #40397B, #9A4596); /* 修改字体颜色为渐变 */
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-right: 20px; /* 调整应用名称和导航项之间的间距 */
    }

    .nav-item {
      cursor: pointer;
      color: #383838; /* 修改未选中字体颜色 */
      padding: 8px 12px;
      border-radius: 4px;
      transition: background 0.3s ease, color 0.3s ease;
      position: relative;
      -webkit-app-region: no-drag;

      &::before {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, rgba(64, 57, 123, 0.3), rgba(154, 69, 150, 0.3)); /* 修改选中颜色为更浅的渐变 */
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.3s ease;
      }

      &:hover {
        background: rgba(255, 255, 255, 0.1);

        &::before {
          transform: scaleX(1);
        }
      }

      &.active {
        color: #9A4596; /* 修改选中颜色 */
        background: rgba(64, 158, 255, 0.1);

        &::before {
          transform: scaleX(1);
        }
      }
    }
  }

  .close-button {
    cursor: pointer;
    color: #C8A2C8; /* 修改字体颜色为淡紫色 */
    padding: 8px 12px;
    border-radius: 4px;
    transition: background 0.3s ease, color 0.3s ease, transform 0.3s ease;
    position: relative;
    -webkit-app-region: no-drag;
    border: 1px solid transparent; /* 添加透明边框 */

    &:hover {
      background: rgba(200, 162, 200, 0.1); /* 修改悬浮背景颜色为淡紫色 */
      border-color: rgba(200, 162, 200, 0.3); /* 悬浮时显示边框 */
      transform: scale(1.05); /* 悬浮时稍微放大 */
    }

    span {
      font-size: 18px;
      font-weight: bold;
    }
  }
}
</style>