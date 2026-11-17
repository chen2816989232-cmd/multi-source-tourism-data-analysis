
/**
 * @description UI组件(View.vue后缀文件)的数据获取
 */

import { getFirstFilePath } from './getFilePath'

function formatDisplayValue(value) {
  if (value === null || value === undefined || value === '') {
    return '\u6682\u65e0'
  }
  return value
}

function formatOptionalValue(value) {
  if (value === undefined) {
    return undefined
  }
  return formatDisplayValue(value)
}

export default function getUiList(config, list) {

  return getUi(config, list)
}

function getUi(config, list) {
  // 字段配置项
  let { hasIsanon, imgName, pubPeopleName, titleNames, titleHeads } = config

  let uiList = list.map(item => {
    return {
      id: item.id,
      img: getFirstFilePath(item[imgName]),
      user: hasIsanon && item.isanon == 1 ? '匿名' : formatOptionalValue(item[pubPeopleName]),
      titles: titleNames.map((name, index) => {
        const value = formatDisplayValue(item[name])
        if (titleHeads[index]) {
          return titleHeads[index] + ': ' + value
        }
        return value
      }),
      introduction: formatOptionalValue(item.introduction),
      price: formatOptionalValue(item.price),
      addtime: item.addtime,
      thumbsupnum: formatOptionalValue(item.thumbsupnum),
      storeupnum: formatOptionalValue(item.storeupnum),
      clicknum: formatOptionalValue(item.clicknum),
      browseduration: formatOptionalValue(item.browseduration),
      sourceData: item,
    }
  })

  return uiList
}

