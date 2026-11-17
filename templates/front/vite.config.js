import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

const apiProxyTarget = process.env.API_PROXY_TARGET || 'http://127.0.0.1:8000'

export default defineConfig({
  root: __dirname,
  plugins: [
    vue()
  ],

  resolve: {
    //设置路径别名
    alias: {
      "@": resolve(__dirname, "src/")
    },
  },

  server: {

    // 服务器默认端口是8080，后台默认8081，前台8082所以需要代理
    port: 8082,
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

  // The Django site serves the public build under /front/dist/.
  base: "/front/dist/",
  build: {
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: false,
  },
})
