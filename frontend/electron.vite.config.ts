import { resolve } from 'path'
import { defineConfig, externalizeDepsPlugin } from 'electron-vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx';
// @ts-ignore
import UnoCSS from 'unocss/vite'
// @ts-ignore
import postCssPxToRem from 'postcss-pxtorem'
import nodePolyfills from 'vite-plugin-node-stdlib-browser'

export default defineConfig({
  main: {
    plugins: [externalizeDepsPlugin()]
  },
  preload: {
    plugins: [externalizeDepsPlugin()]
  },
  renderer: {
    server: {
      port: 9200,
      proxy: {
        '/dev-api/': {
          // target: 'http://192.168.215.177:8080',
          target: 'http://127.0.0.1:8080',
          changeOrigin: true,
          rewrite: (path) => path.replace(/\/dev-api/, '')
        },
        '/static/': {
          target: 'http://127.0.0.1:8080',
          changeOrigin: true,
        },
        '/mic_static/': {
          target: 'http://127.0.0.1:8080',
          changeOrigin: true,
        },
        '/audio/': {
          target: 'http://127.0.0.1:8080',
          changeOrigin: true,
        },
        '/photo/': {
          target: 'http://127.0.0.1:8080',
          changeOrigin: true,
        }
      }
    },
    resolve: {
      alias: {
        '@renderer': resolve('src/renderer/src')
      }
    },
    plugins: [UnoCSS(),     vue(),
      vueJsx(), nodePolyfills()],
    css: {
      postcss: {
        plugins: [
          postCssPxToRem({
            rootValue: 16,
            propList: ['*']
          })
        ]
      }
    }
  }
})
