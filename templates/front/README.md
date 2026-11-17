# 基于 Vue 3 + Vite + Element-plus 框架

| 依赖         | 版本    | 功能     |
| ------------ | ------- | -------- |
| nodejs      | >22.12     |          |
| vue          | 3.5.14  | 框架     |
| vite         | 7.1.17  | 构建工具 |
| vue-router   | 4.5.1   | 路由     |
| pinia        | 3.0.2   | 状态管理 |
| element-plus | 2.9.10  | UI组件   |
| axios        | 1.9.0   | http请求 |
| echarts      | 5.5.0   | 图表     |
| animate.css  | 4.1.1   | 动画样式 |
| dayjs        | 1.11.11 | 时间处理 |
| sass | 1.93.2 | css预处理 |

## 环境搭建

### 1. node环境
- **安装地址**: 百度搜索 node.js,或者访问网址 https://nodejs.org/zh-cn
- **安装成功**:
  ```bash
  # 命令行输入 版本检测
  node --version
  
  # 返回版本号，表示安装成功
  # 如果没有，可以尝试重启电脑再试试
  v22.16.0
  ```

### 2. vscode环境
- **安装地址**: 百度搜索 vscode,或者访问网址 https://code.visualstudio.com/;一直点 next、使用默认配置就行。
- **插件**: 
  - 汉化: Chinese (Simplified) (简体中文) Language Pack for Visual Studio Code
  - 格式化: Prettier - Code formatter
  - 语法提示: Vue (Official)

## 启动命令
``` bash
# 安装依赖
npm install

# 启动
npm run serve

# 打包
npm run build
```
#### 配置淘宝镜像源
如果执行 `npm install`、卡主的话，可以更换下淘宝镜像
``` bash
# 查看当前源
npm config get registry

# 切换为淘宝镜像（推荐）
npm config set registry https://registry.npmmirror.com
```
#### 删除无用文件
在文件夹，直接双击 `双击删除无用文件.bat` ，会删除无用文件

## 目录结构
```
├── .vscode/                    # vscode 推荐插件
├── dist/                       # 打包后的代码
├── public/                     # 静态资源
│   └── icon.svg                # 网站图标
├── src/                        # 源代码
│   ├── api/                    # API 接口
│   ├── assets/                 # 资源文件
│   ├── components/             # 公共组件
│   ├── config/                 # 配置文件
│   ├── router/                 # 路由配置
│   ├── store/                  # 状态管理
│   ├── style/                  # 样式文件
│   ├── utils/                  # 工具函数
│   ├── views/                  # 页面
│   │   ├── home/               # 首页
│   │   ├── layout/             # 布局页
│   │   ├── list/               # 列表页
│   │   ├── login/              # 登录页
│   │   ├── register/           # 注册页
│   │   ├── center/             # 个人中心
│   │   ├── forgetPassword/     # 忘记密码页
│   │   └── updatePassword/     # 密码修改
│   ├── App.vue                 # 入口组件
│   └── main.js                 # 入口逻辑
├── index.html                  # 入口 HTML 文件
├── jsconfig.json               # JavaScript 配置
├── package.json                # 项目依赖配置
├── README.md                   # 项目说明文档
└── vite.config.js              # Vite 构建配置
```