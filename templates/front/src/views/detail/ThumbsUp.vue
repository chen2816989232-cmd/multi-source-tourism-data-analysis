<script setup>
/**
 * @description 赞、踩、取消赞、取消踩
 *
 * thumbsUpId 是否已经点赞
 * crazilyId 是否已经点踩
 * data 详情数据
 *
 * thumbsUpEvent 点赞事件(21) 点踩事件(22)
 * thumbsDownEvent 取消点赞事件(21) 取消点踩事件(22)
 */
import { inject } from 'vue'

let { thumbsUpId, crazilyId, data, thumbsUpEvent, thumbsDownEvent } = inject('detail')
</script>

<template>
  <div class="thumbsup-view">
    <div class="like" v-if="!thumbsUpId && !crazilyId" @click="thumbsUpEvent(21)">
      <span>赞一下</span>
      <span>({{ data.thumbsupnum }})</span>
    </div>
    <div class="unlike" v-if="!thumbsUpId && !crazilyId" @click="thumbsUpEvent(22)">
      <span>踩一下</span>
      <span>({{ data.crazilynum }})</span>
    </div>

    <div class="like act" v-if="thumbsUpId" @click="thumbsDownEvent(21)">
      <span>取消赞</span>
      <span>({{ data.thumbsupnum }})</span>
    </div>

    <div class="unlike act" v-if="crazilyId" @click="thumbsDownEvent(22)">
      <span>取消踩</span>
      <span>({{ data.crazilynum }})</span>
    </div>
  </div>
</template>
<style>
.thumbsup-view {
  padding-top: 20px;
  display: flex;
  justify-content: space-evenly;

  .like {
    width: 30%;
    height: 44px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    color: var(--btn-font-color-);
    background: var(--btn-bg-color-);
    border-radius: 8px;
    font-size: 14px;

    &:hover {
      color: var(--btn-font-hover-color-);
      background: var(--btn-bg-hover-color-);
    }
  }
  .unlike {
    width: 30%;
    height: 44px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    color: var(--btn2-font-color-);
    background: var(--btn2-bg-color-);
    border-radius: 8px;
    font-size: 14px;

    &:hover {
      color: var(--btn2-font-hover-color-);
      background: var(--btn2-bg-hover-color-);
    }
  }
}
</style>

