#coding:utf-8
import base64, copy, logging, os, sys, time, xlrd, json, datetime, configparser
from django.http import JsonResponse
from django.apps import apps
import numbers
from collections import defaultdict
import math
from django.db.models.aggregates import Count,Sum
from django.db.models import Case, When, IntegerField, F
from django.forms import model_to_dict
import requests
from util.CustomJSONEncoder import CustomJsonEncoder
from .models import lvyoushuju
from util.codes import *
from urllib.parse import unquote
from util.auth import Auth
from util.common import Common
import util.message as mes
from django.db import connection
import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.db.models import Q
from util.baidubce_api import BaiDuBce
from .config_model import config


def lvyoushuju_default(request):

    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code,"msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        req_dict.update({"isdefault":"是"})
        data=lvyoushuju.getbyparams(lvyoushuju, lvyoushuju, req_dict)
        if len(data)>0:
            msg['data']  = data[0]
        else:
            msg['data']  = {}
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def lvyoushuju_page(request):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":10,"list":[]}}
        req_dict = request.session.get("req_dict")
        global lvyoushuju
        #当前登录用户信息
        tablename = Auth().getTokenInfo(request).get('tablename')

        msg['data']['list'], msg['data']['currPage'], msg['data']['totalPage'], msg['data']['total'], \
        msg['data']['pageSize']  =lvyoushuju.page(lvyoushuju, lvyoushuju,req_dict, request)
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def lvyoushuju_autoSort(request):
    '''
    ．智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
主要信息列表（如商品列表，新闻列表）中使用，显示最近点击的或最新添加的5条记录就行
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":10,"list":[]}}
        req_dict = request.session.get("req_dict")
        if "clicknum"  in lvyoushuju.getallcolumn(lvyoushuju,lvyoushuju):
            req_dict['sort']='clicknum'
        elif "browseduration"  in lvyoushuju.getallcolumn(lvyoushuju,lvyoushuju):
            req_dict['sort']='browseduration'
        else:
            req_dict['sort']='clicktime'
        req_dict['order']='desc'
        msg['data']['list'], msg['data']['currPage'], msg['data']['totalPage'], msg['data']['total'], \
        msg['data']['pageSize']  = lvyoushuju.page(lvyoushuju,lvyoushuju, req_dict)

        return JsonResponse(msg, encoder=CustomJsonEncoder)

#分类列表
def lvyoushuju_lists(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":[]}
        msg['data'],_,_,_,_  = lvyoushuju.page(lvyoushuju, lvyoushuju, {})
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def lvyoushuju_query(request):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        try:
            query_result = lvyoushuju.objects.filter(**request.session.get("req_dict")).values()
            msg['data'] = query_result[0]
        except Exception as e:

            msg['code'] = crud_error_code
            msg['msg'] = f"发生错误：{e}"
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def lvyoushuju_list(request):
    '''
    前台分页
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":10,"list":[]}}
        req_dict = request.session.get("req_dict")
        #获取全部列名
        columns=  lvyoushuju.getallcolumn( lvyoushuju, lvyoushuju)
        if "vipread" in req_dict and "vipread" not in columns:
          del req_dict["vipread"]
        #表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
        try:
            __foreEndList__=lvyoushuju.__foreEndList__
        except:
            __foreEndList__=None
        try:
            __foreEndListAuth__=lvyoushuju.__foreEndListAuth__
        except:
            __foreEndListAuth__=None

        #authSeparate
        try:
            __authSeparate__=lvyoushuju.__authSeparate__
        except:
            __authSeparate__=None

        if __foreEndListAuth__ =="是" and __authSeparate__=="是":
            tablename=Auth().getTokenInfo(request).get('tablename')
            if tablename!="users" and Auth().getTokenInfo(request).get('params') is not None:
                req_dict['userid']=Auth().getTokenInfo(request).get('params').get("id")

        tablename = Auth().getTokenInfo(request).get('tablename')
        if tablename == "users" and req_dict.get("userid") != None:#判断是否存在userid列名
            del req_dict["userid"]
        else:
            __isAdmin__ = None

            allModels = apps.get_app_config('main').get_models()
            for m in allModels:
                if m.__tablename__==tablename:

                    try:
                        __isAdmin__ = m.__isAdmin__
                    except:
                        __isAdmin__ = None
                    break

            if __isAdmin__ == "是":
                if req_dict.get("userid"):
        # del req_dict["userid"]
                    pass
            else:
    #非管理员权限的表,判断当前表字段名是否有userid
                if "userid" in columns:
                    try:
                        pass
                    except:
                        pass
        #当列属性authTable有值(某个用户表)[该列的列名必须和该用户表的登陆字段名一致]，则对应的表有个隐藏属性authTable为”是”，那么该用户查看该表信息时，只能查看自己的
        try:
            __authTables__=lvyoushuju.__authTables__
        except:
            __authTables__=None

        if __authTables__!=None and  __authTables__!={} and __foreEndListAuth__=="是":
            for authColumn,authTable in __authTables__.items():
                if authTable==tablename:
                    try:
                        del req_dict['userid']
                    except:
                        pass
                    params = Auth().getTokenInfo(request).get('params')
                    req_dict[authColumn]=params.get(authColumn)
                    username=params.get(authColumn)
                    break
        
        if lvyoushuju.__tablename__[:7]=="discuss":
            try:
                del req_dict['userid']
            except:
                pass

        q = Q()
        msg['data']['list'], msg['data']['currPage'], msg['data']['totalPage'], msg['data']['total'], \
        msg['data']['pageSize']  = lvyoushuju.page(lvyoushuju, lvyoushuju, req_dict, request, q)
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def lvyoushuju_save(request):
    '''
    后台新增
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        if 'clicktime' in req_dict.keys():
            del req_dict['clicktime']
        tablename=Auth().getTokenInfo(request).get('tablename')
        __isAdmin__ = None
        allModels = apps.get_app_config('main').get_models()
        for m in allModels:
            if m.__tablename__==tablename:

                try:
                    __isAdmin__ = m.__isAdmin__
                except:
                    __isAdmin__ = None
                break

        #获取全部列名
        columns=  lvyoushuju.getallcolumn( lvyoushuju, lvyoushuju)
        if tablename!='users' and req_dict.get("userid")==None and 'userid' in columns  and __isAdmin__!='是':
            params=Auth().getTokenInfo(request).get('params')
            req_dict['userid']=params.get('id')


        if 'addtime' in req_dict.keys():
            del req_dict['addtime']

        idOrErr= lvyoushuju.createbyreq(lvyoushuju,lvyoushuju, req_dict)
        if idOrErr is Exception:
            msg['code'] = crud_error_code
            msg['msg'] = idOrErr
        else:
            msg['data'] = idOrErr

        return JsonResponse(msg, encoder=CustomJsonEncoder)

def lvyoushuju_add(request):
    '''
    前台新增
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        tablename=Auth().getTokenInfo(request).get('tablename')

        #获取全部列名
        columns=  lvyoushuju.getallcolumn( lvyoushuju, lvyoushuju)
        try:
            __authSeparate__=lvyoushuju.__authSeparate__
        except:
            __authSeparate__=None

        if __authSeparate__=="是" and 'userid' not in req_dict.keys():
            tablename=Auth().getTokenInfo(request).get('tablename')
            if tablename!="users" and 'userid' in columns:
                try:
                    req_dict['userid']=Auth().getTokenInfo(request).get('params').get("id")
                except:
                    pass

        try:
            __foreEndListAuth__=lvyoushuju.__foreEndListAuth__
        except:
            __foreEndListAuth__=None

        if __foreEndListAuth__ and __foreEndListAuth__!="否" and 'userid' not in req_dict.keys():
            tablename=Auth().getTokenInfo(request).get('tablename')
            if tablename!="users":
                req_dict['userid']=Auth().getTokenInfo(request).get('params').get("id")


        if 'addtime' in req_dict.keys():
            del req_dict['addtime']
        error= lvyoushuju.createbyreq(lvyoushuju,lvyoushuju, req_dict)
        if error is Exception:
            msg['code'] = crud_error_code
            msg['msg'] = error
        else:
            msg['data'] = error
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def lvyoushuju_thumbsup(request,id_):
    '''
     点赞：表属性thumbsUp[是/否]，刷表新增thumbsupnum赞和crazilynum踩字段，
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        id_=int(id_)
        type_=int(req_dict.get("type",0))
        rets=lvyoushuju.getbyid(lvyoushuju,lvyoushuju,id_)

        update_dict={
        "id":id_,
        }
        if type_==1:#赞
            update_dict["thumbsupnum"]=int(rets[0].get('thumbsupnum'))+1
        elif type_==2:#踩
            update_dict["crazilynum"]=int(rets[0].get('crazilynum'))+1
        error = lvyoushuju.updatebyparams(lvyoushuju,lvyoushuju, update_dict)
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error
        return JsonResponse(msg, encoder=CustomJsonEncoder)


def lvyoushuju_info(request,id_):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}

        data = lvyoushuju.getbyid(lvyoushuju,lvyoushuju, int(id_))
        if len(data)>0:
            msg['data']=data[0]
            if msg['data'].__contains__("reversetime"):
                if isinstance(msg['data']['reversetime'], datetime.datetime):
                    msg['data']['reversetime'] = msg['data']['reversetime'].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    if msg['data']['reversetime'] != None:
                        reversetime = datetime.datetime.strptime(msg['data']['reversetime'], '%Y-%m-%d %H:%M:%S')
                        msg['data']['reversetime'] = reversetime.strftime("%Y-%m-%d %H:%M:%S")

        #浏览点击次数
        try:
            __browseClick__= lvyoushuju.__browseClick__
        except:
            __browseClick__=None

        if __browseClick__=="是"  and  "clicknum"  in lvyoushuju.getallcolumn(lvyoushuju,lvyoushuju):
            try:
                clicknum=int(data[0].get("clicknum",0))+1
            except:
                clicknum=0+1
            click_dict={"id":int(id_),"clicknum":clicknum,"clicktime":datetime.datetime.now()}
            ret=lvyoushuju.updatebyparams(lvyoushuju,lvyoushuju,click_dict)
            if ret!=None:
                msg['code'] = crud_error_code
                msg['msg'] = ret
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def lvyoushuju_detail(request,id_):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}

        data =lvyoushuju.getbyid(lvyoushuju,lvyoushuju, int(id_))
        if len(data)>0:
            msg['data']=data[0]
            if msg['data'].__contains__("reversetime"):
                if isinstance(msg['data']['reversetime'], datetime.datetime):
                    msg['data']['reversetime'] = msg['data']['reversetime'].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    if msg['data']['reversetime'] != None:
                        reversetime = datetime.datetime.strptime(msg['data']['reversetime'], '%Y-%m-%d %H:%M:%S')
                        msg['data']['reversetime'] = reversetime.strftime("%Y-%m-%d %H:%M:%S")

        #浏览点击次数
        try:
            __browseClick__= lvyoushuju.__browseClick__
        except:
            __browseClick__=None

        if __browseClick__=="是"   and  "clicknum"  in lvyoushuju.getallcolumn(lvyoushuju,lvyoushuju):
            try:
                clicknum=int(data[0].get("clicknum",0))+1
            except:
                clicknum=0+1
            click_dict={"id":int(id_),"clicknum":clicknum,"clicktime":datetime.datetime.now()}

            ret=lvyoushuju.updatebyparams(lvyoushuju,lvyoushuju,click_dict)
            if ret!=None:
                msg['code'] = crud_error_code
                msg['msg'] = ret
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def lvyoushuju_update(request):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        if 'clicktime' in req_dict.keys() and req_dict['clicktime']=="None":
            del req_dict['clicktime']
        if req_dict.get("mima") and "mima" not in lvyoushuju.getallcolumn(lvyoushuju,lvyoushuju) :
            del req_dict["mima"]
        if req_dict.get("password") and "password" not in lvyoushuju.getallcolumn(lvyoushuju,lvyoushuju) :
            del req_dict["password"]
        try:
            del req_dict["clicknum"]
        except:
            pass


        error = lvyoushuju.updatebyparams(lvyoushuju, lvyoushuju, req_dict)
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error

        return JsonResponse(msg)


def lvyoushuju_delete(request):
    '''
    批量删除
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")

        error=lvyoushuju.deletes(lvyoushuju,
            lvyoushuju,
             req_dict.get("ids")
        )
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error
        return JsonResponse(msg)


def lvyoushuju_vote(request,id_):
    '''
    浏览点击次数（表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1）
统计商品或新闻的点击次数；提供新闻的投票功能
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code}


        data= lvyoushuju.getbyid(lvyoushuju, lvyoushuju, int(id_))
        for i in data:
            votenum=i.get('votenum')
            if votenum!=None:
                params={"id":int(id_),"votenum":votenum+1}
                error=lvyoushuju.updatebyparams(lvyoushuju,lvyoushuju,params)
                if error!=None:
                    msg['code'] = crud_error_code
                    msg['msg'] = error
        return JsonResponse(msg)

def lvyoushuju_importExcel(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}

        excel_file = request.FILES.get("file", "")
        if excel_file.size > 100 * 1024 * 1024:  # 限制为 100MB
            msg['code'] = 400
            msg["msg"] = '文件大小不能超过100MB'
            return JsonResponse(msg)

        file_type = excel_file.name.split('.')[1]
        
        if file_type in ['xlsx', 'xls']:
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
            table = data.sheets()[0]
            rows = table.nrows
            
            try:
                for row in range(1, rows):
                    row_values = table.row_values(row)
                    req_dict = {}
                    if str(row_values[0]) != '':
                        try:
                            date_tuple = xlrd.xldate_as_tuple(row_values[0], 0)
                            date_str = '-'.join([str(i) for i in date_tuple[:-3]])
                            req_dict['tongjiriqi'] = datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
                        except:
                            req_dict['tongjiriqi'] = row_values[0]
                    else:
                        req_dict['tongjiriqi'] = None
                    if '.0' in str(row_values[1]):
                        req_dict['jingdianmingcheng'] = str(row_values[1]).split('.')[0]
                    elif str(row_values[1]) != '':
                        req_dict['jingdianmingcheng'] = row_values[1]
                    else:
                        req_dict['jingdianmingcheng'] = None
                    if '.0' in str(row_values[2]):
                        req_dict['jingdianleixing'] = str(row_values[2]).split('.')[0]
                    elif str(row_values[2]) != '':
                        req_dict['jingdianleixing'] = row_values[2]
                    else:
                        req_dict['jingdianleixing'] = None
                    if '.0' in str(row_values[3]):
                        req_dict['suoshuchengshi'] = str(row_values[3]).split('.')[0]
                    elif str(row_values[3]) != '':
                        req_dict['suoshuchengshi'] = row_values[3]
                    else:
                        req_dict['suoshuchengshi'] = None
                    if '.0' in str(row_values[4]):
                        req_dict['jingdianredu'] = str(row_values[4]).split('.')[0]
                    elif str(row_values[4]) != '':
                        req_dict['jingdianredu'] = row_values[4]
                    else:
                        req_dict['jingdianredu'] = None
                    if '.0' in str(row_values[5]):
                        req_dict['menpiaojiage'] = str(row_values[5]).split('.')[0]
                    elif str(row_values[5]) != '':
                        req_dict['menpiaojiage'] = row_values[5]
                    else:
                        req_dict['menpiaojiage'] = None
                    if '.0' in str(row_values[6]):
                        req_dict['dangritianqi'] = str(row_values[6]).split('.')[0]
                    elif str(row_values[6]) != '':
                        req_dict['dangritianqi'] = row_values[6]
                    else:
                        req_dict['dangritianqi'] = None
                    if '.0' in str(row_values[7]):
                        req_dict['rijunqiwen'] = str(row_values[7]).split('.')[0]
                    elif str(row_values[7]) != '':
                        req_dict['rijunqiwen'] = row_values[7]
                    else:
                        req_dict['rijunqiwen'] = None
                    if '.0' in str(row_values[8]):
                        req_dict['fenglidengji'] = str(row_values[8]).split('.')[0]
                    elif str(row_values[8]) != '':
                        req_dict['fenglidengji'] = row_values[8]
                    else:
                        req_dict['fenglidengji'] = None
                    if '.0' in str(row_values[9]):
                        req_dict['jiaotongbianjiedupingfen'] = str(row_values[9]).split('.')[0]
                    elif str(row_values[9]) != '':
                        req_dict['jiaotongbianjiedupingfen'] = row_values[9]
                    else:
                        req_dict['jiaotongbianjiedupingfen'] = None
                    if '.0' in str(row_values[10]):
                        req_dict['zhoubiantingchechangshuliang'] = str(row_values[10]).split('.')[0]
                    elif str(row_values[10]) != '':
                        req_dict['zhoubiantingchechangshuliang'] = row_values[10]
                    else:
                        req_dict['zhoubiantingchechangshuliang'] = None
                    if '.0' in str(row_values[11]):
                        req_dict['fujingongjiaozhandianshu'] = str(row_values[11]).split('.')[0]
                    elif str(row_values[11]) != '':
                        req_dict['fujingongjiaozhandianshu'] = row_values[11]
                    else:
                        req_dict['fujingongjiaozhandianshu'] = None
                    if '.0' in str(row_values[12]):
                        req_dict['ditiexianlukedaxing'] = str(row_values[12]).split('.')[0]
                    elif str(row_values[12]) != '':
                        req_dict['ditiexianlukedaxing'] = row_values[12]
                    else:
                        req_dict['ditiexianlukedaxing'] = None
                    if '.0' in str(row_values[13]):
                        req_dict['shifoujiejiari'] = str(row_values[13]).split('.')[0]
                    elif str(row_values[13]) != '':
                        req_dict['shifoujiejiari'] = row_values[13]
                    else:
                        req_dict['shifoujiejiari'] = None
                    if '.0' in str(row_values[14]):
                        req_dict['jiejiarileixing'] = str(row_values[14]).split('.')[0]
                    elif str(row_values[14]) != '':
                        req_dict['jiejiarileixing'] = row_values[14]
                    else:
                        req_dict['jiejiarileixing'] = None
                    if '.0' in str(row_values[15]):
                        req_dict['rijunyoukejiedailiang'] = str(row_values[15]).split('.')[0]
                    elif str(row_values[15]) != '':
                        req_dict['rijunyoukejiedailiang'] = row_values[15]
                    else:
                        req_dict['rijunyoukejiedailiang'] = None
                    if '.0' in str(row_values[16]):
                        req_dict['youkehaopinglv'] = str(row_values[16]).split('.')[0]
                    elif str(row_values[16]) != '':
                        req_dict['youkehaopinglv'] = row_values[16]
                    else:
                        req_dict['youkehaopinglv'] = None
                    if '.0' in str(row_values[17]):
                        req_dict['zhoubianjiudianshuliang'] = str(row_values[17]).split('.')[0]
                    elif str(row_values[17]) != '':
                        req_dict['zhoubianjiudianshuliang'] = row_values[17]
                    else:
                        req_dict['zhoubianjiudianshuliang'] = None
                    lvyoushuju.createbyreq(lvyoushuju, lvyoushuju, req_dict)
                    
            except:
                pass
                
        else:
            msg = {
                "msg": "文件类型错误",
                "code": 500
            }
                
        return JsonResponse(msg)

def lvyoushuju_autoSort2(request):
    return JsonResponse({"code": 0, "msg": '',  "data":{}})












