# 4.4.2 数据库表结构设计（修改稿）

本系统数据库表结构按照项目实际运行情况进行整理。表结构说明中将“是否为空”和“默认值”分开描述，其中“是否为空”表示字段是否允许存储 NULL 值，“默认值”表示插入数据时未传入该字段时数据库自动写入的值。

主键自增字段的默认值统一写为 AUTO_INCREMENT；创建时间字段默认值写为 CURRENT_TIMESTAMP；允许为空且没有固定默认值的字段写为 NULL；不允许为空且没有设置默认值的字段写为“—”。

## 表4-1 T_Administrator

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| username | varchar | 200 | 否 | — | 用户名 |
| password | varchar | 200 | 否 | — | 密码 |
| role | varchar | 200 | 是 | 管理员 | 角色 |
| image | longtext | — | 是 | NULL | 头像 |

## 表4-2 T_Attraction_Reviews

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| content | longtext | — | 是 | NULL | 评论内容 |
| images | longtext | — | 是 | NULL | 评论首图 |
| usernick | varchar | 200 | 是 | NULL | 评论人 |
| ipadd | varchar | 200 | 是 | NULL | ip地址 |
| dptime | varchar | 200 | 是 | NULL | 点评时间 |
| scoresjs | int | 11 | 是 | NULL | 景色 |
| scoresqw | int | 11 | 是 | NULL | 趣味 |
| scoresxjb | varchar | 200 | 是 | NULL | 性价比 |
| plurl | varchar | 200 | 是 | NULL | 评论地址 |

## 表4-3 T_Comprehensive_data

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| tongjiriqi | date | — | 是 | NULL | 统计日期 |
| jingdianmingcheng | varchar | 200 | 是 | NULL | 景点名称 |
| jingdianleixing | varchar | 200 | 是 | NULL | 景点类型 |
| suoshuchengshi | varchar | 200 | 是 | NULL | 所属城市 |
| jingdianredu | int | 11 | 是 | NULL | 景点热度 |
| menpiaojiage | int | 11 | 是 | NULL | 门票价格 |
| dangritianqi | varchar | 200 | 是 | NULL | 当日天气 |
| rijunqiwen | int | 11 | 是 | NULL | 日均气温 |
| fenglidengji | int | 11 | 是 | NULL | 风力等级 |
| jiaotongbianjiedupingfen | int | 11 | 是 | NULL | 交通便捷度评分 |
| zhoubiantingchechangshuliang | int | 11 | 是 | NULL | 周边停车场数量 |
| fujingongjiaozhandianshu | int | 11 | 是 | NULL | 附近公交站点数 |
| ditiexianlukedaxing | varchar | 200 | 是 | NULL | 地铁线路可达性 |
| shifoujiejiari | varchar | 200 | 是 | NULL | 是否节假日 |
| jiejiarileixing | varchar | 200 | 是 | NULL | 节假日类型 |
| rijunyoukejiedailiang | int | 11 | 是 | NULL | 日均游客接待量 |
| youkehaopinglv | int | 11 | 是 | NULL | 游客好评率 |
| zhoubianjiudianshuliang | int | 11 | 是 | NULL | 周边酒店数量 |

## 表4-4 T_Core_attractions

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| poiname | varchar | 200 | 是 | NULL | 景点名称 |
| imgurl | longtext | — | 是 | NULL | 图片 |
| commentscore | double | — | 是 | NULL | 评分 |
| commentcount | int | 11 | 是 | NULL | 评论数 |
| heatscore | double | — | 是 | NULL | 热度 |
| jiage | double | — | 是 | NULL | 价格 |
| districtname | varchar | 200 | 是 | NULL | 地区 |
| zonename | varchar | 200 | 是 | NULL | 地址 |
| sightcategoryinfo | varchar | 200 | 是 | NULL | 口碑榜 |
| tagname | varchar | 200 | 是 | NULL | 标签 |
| shortfeatures | varchar | 200 | 是 | NULL | 简介 |
| distancestr | varchar | 200 | 是 | NULL | 位置 |
| othertaglist | varchar | 200 | 是 | NULL | 其他标签 |
| detailurl | longtext | — | 是 | NULL | 详情地址 |
| thumbsupnum | int | 11 | 是 | 0 | 赞 |
| crazilynum | int | 11 | 是 | 0 | 踩 |
| clicktime | datetime | — | 是 | NULL | 最近点击时间 |
| clicknum | int | 11 | 是 | 0 | 点击次数 |
| discussnum | int | 11 | 是 | 0 | 评论数 |
| storeupnum | int | 11 | 是 | 0 | 收藏数 |
| source_platform | varchar | 100 | 是 | ctrip | 来源平台 |
| source_id | varchar | 255 | 是 | NULL | 来源编号 |
| source_url | text | — | 是 | NULL | 来源地址 |
| standard_name | varchar | 255 | 是 | NULL | 标准化名称 |
| source_count | int | 11 | 是 | 1 | 来源数量 |
| longitude | varchar | 50 | 是 | NULL | 经度 |
| latitude | varchar | 50 | 是 | NULL | 纬度 |
| raw_json | longtext | — | 是 | NULL | 原始JSON |
| data_status | varchar | 50 | 是 | normal | 数据状态 |

## 表4-5 T_Raw_Platform_City_Collect_Log

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| source_platform | varchar | 50 | 否 | — | 来源平台 |
| keyword | varchar | 100 | 否 | — | 采集关键词 |
| city | varchar | 255 | 否 | — | 采集城市 |
| fetched | int | 11 | 是 | 0 | 采集数量 |
| status | varchar | 50 | 是 | success | 采集状态 |
| message | text | — | 是 | NULL | 采集信息 |
| crawl_time | datetime | — | 是 | CURRENT_TIMESTAMP | 采集时间 |

## 表4-6 T_Raw_Platform_Spot

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | — | 主键 |
| source_platform | varchar | 50 | 否 | — | 来源平台 |
| source_id | varchar | 255 | 是 | NULL | 来源编号 |
| source_url | text | — | 是 | NULL | 来源地址 |
| poiname | varchar | 255 | 是 | NULL |  |
| standard_name | varchar | 255 | 是 | NULL | 标准化名称 |
| districtname | varchar | 255 | 是 | NULL |  |
| address | varchar | 255 | 是 | NULL | 地址 |
| longitude | varchar | 50 | 是 | NULL | 经度 |
| latitude | varchar | 50 | 是 | NULL | 纬度 |
| commentscore | double | — | 是 | NULL |  |
| commentcount | int | 11 | 是 | NULL |  |
| heatscore | double | — | 是 | NULL |  |
| jiage | double | — | 是 | NULL |  |
| crawl_time | datetime | — | 是 | NULL | 采集时间 |
| raw_json | longtext | — | 是 | NULL | 原始JSON |
| data_status | varchar | 50 | 是 | normal | 数据状态 |

## 表4-7 T_RegionRating_Prediction

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| poiname | varchar | 200 | 是 | NULL | 景点名称 |
| commentscore | double | — | 是 | NULL | 评分 |
| heatscore | double | — | 是 | NULL | 热度 |
| districtname | varchar | 200 | 是 | NULL | 地区 |

## 表4-8 T_Sentiment_Analysis

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| poiname | varchar | 255 | 是 | NULL | 景点名称 |
| reviewid | bigint | 20 | 是 | NULL | 评论编号 |
| usernick | varchar | 200 | 是 | NULL | 评论人 |
| content | longtext | — | 是 | NULL | 评论内容 |
| dptime | varchar | 200 | 是 | NULL | 点评时间 |
| fenxijieguo | varchar | 200 | 是 | NULL | 分析结果 |

## 表4-9 T_SMS_Verification_Code

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| mobile | varchar | 200 | 否 | — | 手机 |
| role | varchar | 200 | 否 | — | 角色 |
| code | varchar | 200 | 否 | — | 验证码 |

## 表4-10 T_System_Config

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| name | varchar | 100 | 否 | — | 配置参数名称 |
| value | varchar | 200 | 是 | NULL | 配置参数值 |
| url | varchar | 500 | 是 | NULL | url |
| type | int | 11 | 是 | NULL | 参数类型 |

## 表4-11 T_System_Introduction

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| title | varchar | 200 | 否 | — | 标题 |
| subtitle | varchar | 200 | 是 | NULL | 副标题 |
| content | longtext | — | 否 | — | 内容 |
| picture1 | longtext | — | 是 | NULL | 图片1 |
| picture2 | longtext | — | 是 | NULL | 图片2 |
| picture3 | longtext | — | 是 | NULL | 图片3 |

## 表4-12 T_System_News

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| title | varchar | 64 | 否 | — | 标题 |
| introduction | longtext | — | 是 | NULL | 简介 |
| picture | longtext | — | 否 | — | 图片 |
| content | longtext | — | 否 | — | 内容 |
| name | varchar | 16 | 是 | NULL | 发布人 |
| headportrait | longtext | — | 是 | NULL | 头像 |

## 表4-13 T_temporary_attractions

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | 0 | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| poiname | varchar | 200 | 是 | NULL | 景点名称 |
| imgurl | varchar | 200 | 是 | NULL | 图片 |
| commentscore | varchar | 200 | 是 | NULL | 评分 |
| commentcount | int | 11 | 是 | NULL | 评论数 |
| heatscore | double | — | 是 | NULL | 热度 |
| jiage | double | — | 是 | NULL | 价格 |
| districtname | varchar | 200 | 是 | NULL | 地区 |
| zonename | varchar | 200 | 是 | NULL | 地址 |
| sightcategoryinfo | varchar | 200 | 是 | NULL | 口碑榜 |
| tagname | varchar | 200 | 是 | NULL | 标签 |
| shortfeatures | varchar | 200 | 是 | NULL | 简介 |
| distancestr | varchar | 200 | 是 | NULL | 位置 |
| othertaglist | varchar | 200 | 是 | NULL | 其他标签 |
| detailurl | longtext | — | 是 | NULL | 详情地址 |

## 表4-14 T_temporary_comment_data

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | 0 | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| content | longtext | — | 是 | NULL | 评论内容 |
| images | longtext | — | 是 | NULL | 评论首图 |
| usernick | varchar | 200 | 是 | NULL | 评论人 |
| ipadd | varchar | 200 | 是 | NULL | ip地址 |
| dptime | varchar | 200 | 是 | NULL | 点评时间 |
| scoresjs | int | 11 | 是 | NULL | 景色 |
| scoresqw | int | 11 | 是 | NULL | 趣味 |
| scoresxjb | varchar | 200 | 是 | NULL | 性价比 |
| plurl | varchar | 200 | 是 | NULL | 评论地址 |

## 表4-15 T_tourist_Attraction_discuss

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| refid | bigint | 20 | 否 | — | 关联表id |
| userid | bigint | 20 | 否 | — | 用户id |
| avatarurl | longtext | — | 是 | NULL | 头像 |
| nickname | varchar | 200 | 是 | NULL | 用户名 |
| content | longtext | — | 否 | — | 评论内容 |
| reply | longtext | — | 是 | NULL | 回复内容 |
| thumbsupnum | int | 11 | 是 | 0 | 赞 |
| crazilynum | int | 11 | 是 | 0 | 踩 |
| istop | int | 11 | 是 | 0 | 置顶 |
| tuserids | longtext | — | 是 | NULL | 赞用户ids |
| cuserids | longtext | — | 是 | NULL | 踩用户ids |

## 表4-16 T_tourist_Attraction_Popularity_Forecast

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| poiname | varchar | 200 | 是 | NULL | 景点名称 |
| districtname | varchar | 200 | 是 | NULL | 地区 |
| commentcount | int | 11 | 是 | NULL | 评论数 |
| heatscore | double | — | 是 | NULL | 热度 |

## 表4-17 T_User_Behavior

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| userid | bigint | 20 | 否 | — | 用户id |
| refid | bigint | 20 | 是 | NULL | 商品id |
| tablename | varchar | 200 | 是 | NULL | 表名 |
| name | varchar | 200 | 否 | — | 名称 |
| picture | longtext | — | 是 | NULL | 图片 |
| type | varchar | 200 | 是 | 1 | 类型 |
| inteltype | varchar | 200 | 是 | NULL | 推荐类型 |
| remark | varchar | 200 | 是 | NULL | 备注 |

## 表4-18 T_users

| 字段名称 | 类型 | 长度 | 是否为空 | 默认值 | 字段说明 |
|---|---|---:|---|---|---|
| id | bigint | 20 | 否 | AUTO_INCREMENT | 主键 |
| addtime | timestamp | — | 否 | CURRENT_TIMESTAMP | 创建时间 |
| yonghuzhanghao | varchar | 16 | 否 | — | 用户账号 |
| yonghuxingming | varchar | 200 | 否 | — | 用户姓名 |
| mima | varchar | 200 | 否 | — | 密码 |
| xingbie | varchar | 200 | 是 | NULL | 性别 |
| touxiang | longtext | — | 是 | NULL | 头像 |
| mobile | varchar | 200 | 是 | NULL | 手机号 |
| status | int | 11 | 是 | 0 | 状态 |
