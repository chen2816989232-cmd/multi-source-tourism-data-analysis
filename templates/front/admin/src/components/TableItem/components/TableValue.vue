<script setup>
import { computed } from 'vue'

defineOptions({
  inheritAttrs: false,
})

const { value, column } = defineProps(['value', 'column', 'row'])

const text = computed(() => {
  if (value === null || value === undefined || value === '') {
    return '暂无'
  }

  if (column?.columnName === 'jiage') {
    const price = Number(value)
    if (!Number.isNaN(price)) {
      if (price === 0) {
        return '免费'
      }
      return Number.isInteger(price) ? String(price) : price.toFixed(2).replace(/0+$/, '').replace(/\.$/, '')
    }
  }

  return value
})
</script>

<template>
  <span :class="{ 'table-empty-value': text === '暂无' }">{{ text }}</span>
</template>

<style scoped>
.table-empty-value {
  color: #98a2b3;
}
</style>
