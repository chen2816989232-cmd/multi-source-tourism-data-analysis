import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

const apiProxyTarget = process.env.API_PROXY_TARGET || 'http://127.0.0.1:8000'

export default defineConfig({
  root: __dirname,
  plugins: [
    vue(),
  ],

  resolve: {
    //设置路径别名
    alias: {
      "@": resolve(__dirname, "src/")
    },
  },

  server: {

    // 服务器默认端口是8080，前端默认8081，所以需要代理
    port: 8081,
    host: "0.0.0.0",

    // 自动打开浏览器
    open: false, 

    // 设置代理
    proxy: {
      "/lvxing2f63wq5x": {
        target: apiProxyTarget,
        changeOrigin: true,
        ws: true,
      },
    },
  },

  // 打包后的文件引入路径 由/assets，改为./assets
  base: "./",
  build: {
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: false,
  },
})
