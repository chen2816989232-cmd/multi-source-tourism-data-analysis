<script setup>
/**
 * @description 系统简介
 * title 标题
 * subtitle 副标题
 * picture1 图1
 * picture2 图2
 * picture3 图4
 * content 内容
 */
import { inject } from 'vue'
let { data } = defineProps(['data'])
let { systemIntroduceData } = inject('start')
</script>

<template>
  <div class="introduction-default">
    <div class="inner">
      <div class="header">
        <span class="title">{{ data.title }}</span>
        <span class="subtitle">{{ data.subtitle }}</span>
      </div>
      <div class="content">
        <div class="img-box">
          <img class="img1" :src="data.picture1" draggable="false" />
          <img class="img2" :src="data.picture2" draggable="false" />
          <img class="img3" :src="data.picture3" draggable="false" />
        </div>
        <div class="desc">
          <div class="ql-snow ql-editor" v-html="data.content"></div>
        </div>
      </div>
    </div>
  </div>
</template>
<style>
.introduction-default {
  .header {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    flex-direction: column;
    &::before {
      content: '';
      width: 100%;
      height: 22px;
      background: url(http://codegen.caihongy.cn/20250926/dc4e0caa1a6b40979ba5998b2310daa9.png);
      position: absolute;
      bottom: 0;
    }
    .title {
      font-size: 28px;
      color: var(--btn-bg-color-);
      padding: 0 50px;
      margin: 0 0 10px;

      z-index: 3;
      font-weight: 600;
    }
    .subtitle {
      font-size: 18px;
      color: #ccc;
      padding: 0 20px;
      margin: 0;
      z-index: 2;
    }
  }
  .content {
    width: 100%;
    height: auto;
    padding: 20px 0;
    margin: 0;
    display: flex;
    flex-wrap: wrap;
  }
  .img-box {
    width: 50%;
    padding: 0 20px 0 0;
    margin: 0;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 20px;
    height: 300px;
    .img1,
    .img2,
    .img3 {
      flex: auto;
      width: 0;
      height: 100%;
      padding: 0;
      margin: 0;
      object-fit: cover;
    }
  }
  .desc {
    width: 50%;
    padding: 0px;
    margin: 0;
    border: 0px solid #150572;
    color: #787878;
    font-size: inherit;
    line-height: 24px;
  }
}
</style>

