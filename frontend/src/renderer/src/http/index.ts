import axios from 'axios'
import { ElMessage } from 'element-plus'

// Determine the base URL based on the environment
const baseURL = process.env.NODE_ENV === 'production'
  ? import.meta.env.VITE_APP_PRODUCTION
  : import.meta.env.VITE_APP_BASE_API;

console.info('baseURL ' + baseURL + process.env.NODE_ENV)

// Create Axios instance
const http = axios.create({
  baseURL: baseURL, // Set the base request URL
  timeout: 60000 // Set the request timeout
});


// 请求拦截器
http.interceptors.request.use(
  (config) => {
    // 在发送请求之前做一些处理，例如添加请求头、身份验证等
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token
    }

    // 删除请求参数中的下划线开头的参数
    ;[config.params, config.data].forEach((params) => {
      for (const p in params) {
        if (p.startsWith('_')) {
          delete params[p]
        }
        // if(params[p] === "") {
        //   delete params[p];
        // }
      }
    })
    return config
  },
  (error) => {
    // 处理请求错误
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  (response) => {
    // 对响应数据进行处理，例如解析数据、错误处理等
    if (response.data.err_msg || response.data.error || response.data.error_msg) {
      ElMessage.error(response.data.err_msg || response.data.error || response.data.error_msg)
    }
    if (response.status === 500) {
      ElMessage.error(response.data.message)
      return Promise.reject(response)
    }
    return response.data
  },
  (error) => {
    if (error.response.status === 401) {
      window.location.href = '#/product'
    }
    // 处理响应错误
    return Promise.reject(error)
  }
)

export { http }
