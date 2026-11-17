#coding:utf-8
from django.db import models

from .model import BaseModel

from datetime import datetime



class ctripjd(BaseModel):
    __doc__ = u'''ctripjd'''
    __tablename__ = 'ctripjd'



    __authTables__={}
    __authPeople__='否'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='是'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='用协'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='是'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='是'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    poiname=models.CharField ( max_length=255, null=True, unique=False, verbose_name='景点名称' )
    imgurl=models.TextField   (  null=True, unique=False, verbose_name='图片' )
    commentscore=models.FloatField   (  null=True, unique=False, verbose_name='评分' )
    commentcount=models.IntegerField  (  null=True, unique=False, verbose_name='评论数' )
    heatscore=models.FloatField   (  null=True, unique=False, verbose_name='热度' )
    jiage=models.FloatField   (  null=True, unique=False, verbose_name='价格' )
    districtname=models.CharField ( max_length=255, null=True, unique=False, verbose_name='地区' )
    zonename=models.CharField ( max_length=255, null=True, unique=False, verbose_name='地址' )
    sightcategoryinfo=models.CharField ( max_length=255, null=True, unique=False, verbose_name='口碑榜' )
    tagname=models.CharField ( max_length=255, null=True, unique=False, verbose_name='标签' )
    shortfeatures=models.CharField ( max_length=255, null=True, unique=False, verbose_name='简介' )
    distancestr=models.CharField ( max_length=255, null=True, unique=False, verbose_name='位置' )
    othertaglist=models.CharField ( max_length=255, null=True, unique=False, verbose_name='其他标签' )
    detailurl=models.TextField   (  null=True, unique=False, verbose_name='详情地址' )
    thumbsupnum=models.IntegerField  (  null=True, unique=False,default='0', verbose_name='赞' )
    crazilynum=models.IntegerField  (  null=True, unique=False,default='0', verbose_name='踩' )
    clicktime=models.DateTimeField  (auto_now=True,  null=True, unique=False, verbose_name='最近点击时间' )
    clicknum=models.IntegerField  (  null=True, unique=False,default='0', verbose_name='点击次数' )
    discussnum=models.IntegerField  (  null=True, unique=False,default='0', verbose_name='评论数' )
    storeupnum=models.IntegerField  (  null=True, unique=False,default='0', verbose_name='收藏数' )
    '''
    poiname=VARCHAR
    imgurl=Text
    commentscore=Float
    commentcount=Integer
    heatscore=Float
    jiage=Float
    districtname=VARCHAR
    zonename=VARCHAR
    sightcategoryinfo=VARCHAR
    tagname=VARCHAR
    shortfeatures=VARCHAR
    distancestr=VARCHAR
    othertaglist=VARCHAR
    detailurl=Text
    thumbsupnum=Integer
    crazilynum=Integer
    clicktime=DateTime
    clicknum=Integer
    discussnum=Integer
    storeupnum=Integer
    '''
    class Meta:
        db_table = 'T_Core_attractions'
        verbose_name = verbose_name_plural = '携程景点'
class ctrippinglun(BaseModel):
    __doc__ = u'''ctrippinglun'''
    __tablename__ = 'ctrippinglun'



    __authTables__={}
    __authPeople__='否'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='是'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    content=models.TextField   (  null=True, unique=False, verbose_name='评论内容' )
    images=models.TextField   (  null=True, unique=False, verbose_name='评论首图' )
    usernick=models.CharField ( max_length=255, null=True, unique=False, verbose_name='评论人' )
    ipadd=models.CharField ( max_length=255, null=True, unique=False, verbose_name='ip地址' )
    dptime=models.CharField ( max_length=255, null=True, unique=False, verbose_name='点评时间' )
    scoresjs=models.IntegerField  (  null=True, unique=False, verbose_name='景色' )
    scoresqw=models.IntegerField  (  null=True, unique=False, verbose_name='趣味' )
    scoresxjb=models.CharField ( max_length=255, null=True, unique=False, verbose_name='性价比' )
    plurl=models.CharField ( max_length=255, null=True, unique=False, verbose_name='评论地址' )
    '''
    content=Text
    images=Text
    usernick=VARCHAR
    ipadd=VARCHAR
    dptime=VARCHAR
    scoresjs=Integer
    scoresqw=Integer
    scoresxjb=VARCHAR
    plurl=VARCHAR
    '''
    class Meta:
        db_table = 'T_Attraction_Reviews'
        verbose_name = verbose_name_plural = '景点评论'
class yonghu(BaseModel):
    __doc__ = u'''yonghu'''
    __tablename__ = 'yonghu'

    __loginUser__='yonghuzhanghao'


    __authTables__={}
    __authPeople__='是'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __loginUserColumn__='yonghuzhanghao'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='否'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    yonghuzhanghao=models.CharField ( max_length=255,null=False,unique=True, verbose_name='用户账号' )
    yonghuxingming=models.CharField ( max_length=255,null=False, unique=False, verbose_name='用户姓名' )
    mima=models.CharField ( max_length=255,null=False, unique=False, verbose_name='密码' )
    xingbie=models.CharField ( max_length=255, null=True, unique=False, verbose_name='性别' )
    touxiang=models.TextField   (  null=True, unique=False, verbose_name='头像' )
    mobile=models.CharField ( max_length=255, null=True, unique=False, verbose_name='手机号' )
    status=models.IntegerField  (  null=True, unique=False,default='0', verbose_name='状态' )
    '''
    yonghuzhanghao=VARCHAR
    yonghuxingming=VARCHAR
    mima=VARCHAR
    xingbie=VARCHAR
    touxiang=Text
    mobile=VARCHAR
    status=Integer
    '''
    class Meta:
        db_table = 'T_users'
        verbose_name = verbose_name_plural = '用户'
class ctripjdforecast(BaseModel):
    __doc__ = u'''ctripjdforecast'''
    __tablename__ = 'ctripjdforecast'



    __authTables__={}
    __authPeople__='否'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='否'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    poiname=models.CharField ( max_length=255, null=True, unique=False, verbose_name='景点名称' )
    districtname=models.CharField ( max_length=255, null=True, unique=False, verbose_name='地区' )
    commentcount=models.IntegerField  (  null=True, unique=False, verbose_name='评论数' )
    heatscore=models.FloatField   (  null=True, unique=False, verbose_name='热度' )
    '''
    poiname=VARCHAR
    districtname=VARCHAR
    commentcount=Integer
    heatscore=Float
    '''
    class Meta:
        db_table = 'T_tourist_Attraction_Popularity_Forecast'
        verbose_name = verbose_name_plural = '景点热度预测'
class ctripjdforecast1(BaseModel):
    __doc__ = u'''ctripjdforecast1'''
    __tablename__ = 'ctripjdforecast1'



    __authTables__={}
    __authPeople__='否'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='否'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    poiname=models.CharField ( max_length=255, null=True, unique=False, verbose_name='景点名称' )
    commentscore=models.FloatField   (  null=True, unique=False, verbose_name='评分' )
    heatscore=models.FloatField   (  null=True, unique=False, verbose_name='热度' )
    districtname=models.CharField ( max_length=255, null=True, unique=False, verbose_name='地区' )
    '''
    poiname=VARCHAR
    commentscore=Float
    heatscore=Float
    districtname=VARCHAR
    '''
    class Meta:
        db_table = 'T_RegionRating_Prediction'
        verbose_name = verbose_name_plural = '地区预测'
class qingganfenxi(BaseModel):
    __doc__ = u'''qingganfenxi'''
    __tablename__ = 'qingganfenxi'
    poiname=models.CharField ( max_length=255, null=True, unique=False, verbose_name='景点名称' )
    reviewid=models.BigIntegerField  (  null=True, unique=False, verbose_name='评论编号' )



    __authTables__={}
    __authPeople__='否'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='是'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    usernick=models.CharField ( max_length=255, null=True, unique=False, verbose_name='评论人' )
    content=models.TextField   (  null=True, unique=False, verbose_name='评论内容' )
    dptime=models.CharField ( max_length=255, null=True, unique=False, verbose_name='点评时间' )
    fenxijieguo=models.CharField ( max_length=255, null=True, unique=False, verbose_name='分析结果' )
    '''
    reviewid=BigInteger
    usernick=VARCHAR
    content=Text
    dptime=VARCHAR
    fenxijieguo=VARCHAR
    '''
    class Meta:
        db_table = 'T_Sentiment_Analysis'
        verbose_name = verbose_name_plural = '情感分析'
class lvyoushuju(BaseModel):
    __doc__ = u'''lvyoushuju'''
    __tablename__ = 'lvyoushuju'



    __authTables__={}
    __authPeople__='否'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='是'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    tongjiriqi=models.DateField   (  null=True, unique=False, verbose_name='统计日期' )
    jingdianmingcheng=models.CharField ( max_length=255, null=True, unique=False, verbose_name='景点名称' )
    jingdianleixing=models.CharField ( max_length=255, null=True, unique=False, verbose_name='景点类型' )
    suoshuchengshi=models.CharField ( max_length=255, null=True, unique=False, verbose_name='所属城市' )
    jingdianredu=models.IntegerField  (  null=True, unique=False, verbose_name='景点热度' )
    menpiaojiage=models.IntegerField  (  null=True, unique=False, verbose_name='门票价格' )
    dangritianqi=models.CharField ( max_length=255, null=True, unique=False, verbose_name='当日天气' )
    rijunqiwen=models.IntegerField  (  null=True, unique=False, verbose_name='日均气温' )
    fenglidengji=models.IntegerField  (  null=True, unique=False, verbose_name='风力等级' )
    jiaotongbianjiedupingfen=models.IntegerField  (  null=True, unique=False, verbose_name='交通便捷度评分' )
    zhoubiantingchechangshuliang=models.IntegerField  (  null=True, unique=False, verbose_name='周边停车场数量' )
    fujingongjiaozhandianshu=models.IntegerField  (  null=True, unique=False, verbose_name='附近公交站点数' )
    ditiexianlukedaxing=models.CharField ( max_length=255, null=True, unique=False, verbose_name='地铁线路可达性' )
    shifoujiejiari=models.CharField ( max_length=255, null=True, unique=False, verbose_name='是否节假日' )
    jiejiarileixing=models.CharField ( max_length=255, null=True, unique=False, verbose_name='节假日类型' )
    rijunyoukejiedailiang=models.IntegerField  (  null=True, unique=False, verbose_name='日均游客接待量' )
    youkehaopinglv=models.IntegerField  (  null=True, unique=False, verbose_name='游客好评率' )
    zhoubianjiudianshuliang=models.IntegerField  (  null=True, unique=False, verbose_name='周边酒店数量' )
    '''
    tongjiriqi=Date
    jingdianmingcheng=VARCHAR
    jingdianleixing=VARCHAR
    suoshuchengshi=VARCHAR
    jingdianredu=Integer
    menpiaojiage=Integer
    dangritianqi=VARCHAR
    rijunqiwen=Integer
    fenglidengji=Integer
    jiaotongbianjiedupingfen=Integer
    zhoubiantingchechangshuliang=Integer
    fujingongjiaozhandianshu=Integer
    ditiexianlukedaxing=VARCHAR
    shifoujiejiari=VARCHAR
    jiejiarileixing=VARCHAR
    rijunyoukejiedailiang=Integer
    youkehaopinglv=Integer
    zhoubianjiudianshuliang=Integer
    '''
    class Meta:
        db_table = 'T_Comprehensive_data'
        verbose_name = verbose_name_plural = '旅游数据'
class news(BaseModel):
    __doc__ = u'''news'''
    __tablename__ = 'news'



    __authTables__={}
    __authPeople__='否'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='是'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    title=models.CharField ( max_length=255,null=False, unique=False, verbose_name='标题' )
    introduction=models.TextField   (  null=True, unique=False, verbose_name='简介' )
    picture=models.TextField   ( null=False, unique=False, verbose_name='图片' )
    content=models.TextField   ( null=False, unique=False, verbose_name='内容' )
    name=models.CharField ( max_length=255, null=True, unique=False, verbose_name='发布人' )
    headportrait=models.TextField   (  null=True, unique=False, verbose_name='头像' )
    '''
    title=VARCHAR
    introduction=Text
    picture=Text
    content=Text
    name=VARCHAR
    headportrait=Text
    '''
    class Meta:
        db_table = 'T_System_News'
        verbose_name = verbose_name_plural = '系统公告'
class storeup(BaseModel):
    __doc__ = u'''storeup'''
    __tablename__ = 'storeup'



    __authTables__={}
    __authSeparate__='是'#后台列表权限
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    userid=models.BigIntegerField  ( null=False, unique=False, verbose_name='用户id' )
    refid=models.BigIntegerField  (  null=True, unique=False, verbose_name='商品id' )
    tablename=models.CharField ( max_length=255, null=True, unique=False, verbose_name='表名' )
    name=models.CharField ( max_length=255,null=False, unique=False, verbose_name='名称' )
    picture=models.TextField   (  null=True, unique=False, verbose_name='图片' )
    type=models.CharField ( max_length=255, null=True, unique=False,default='1', verbose_name='类型' )
    inteltype=models.CharField ( max_length=255, null=True, unique=False, verbose_name='推荐类型' )
    remark=models.CharField ( max_length=255, null=True, unique=False, verbose_name='备注' )
    '''
    userid=BigInteger
    refid=BigInteger
    tablename=VARCHAR
    name=VARCHAR
    picture=Text
    type=VARCHAR
    inteltype=VARCHAR
    remark=VARCHAR
    '''
    class Meta:
        db_table = 'T_User_Behavior'
        verbose_name = verbose_name_plural = '收藏表'
class systemintro(BaseModel):
    __doc__ = u'''systemintro'''
    __tablename__ = 'systemintro'



    __authTables__={}
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    title=models.CharField ( max_length=255,null=False, unique=False, verbose_name='标题' )
    subtitle=models.CharField ( max_length=255, null=True, unique=False, verbose_name='副标题' )
    content=models.TextField   ( null=False, unique=False, verbose_name='内容' )
    picture1=models.TextField   (  null=True, unique=False, verbose_name='图片1' )
    picture2=models.TextField   (  null=True, unique=False, verbose_name='图片2' )
    picture3=models.TextField   (  null=True, unique=False, verbose_name='图片3' )
    '''
    title=VARCHAR
    subtitle=VARCHAR
    content=Text
    picture1=Text
    picture2=Text
    picture3=Text
    '''
    class Meta:
        db_table = 'T_System_Introduction'
        verbose_name = verbose_name_plural = '系统简介'
class smsregistercode(BaseModel):
    __doc__ = u'''smsregistercode'''
    __tablename__ = 'smsregistercode'



    __authTables__={}
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    mobile=models.CharField ( max_length=255,null=False, unique=False, verbose_name='手机' )
    role=models.CharField ( max_length=255,null=False, unique=False, verbose_name='角色' )
    code=models.CharField ( max_length=255,null=False, unique=False, verbose_name='验证码' )
    '''
    mobile=VARCHAR
    role=VARCHAR
    code=VARCHAR
    '''
    class Meta:
        db_table = 'T_SMS_Verification_Code'
        verbose_name = verbose_name_plural = '短信验证码'
class users(BaseModel):
    __doc__ = u'''users'''
    __tablename__ = 'users'



    __authTables__={}
    __authPeople__ = '是'
    __isAdmin__ = '是'
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    username=models.CharField ( max_length=255,null=False, unique=False, verbose_name='用户名' )
    password=models.CharField ( max_length=255,null=False, unique=False, verbose_name='密码' )
    role=models.CharField ( max_length=255, null=True, unique=False,default='管理员', verbose_name='角色' )
    image=models.TextField   (  null=True, unique=False, verbose_name='头像' )
    '''
    username=VARCHAR
    password=VARCHAR
    role=VARCHAR
    image=Text
    '''
    class Meta:
        db_table = 'T_Administrator'
        verbose_name = verbose_name_plural = '管理员'
class discussctripjd(BaseModel):
    __doc__ = u'''discussctripjd'''
    __tablename__ = 'discussctripjd'



    __authTables__={}
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    refid=models.BigIntegerField  ( null=False, unique=False, verbose_name='关联表id' )
    userid=models.BigIntegerField  ( null=False, unique=False, verbose_name='用户id' )
    avatarurl=models.TextField   (  null=True, unique=False, verbose_name='头像' )
    nickname=models.CharField ( max_length=255, null=True, unique=False, verbose_name='用户名' )
    content=models.TextField   ( null=False, unique=False, verbose_name='评论内容' )
    reply=models.TextField   (  null=True, unique=False, verbose_name='回复内容' )
    thumbsupnum=models.IntegerField  (  null=True, unique=False,default='0', verbose_name='赞' )
    crazilynum=models.IntegerField  (  null=True, unique=False,default='0', verbose_name='踩' )
    istop=models.IntegerField  (  null=True, unique=False,default='0', verbose_name='置顶' )
    tuserids=models.TextField   (  null=True, unique=False, verbose_name='赞用户ids' )
    cuserids=models.TextField   (  null=True, unique=False, verbose_name='踩用户ids' )
    '''
    refid=BigInteger
    userid=BigInteger
    avatarurl=Text
    nickname=VARCHAR
    content=Text
    reply=Text
    thumbsupnum=Integer
    crazilynum=Integer
    istop=Integer
    tuserids=Text
    cuserids=Text
    '''
    class Meta:
        db_table = 'T_tourist_Attraction_discuss'
        verbose_name = verbose_name_plural = '携程景点'
