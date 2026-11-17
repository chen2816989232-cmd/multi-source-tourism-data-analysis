<script setup>
/**
 * @description 个人中心
 */
import '@/style/center.scss'

// 注册表单组件
import '@/components/FormItem/index.js'
import { reactive, ref, computed, provide, shallowRef } from 'vue'

import CenterTitle from './CenterTitle.vue'
import Custom from './Custom.vue'
import Info from './Info.vue'
import Menus from './Menus.vue'
import Tabs from './Tabs.vue'
import CenterEdit from './CenterEdit.vue'
import UpdatePassword from './updatePassword.vue'

import MyDiscuss from '@/components/MyDiscuss.vue'
import MyStoreup from '@/components/MyStoreup.vue'

import tableConfigs from '@/utils/tableConfigs'
import { useUserInfo } from '@/store'
import { useRouter } from 'vue-router'
import { toListPage } from '@/utils/navigate'
import { isAuth } from '@/utils/auth'
import { getPageAPI, getListAPI } from '@/api/list'
import { getChatHistoryAPI } from '@/api/common'
import { getSessionAPI } from '@/api/login'

let router = useRouter()
// 检查用户是否登录
const userInfoStore = useUserInfo()
// if (!userInfoStore.userInfo.isLogin) {
//   router.push('/login')
// }

let tableName = localStorage.getItem('sessionTable')
let tableConfig = tableConfigs[tableName]
let { table, columns } = tableConfig

const title = '个人中心'
const userAvatar = computed(() => userInfoStore.userInfo.avatar)
// ----------------------------------
// ---------- 个人信息 ----------------
// ----------------------------------
const infoList = ref([])
infoEvent()
async function infoEvent() {
  let excludeColumnTypes = ['图', '音', '视', '文', '编'] // 媒体类型不显示
  let excludeColumnNames = [
    'passwordwrongnum',
    'mima',
    'password',
    'status',
    'money',
    'pquestion',
    'panswer',
    'sfsh',
    'shhf',
    'clicktime',
    'browseduration',
    'thumbsupnum',
    'crazilynum',
    'clicknum',
    'storeupnum',
    'discussnum',
  ] // 排除的字段名
  let centerColumns = columns
    .filter(
      item =>
        !excludeColumnTypes.includes(item.type) && !excludeColumnNames.includes(item.columnName)
    )
    .slice(0, 6) // 只显示前6个字段
  // 更新个人信息
  let { data: userForm } = await getSessionAPI(tableName)
  localStorage.setItem('userForm', JSON.stringify(userForm))

  let list = []
  centerColumns.forEach(column => {
    list.push({
      label: column.comments,
      value: userForm[column.columnName] || '',
    })
  })
  infoList.value = list
}

// ----------------------------------
// ---------- 标签页 ----------------
// ----------------------------------
const tabs = shallowRef(getTabs())
function getTabs() {
  let list = [
    {
      label: '个人中心',
      name: CenterEdit,
    },
    {
      label: '修改密码',
      name: UpdatePassword,
    },
    {
      label: '我的收藏',
      name: MyStoreup,
      type: '1'
    },
    {
      label: '我的点赞',
      name: MyStoreup,
      type: '21'
    },
  ]

  let roleMenu = JSON.parse(localStorage.getItem('roleMenu'))
  let hasMyDiscuss = roleMenu.some(item => {
    if (item.menuJump == '81') {
      return true
    }
    if (item.child) {
      return item.child.some(i => i.menuJump == '81')
    }
    return false
  })
  if (hasMyDiscuss) {
    list.push({
      label: '我的评论',
      name: MyDiscuss,
    })
  }    

  return list
}

function tabEvent(tab, event) {}

// ----------------------------------
// ---------- 菜单 ----------------
// ----------------------------------
const menuList = ref(getMenuList())
function getMenuList() {
  let list = [
  ]


  const filterTableNames = [
    'storeup',
    'systemintro',
    'aboutus',
    'menu',  
  ]
  let roleMenu = JSON.parse(localStorage.getItem('roleMenu'))
  // 展开所有菜单
  roleMenu.forEach(item => {
    getMenuItem(item)
    
    if (item.child) {
      item.child.forEach(child => {
        getMenuItem(child)
      })
    }
  })

  function getMenuItem(item) {
    let { menu, tableName } = item
    // 过滤菜单
    if (!tableName) {
      return
    }

    if (tableName.startsWith('stat/')) {
      return
    }

    if (filterTableNames.includes(tableName)) {
      return
    }

    // 确定路径
    let path = '/index/' + tableName
    if (tableName == 'hasBoard') {
      path = '/board'
    }
    list.push({
      label: menu,
      tableName: tableName,
      path,
      query: { centerType: 1 },
    })
  }

  return list
}

function menuEvent(item) {
  router.push({ path: item.path, query: item.query })
}


provide('center', {
  infoList,
  userAvatar,

  tabs,
  tabEvent,

  menuList,
  menuEvent,

  infoEvent,
})
</script>

<template>
  <div class="center-page">
    
    <CenterTitle :title="title" />
    <Info />
    <Tabs />
    <Menus />
    <Custom />
  
  </div>
</template>
