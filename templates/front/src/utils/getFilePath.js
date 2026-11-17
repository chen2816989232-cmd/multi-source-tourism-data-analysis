/**
 * @description 获取文件（图片、音频、视频）的完整路径地址
 * 本项目地址：upload/test.png  --> 转换为 baseUrl + upload/test.png
 */

import base from '@/utils/base'
const projectBase = base.get()
let baseUrl = projectBase.url
let schemaBaseUrl = `/${projectBase.name}/`

/**
 * @description 解析文件路径
 * @param { string } fileStr upload/upian2.jpg 经过split(',')[0]处理
 * @returns
 */
export function getFilePath(fileStr) {
  if (!fileStr) {
    return ''
  }
  let isNet = /^(https?:)?\/\//.test(fileStr) || /^data:/.test(fileStr)
  if (isNet) {
    return fileStr
  }

  let cleanPath = fileStr.replace(/^\/+/, '')
  if (cleanPath.startsWith(projectBase.name + '/')) {
    return '/' + cleanPath
  }
  return schemaBaseUrl + cleanPath
}

/**
 * @description 解析第一个文件路径
 * @param { string } fileStrs  upload/upian2.jpg,upload/upian3.jpg 未经过split(',')[0]处理
 * @returns
 */
export function getFirstFilePath(fileStrs) {
  if (!fileStrs) {
    return ''
  }
  let firstStr = fileStrs.split(/,(?=upload)/)[0]
  return getFilePath(firstStr)
}

/**
 * @description 根据字符串，解析所有文件路径
 * @param { string } fileStr
 * @returns
 */
export function getFilePaths(fileStrs) {
  if (!fileStrs) {
    return []
  }
  let list = fileStrs.split(/,(?=upload)/)
  return list.map(fileStr => getFilePath(fileStr))
}

/**
 * @description 把添加的baseUrl和inlinePreUrl去除掉
 * @param {string} fileStr
 * @returns
 */
export function clearFilePath(fileStr) {
  if (!fileStr) {
    return ''
  }
  return fileStr.replace(baseUrl, '').replace(schemaBaseUrl, '')
}

export default getFilePath
