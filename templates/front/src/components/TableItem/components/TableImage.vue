<script setup>
import { getFilePaths } from '@/utils/getFilePath'
import { computed } from 'vue'

/**
 * @description 图片
 */
defineOptions({
  inheritAttrs: false,
})
const { value } = defineProps(['value'])

let srcList = computed(() => {
  return getFilePaths(value)
})

let hasImage = computed(() => {
  return srcList.value.length > 0 && !!srcList.value[0]
})
</script>

<template>
  <el-image
    v-if="hasImage"
    class="table-image"
    preview-teleported
    :src="srcList[0]"
    :preview-src-list="srcList"
    show-progress
    fit="cover"
  >
    <template #error>
      <div class="table-image-placeholder">暂无图片</div>
    </template>
  </el-image>
  <div v-else class="table-image table-image-placeholder">暂无图片</div>
</template>

<style scoped>
.table-image-placeholder {
  width: 64px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: #f2f4f7;
  color: #98a2b3;
  font-size: 12px;
}
</style>
