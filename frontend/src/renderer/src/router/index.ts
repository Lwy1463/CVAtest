import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'

const layout = () => import('@renderer/views/layout/index.vue')

export const constantRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@renderer/views/login.vue')
  },
  {
    path: '/registry',
    name: 'registry',
    component: () => import('@renderer/views/registry.vue')
  },
  {
    path: '/',
    name: 'root',
    component: layout,
    redirect: '/project',
    children: [
      {
        path: '/project',
        name: 'project',
        meta: {
          title: '测试项目'
        },
        component: () => import('@renderer/views/TestProject.vue')
      },
      {
        path: '/test-object',
        name: 'test-object',
        meta: {
          title: '测试对象'
        },
        component: () => import('@renderer/views/TestObject.vue')
      },
      {
        path: '/device-config',
        name: 'device-config',
        meta: {
          title: '设备配置'
        },
        component: () => import('@renderer/views/DeviceConfig.vue')
      },
      {
        path: '/corpus',
        name: 'corpus',
        meta: {
          title: '语料库'
        },
        component: () => import('@renderer/views/corpus/CorpusMain.vue')
      },
      {
        path: '/tag-library',
        name: 'tag-library',
        meta: {
          title: '标签库'
        },
        component: () => import('@renderer/views/TagLibrary.vue')
      },
      {
        path: '/customPlan',
        name: 'customPlan',
        component: () => import('@renderer/views/customPlan/CustomPlan.vue')
      },
      {
        path: '/execution',
        name: 'execution',
        component: () => import('@renderer/views/execution/ExecutionMain.vue')
      },
      {
        path: '/playconfig',
        name: 'playconfig',
        component: () => import('@renderer/views/playconfig/PlayConfig.vue')
      },
      {
        path: '/record',
        name: 'record',
        component: () => import('@renderer/views/record/Record.vue')
      },
      {
        path: '/synthesize',
        name: 'synthesize',
        component: () => import('@renderer/views/synthesize/Synthesize.vue')
      },
      {
        path: '/resultCheck',
        name: 'resultCheck',
        component: () => import('@renderer/views/execution/ResultCheck.vue')
      },
      {
        path: '/batchSynthesize',
        name: 'batchSynthesize',
        component: () => import('@renderer/views/synthesize/BatchSynthesize.vue')
      },
      {
        path: '/labelManage',
        name: 'labelManage',
        component: () => import('@renderer/views/labelManage/LabelManage.vue')
      }
    ]
  },

]

const router = createRouter({
  history: createWebHashHistory(),
  scrollBehavior() {
    // 始终滚动到顶部
    return { top: 0 }
  },
  routes: constantRoutes
})

export default router