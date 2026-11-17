<script setup>
/**
 * @description 首页
 */
import '@/style/home.scss';
import { onMounted, ref, provide } from 'vue'

import HomeChart from './HomeChart.vue'
import HomeCount from './HomeCount.vue'
import HomeTitle from './HomeTitle.vue'
import HomeNews from './HomeNews.vue'
import Custom from './Custom.vue'

import chartData from '@/components/Echart/chartData'
import { isAuth } from '@/utils/auth';
import { getCountAPI, getPageAPI } from '@/api/list'
import { getFirstFilePath } from '@/utils/getFilePath'

// ----------------------------------
// ----------- 总数统计 --------------
// ----------------------------------
let initCountList = [
  {
    tableName: 'ctripjd',
    comments: '景点查询',
    count: 0,
  },
  {
    tableName: 'ctrippinglun',
    comments: '景点评论',
    count: 0,
  },
  {
    tableName: 'yonghu',
    comments: '用户',
    count: 0,
  },
  {
    tableName: 'qingganfenxi',
    comments: '情感分析',
    count: 0,
  },
]
// 当前角色的总数统计 (鉴权)
initCountList = initCountList.filter(item => isAuth(item.tableName, '首页总数'))
const roleCountList = ref(initCountList)
getCountDatas()
function getCountDatas() {
  roleCountList.value.forEach(async item => {
    let res = await getCountAPI(item.tableName)
    item.count = res.data
  })
}

// ----------------------------------
// ----------- 首页图表 --------------
// ----------------------------------
// 当前角色的首页统计 (鉴权)
const roleChartList = chartData.filter(item => item.showHome).filter(item => isAuth(item.tableName, '首页统计'))

// ----------------------------------
// ----------- 新闻资讯 --------------
// ----------------------------------
const newsData = ref({
  title: '系统公告',
  list: [],
})
getNews()
async function getNews() {
  let res = await getPageAPI('news', {
    page: 1,
    limit: 6,
  })
  res.data.list.forEach(item => {
    item.img = getFirstFilePath(item.picture)
  })
  newsData.value.list = res.data.list
}

onMounted(() => {
  setTimeout(() => {
    requestIdleCallback(() => {
      // 提前加载 列表页
      import("@/views/list/list.vue");
    });
  }, 1000);
});

provide('home', {
  roleCountList,
  roleChartList,
  newsData,
})
</script>

<template>
  <div
    class="home-wrapper"
    :style="
      $projectImages.bIndexBackgroundImg
        ? `background-image: url(${$projectImages.bIndexBackgroundImg})`
        : ''
    "
  >
    <HomeCount />  
<HomeChart />  
<HomeNews />
<Custom />  

  
  </div>
</template>
