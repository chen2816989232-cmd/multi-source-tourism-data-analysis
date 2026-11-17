<script setup>
/**
 * @description 首页
 */
import '@/style/start.scss'

import { onMounted, onUnmounted, ref, reactive, provide } from 'vue'

import AboutUs from './AboutUs.vue'
import Custom from './Custom.vue'
import FriendLink from './FriendLink.vue'
import List from './List.vue'
import OnlineMessage from './OnlineMessage.vue'
import Recommend from './Recommend.vue'
import SystemIntroduce from './SystemIntroduce.vue'
import News from './News.vue'

import { getDetailAPI, addAPI, getListAPI } from '@/api/list'
import { getFirstFilePath } from '@/utils/getFilePath'
import { toDetailPage, toListPage } from '@/utils/navigate'
import { getAutoSort1API, getAutoSort2API } from '@/api/front'
import getUiList from '@/utils/getUiList'
// ----------------------------------
// ------------ 列表 ----------------
// ----------------------------------
const listList = ref([
])
// 更新listList.list字段数据
getListList()
function getListList() {
  listList.value.forEach(async item => {
    // [1] 查询api参数
    let apiParams = {
      limit: 4,
    }
    // 参数: 排序
    if (item.sortName) {
      apiParams.sort = item.sortName
      apiParams.order = item.sortOrder
    }

    // 参数: 审核
    if (item.sfsh == '是') {
      apiParams.sfsh = '是'
    }

    if (item.hasOnshelves) {
      apiParams.onshelves = 1
    }
    
    let res = await getListAPI(item.tableName, apiParams)
    item.list = getUiList(item, res.data.list)
  })
}

// ----------------------------------
// ------------ 推荐 ----------------
// ----------------------------------
const recommendList = ref([
  {
    tableName: 'ctripjd',
    comments: '景点查询 推荐',
    subtitle: 'ctripjd Recommend',
    sfsh: '否',
    isIntelRecom: true,
    titleNames: ['poiname','commentscore','heatscore','districtname'],
    titleHeads: ['','评分','热度',''],
    imgName: 'imgurl',
    pubPeopleName: '',
    sortName: '',
    sortOrder: 'desc',
    hasOnshelves: false,
    list: [],
  },
])
recommendList.value = []
function getRecommendList() {
  recommendList.value.forEach(async item => {
    // [1] 查询api参数
    let apiParams = {
      limit: 4,
    }
    // 参数: 排序
    if (item.sortName) {
      apiParams.sort = item.sortName
      apiParams.order = item.sortOrder
    }

    // 参数: 审核
    if (item.sfsh == '是') {
      apiParams.sfsh = '是'
    }

    if (item.hasOnshelves) {
      apiParams.onshelves = 1
    }

    // 智能推荐2 【推荐】 需要登录，如果没有登录，降级使用autoSort 接口（前台）
    let res
    if (item.isIntelRecom && localStorage.getItem('Token')) {
      try {
        res = await getAutoSort2API(item.tableName, apiParams)
      } catch (error) {
      }
    }
    if(!res || res.code !== 0){
      res = await getAutoSort1API(item.tableName, apiParams)
    }

    item.list = getUiList(item, res.data.list)
  })
}

const newsData = ref({})
// ----------------------------------
// ------------ 新闻 ----------------
// ----------------------------------
newsData.value = {
  tableName: 'news',
  comments: '系统公告',
  sfsh: '否',
  subtitle: 'news',
  titleNames: ['title'],
  titleHeads: [''],
  imgName: 'picture',
  pubPeopleName: '',
  sortName: '',
  sortOrder: 'desc',
  list: [],
}
getNewsList()
async function getNewsList() {
  // [1] 查询api参数
  let apiParams = {
    limit: 6,
  }
  // 参数: 排序
  if (newsData.value.sortName) {
    apiParams.sort = newsData.value.sortName
    apiParams.order = newsData.value.sortOrder
  }

  // 参数: 审核
  if (newsData.value.sfsh == '是') {
    apiParams.sfsh = '是'
  }

  let res = await getListAPI(newsData.value.tableName, apiParams)
  newsData.value.list = getUiList(newsData.value, res.data.list)
}

let aboutUsData = ref({})

let systemIntroduceData = ref({})
// ----------------------------------
// ---------- 系统简介 ---------------
// ----------------------------------
getintroductionData()
async function getintroductionData() {
  let { data } = await getDetailAPI('systemintro', '1')
  data.picture1 = getFirstFilePath(data.picture1)
  data.picture2 = getFirstFilePath(data.picture2)
  data.picture3 = getFirstFilePath(data.picture3)
  systemIntroduceData.value = data
}



onMounted(() => {
  setTimeout(() => {
    requestIdleCallback(() => {
      // 提前加载 列表页
      import('@/views/list/list.vue')
      import('@/views/detail/detail.vue')
    })
  }, 1000)
})

provide('start', {
  aboutUsData,
  systemIntroduceData,



  listList,
  recommendList,
  newsData,
  detailEvent: toDetailPage,
  moreEvent: toListPage,
})
</script>

<template>
  <div class="home-page">
    
<AboutUs :data="aboutUsData" />
<SystemIntroduce :data="systemIntroduceData" />
<List v-for="item in listList" :key="item.tableName" :data="item" />
<Recommend v-for="item in recommendList" :key="item.tableName" :data="item" />
<News :data="newsData" />
<OnlineMessage />
<FriendLink />
<Custom />
  
  </div>
</template>
