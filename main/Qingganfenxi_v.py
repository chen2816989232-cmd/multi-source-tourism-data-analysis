#coding:utf-8
import base64, copy, logging, os, sys, time, xlrd, json, datetime, configparser, re
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
from .models import qingganfenxi
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


def _safe_y_column_names(req_dict):
    raw_value = (req_dict or {}).get("yColumnNameMul")
    if raw_value is None:
        return []
    return [item.strip() for item in str(raw_value).split(",") if item and item.strip()]


def _safe_y_column_filename(req_dict):
    return "".join(_safe_y_column_names(req_dict))


_SENTIMENT_SCHEMA_READY = False
UNKNOWN_SPOT_NAME = "\u672a\u5173\u8054\u666f\u70b9"
POSITIVE_SENTIMENT = "\u60a8\u7684\u60c5\u611f\u504f\u6b63\u5411\U0001f600"
NEUTRAL_SENTIMENT = "\u60a8\u7684\u60c5\u611f\u504f\u4e2d\u6027\U0001f610"
NEGATIVE_SENTIMENT = "\u60a8\u7684\u60c5\u611f\u504f\u8d1f\u5411\u2639\ufe0f"
POSITIVE_WORDS = [
    "\u597d", "\u68d2", "\u7f8e", "\u503c\u5f97", "\u559c\u6b22", "\u63a8\u8350", "\u9707\u64bc",
    "\u58ee\u89c2", "\u65b9\u4fbf", "\u5e72\u51c0", "\u5f00\u5fc3", "\u6ee1\u5206", "\u8212\u670d",
    "\u6709\u8da3", "\u60ca\u559c", "\u4f18\u79c0", "\u70ed\u60c5", "\u8d5e", "\u6f02\u4eae",
    "\u7ecf\u5178", "\u58ee\u7f8e", "\u7cbe\u7f8e", "\u5b8c\u7f8e", "\u79f0\u5947", "\u597d\u73a9",
]
NEGATIVE_WORDS = [
    "\u5dee", "\u8d35", "\u5751", "\u4e0d\u503c", "\u5931\u671b", "\u96be", "\u7d2f", "\u810f",
    "\u4e71", "\u5dee\u8bc4", "\u6392\u961f", "\u62e5\u6324", "\u4eba\u592a\u591a",
    "\u6ca1\u610f\u601d", "\u715e\u98ce\u666f", "\u7cdf\u7cd5", "\u540e\u6094",
    "\u4e0d\u597d", "\u4e00\u822c", "\u5546\u4e1a\u5316", "\u9a97", "\u4e0d\u63a8\u8350",
]


def ensure_sentiment_spot_schema():
    """Keep the sentiment table compatible with the final project schema."""
    global _SENTIMENT_SCHEMA_READY
    if _SENTIMENT_SCHEMA_READY:
        return
    with connection.cursor() as cursor:
        cursor.execute("SHOW COLUMNS FROM T_Sentiment_Analysis LIKE %s", ["poiname"])
        if cursor.fetchone() is None:
            cursor.execute(
                "ALTER TABLE T_Sentiment_Analysis "
                "ADD COLUMN `poiname` VARCHAR(255) DEFAULT NULL COMMENT '景点名称' AFTER `addtime`"
            )
        cursor.execute("SHOW COLUMNS FROM T_Sentiment_Analysis LIKE %s", ["reviewid"])
        if cursor.fetchone() is None:
            cursor.execute(
                "ALTER TABLE T_Sentiment_Analysis "
                "ADD COLUMN `reviewid` BIGINT DEFAULT NULL COMMENT '评论编号' AFTER `poiname`"
            )
    _SENTIMENT_SCHEMA_READY = True


def extract_ctrip_spot_id(url):
    if not url:
        return None
    match = re.search(r"/comment/detail/(\d+)/", str(url))
    return match.group(1) if match else None


def find_poiname_by_plurl(plurl):
    spot_id = extract_ctrip_spot_id(plurl)
    if not spot_id:
        return None

    with connection.cursor() as cursor:
        for table_name in ("T_Core_attractions", "T_temporary_attractions"):
            cursor.execute(
                "SELECT poiname FROM {0} WHERE detailurl LIKE %s ORDER BY id DESC LIMIT 1".format(table_name),
                ["%/{0}.html%".format(spot_id)],
            )
            spot = cursor.fetchone()
            if spot and spot[0]:
                return spot[0]
    return None


def infer_poiname_from_review(record):
    reviewid = record.get("reviewid")
    if reviewid:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT plurl FROM T_Attraction_Reviews WHERE id=%s LIMIT 1",
                [reviewid],
            )
            row = cursor.fetchone()
            if row:
                return find_poiname_by_plurl(row[0])

    content = record.get("content")
    if not content:
        return None

    params = [content]
    sql = "SELECT plurl FROM T_Attraction_Reviews WHERE content=%s"
    if record.get("usernick"):
        sql += " AND usernick=%s"
        params.append(record.get("usernick"))
    if record.get("dptime"):
        sql += " AND dptime=%s"
        params.append(record.get("dptime"))
    sql += " ORDER BY id DESC LIMIT 1"

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        row = cursor.fetchone()
        if not row:
            return None

        return find_poiname_by_plurl(row[0])


def analyze_sentiment_text(text):
    text = str(text or "")
    positive_score = sum(text.count(word) for word in POSITIVE_WORDS)
    negative_score = sum(text.count(word) for word in NEGATIVE_WORDS)
    if positive_score > negative_score:
        return POSITIVE_SENTIMENT
    if negative_score > positive_score:
        return NEGATIVE_SENTIMENT
    return NEUTRAL_SENTIMENT


def fill_poiname_for_records(records, persist=True):
    for item in records:
        if item.get("poiname"):
            continue
        poiname = infer_poiname_from_review(item)
        item["poiname"] = poiname or UNKNOWN_SPOT_NAME
        if persist and poiname and item.get("id"):
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE T_Sentiment_Analysis SET poiname=%s "
                    "WHERE id=%s AND (poiname IS NULL OR poiname='')",
                    [poiname, item.get("id")],
                )
    return records


def fill_poiname_for_request(req_dict):
    if req_dict.get("poiname"):
        return req_dict
    poiname = infer_poiname_from_review(req_dict)
    if poiname:
        req_dict["poiname"] = poiname
    return req_dict


def attach_review_ids_to_existing_sentiments():
    linked_count = 0
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, content, usernick, dptime FROM T_Sentiment_Analysis "
            "WHERE reviewid IS NULL OR reviewid=0"
        )
        rows = cursor.fetchall()

    for sentiment_id, content, usernick, dptime in rows:
        params = [content]
        sql = "SELECT id, plurl FROM T_Attraction_Reviews WHERE content=%s"
        if usernick:
            sql += " AND usernick=%s"
            params.append(usernick)
        if dptime:
            sql += " AND dptime=%s"
            params.append(dptime)
        sql += " ORDER BY id ASC LIMIT 1"

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            review = cursor.fetchone()
            if not review:
                continue
            poiname = find_poiname_by_plurl(review[1])
            cursor.execute(
                "UPDATE T_Sentiment_Analysis SET reviewid=%s, poiname=COALESCE(NULLIF(poiname, ''), %s) "
                "WHERE id=%s",
                [review[0], poiname, sentiment_id],
            )
            linked_count += 1
    return linked_count


def deduplicate_sentiments_by_reviewid():
    removed_count = 0
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT reviewid, MIN(id) AS keep_id, COUNT(*) AS total "
            "FROM T_Sentiment_Analysis "
            "WHERE reviewid IS NOT NULL AND reviewid<>0 "
            "GROUP BY reviewid HAVING COUNT(*) > 1"
        )
        duplicate_groups = cursor.fetchall()

    for reviewid, keep_id, total in duplicate_groups:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM T_Sentiment_Analysis WHERE reviewid=%s AND id<>%s",
                [reviewid, keep_id],
            )
            removed_count += cursor.rowcount
    return removed_count


def preview_sentiment_results_from_reviews():
    ensure_sentiment_spot_schema()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM T_Attraction_Reviews")
        review_total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM T_Sentiment_Analysis")
        sentiment_total = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM T_Attraction_Reviews r "
            "WHERE r.content IS NOT NULL AND r.content<>'' "
            "AND NOT EXISTS (SELECT 1 FROM T_Sentiment_Analysis s WHERE s.reviewid=r.id)"
        )
        remaining_count = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COALESCE(SUM(total - 1), 0) FROM ("
            "  SELECT COUNT(*) AS total FROM T_Sentiment_Analysis "
            "  WHERE reviewid IS NOT NULL AND reviewid<>0 "
            "  GROUP BY reviewid HAVING COUNT(*) > 1"
            ") duplicate_groups"
        )
        duplicate_count = cursor.fetchone()[0] or 0

    return {
        "dry_run": True,
        "review_total": review_total,
        "sentiment_total": sentiment_total,
        "linked_existing": 0,
        "removed_duplicates": 0,
        "duplicate_candidates": duplicate_count,
        "created": 0,
        "would_create": remaining_count,
        "unknown_spot": 0,
        "remaining": remaining_count,
    }


def build_sentiment_results_from_reviews(limit=None, deduplicate=False):
    ensure_sentiment_spot_schema()
    linked_count = attach_review_ids_to_existing_sentiments()
    removed_count = deduplicate_sentiments_by_reviewid() if deduplicate else 0

    sql = (
        "SELECT r.id, r.content, r.usernick, r.dptime, r.plurl "
        "FROM T_Attraction_Reviews r "
        "WHERE r.content IS NOT NULL AND r.content<>'' "
        "AND NOT EXISTS ("
        "  SELECT 1 FROM T_Sentiment_Analysis s WHERE s.reviewid=r.id"
        ") "
        "ORDER BY r.id ASC"
    )
    if limit:
        sql += " LIMIT {0}".format(int(limit))

    with connection.cursor() as cursor:
        cursor.execute(sql)
        reviews = cursor.fetchall()

    created_count = 0
    unknown_spot_count = 0
    for reviewid, content, usernick, dptime, plurl in reviews:
        poiname = find_poiname_by_plurl(plurl) or UNKNOWN_SPOT_NAME
        if poiname == UNKNOWN_SPOT_NAME:
            unknown_spot_count += 1
        fenxijieguo = analyze_sentiment_text(content)
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO T_Sentiment_Analysis "
                "(poiname, reviewid, usernick, content, dptime, fenxijieguo) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                [poiname, reviewid, usernick, content, dptime, fenxijieguo],
            )
        created_count += 1

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM T_Attraction_Reviews")
        review_total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM T_Sentiment_Analysis")
        sentiment_total = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM T_Attraction_Reviews r "
            "WHERE NOT EXISTS (SELECT 1 FROM T_Sentiment_Analysis s WHERE s.reviewid=r.id)"
        )
        remaining_count = cursor.fetchone()[0]

    return {
        "review_total": review_total,
        "sentiment_total": sentiment_total,
        "linked_existing": linked_count,
        "removed_duplicates": removed_count,
        "created": created_count,
        "unknown_spot": unknown_spot_count,
        "remaining": remaining_count,
    }


def qingganfenxi_default(request):

    if request.method in ["POST", "GET"]:
        ensure_sentiment_spot_schema()
        msg = {"code": normal_code,"msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        req_dict.update({"isdefault":"是"})
        data=qingganfenxi.getbyparams(qingganfenxi, qingganfenxi, req_dict)
        if len(data)>0:
            msg['data']  = fill_poiname_for_records([data[0]])[0]
        else:
            msg['data']  = {}
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def qingganfenxi_page(request):
    '''
    '''
    if request.method in ["POST", "GET"]:
        ensure_sentiment_spot_schema()
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":10,"list":[]}}
        req_dict = request.session.get("req_dict")
        global qingganfenxi
        #当前登录用户信息
        tablename = Auth().getTokenInfo(request).get('tablename')

        msg['data']['list'], msg['data']['currPage'], msg['data']['totalPage'], msg['data']['total'], \
        msg['data']['pageSize']  =qingganfenxi.page(qingganfenxi, qingganfenxi,req_dict, request)
        msg['data']['list'] = fill_poiname_for_records(msg['data']['list'])
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def qingganfenxi_autoSort(request):
    '''
    ．智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
主要信息列表（如商品列表，新闻列表）中使用，显示最近点击的或最新添加的5条记录就行
    '''
    if request.method in ["POST", "GET"]:
        ensure_sentiment_spot_schema()
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":10,"list":[]}}
        req_dict = request.session.get("req_dict")
        if "clicknum"  in qingganfenxi.getallcolumn(qingganfenxi,qingganfenxi):
            req_dict['sort']='clicknum'
        elif "browseduration"  in qingganfenxi.getallcolumn(qingganfenxi,qingganfenxi):
            req_dict['sort']='browseduration'
        else:
            req_dict['sort']='clicktime'
        req_dict['order']='desc'
        msg['data']['list'], msg['data']['currPage'], msg['data']['totalPage'], msg['data']['total'], \
        msg['data']['pageSize']  = qingganfenxi.page(qingganfenxi,qingganfenxi, req_dict)
        msg['data']['list'] = fill_poiname_for_records(msg['data']['list'])

        return JsonResponse(msg, encoder=CustomJsonEncoder)

#分类列表
def qingganfenxi_lists(request):
    if request.method in ["POST", "GET"]:
        ensure_sentiment_spot_schema()
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":[]}
        msg['data'],_,_,_,_  = qingganfenxi.page(qingganfenxi, qingganfenxi, {})
        msg['data'] = fill_poiname_for_records(msg['data'])
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def qingganfenxi_query(request):
    '''
    '''
    if request.method in ["POST", "GET"]:
        ensure_sentiment_spot_schema()
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        try:
            query_result = qingganfenxi.objects.filter(**request.session.get("req_dict")).values()
            msg['data'] = fill_poiname_for_records([query_result[0]])[0]
        except Exception as e:

            msg['code'] = crud_error_code
            msg['msg'] = f"发生错误：{e}"
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def qingganfenxi_list(request):
    '''
    前台分页
    '''
    if request.method in ["POST", "GET"]:
        ensure_sentiment_spot_schema()
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":10,"list":[]}}
        req_dict = request.session.get("req_dict")
        #获取全部列名
        columns=  qingganfenxi.getallcolumn( qingganfenxi, qingganfenxi)
        if "vipread" in req_dict and "vipread" not in columns:
          del req_dict["vipread"]
        #表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
        try:
            __foreEndList__=qingganfenxi.__foreEndList__
        except:
            __foreEndList__=None
        try:
            __foreEndListAuth__=qingganfenxi.__foreEndListAuth__
        except:
            __foreEndListAuth__=None

        #authSeparate
        try:
            __authSeparate__=qingganfenxi.__authSeparate__
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
            __authTables__=qingganfenxi.__authTables__
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
        
        if qingganfenxi.__tablename__[:7]=="discuss":
            try:
                del req_dict['userid']
            except:
                pass

        q = Q()
        msg['data']['list'], msg['data']['currPage'], msg['data']['totalPage'], msg['data']['total'], \
        msg['data']['pageSize']  = qingganfenxi.page(qingganfenxi, qingganfenxi, req_dict, request, q)
        msg['data']['list'] = fill_poiname_for_records(msg['data']['list'])
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def qingganfenxi_save(request):
    '''
    后台新增
    '''
    if request.method in ["POST", "GET"]:
        ensure_sentiment_spot_schema()
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict") or {}
        fill_poiname_for_request(req_dict)
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
        columns=  qingganfenxi.getallcolumn( qingganfenxi, qingganfenxi)
        if tablename!='users' and req_dict.get("userid")==None and 'userid' in columns  and __isAdmin__!='是':
            params=Auth().getTokenInfo(request).get('params')
            req_dict['userid']=params.get('id')


        if 'addtime' in req_dict.keys():
            del req_dict['addtime']

        idOrErr= qingganfenxi.createbyreq(qingganfenxi,qingganfenxi, req_dict)
        if idOrErr is Exception:
            msg['code'] = crud_error_code
            msg['msg'] = idOrErr
        else:
            msg['data'] = idOrErr

        return JsonResponse(msg, encoder=CustomJsonEncoder)

def qingganfenxi_add(request):
    '''
    前台新增
    '''
    if request.method in ["POST", "GET"]:
        ensure_sentiment_spot_schema()
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        fill_poiname_for_request(req_dict)
        tablename=Auth().getTokenInfo(request).get('tablename')

        #获取全部列名
        columns=  qingganfenxi.getallcolumn( qingganfenxi, qingganfenxi)
        try:
            __authSeparate__=qingganfenxi.__authSeparate__
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
            __foreEndListAuth__=qingganfenxi.__foreEndListAuth__
        except:
            __foreEndListAuth__=None

        if __foreEndListAuth__ and __foreEndListAuth__!="否" and 'userid' not in req_dict.keys():
            tablename=Auth().getTokenInfo(request).get('tablename')
            if tablename!="users":
                req_dict['userid']=Auth().getTokenInfo(request).get('params').get("id")


        if 'addtime' in req_dict.keys():
            del req_dict['addtime']
        error= qingganfenxi.createbyreq(qingganfenxi,qingganfenxi, req_dict)
        if error is Exception:
            msg['code'] = crud_error_code
            msg['msg'] = error
        else:
            msg['data'] = error
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def qingganfenxi_thumbsup(request,id_):
    '''
     点赞：表属性thumbsUp[是/否]，刷表新增thumbsupnum赞和crazilynum踩字段，
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        id_=int(id_)
        type_=int(req_dict.get("type",0))
        rets=qingganfenxi.getbyid(qingganfenxi,qingganfenxi,id_)

        update_dict={
        "id":id_,
        }
        if type_==1:#赞
            update_dict["thumbsupnum"]=int(rets[0].get('thumbsupnum'))+1
        elif type_==2:#踩
            update_dict["crazilynum"]=int(rets[0].get('crazilynum'))+1
        error = qingganfenxi.updatebyparams(qingganfenxi,qingganfenxi, update_dict)
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error
        return JsonResponse(msg, encoder=CustomJsonEncoder)


def qingganfenxi_info(request,id_):
    '''
    '''
    if request.method in ["POST", "GET"]:
        ensure_sentiment_spot_schema()
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}

        data = qingganfenxi.getbyid(qingganfenxi,qingganfenxi, int(id_))
        if len(data)>0:
            msg['data']=fill_poiname_for_records([data[0]])[0]
            if msg['data'].__contains__("reversetime"):
                if isinstance(msg['data']['reversetime'], datetime.datetime):
                    msg['data']['reversetime'] = msg['data']['reversetime'].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    if msg['data']['reversetime'] != None:
                        reversetime = datetime.datetime.strptime(msg['data']['reversetime'], '%Y-%m-%d %H:%M:%S')
                        msg['data']['reversetime'] = reversetime.strftime("%Y-%m-%d %H:%M:%S")

        #浏览点击次数
        try:
            __browseClick__= qingganfenxi.__browseClick__
        except:
            __browseClick__=None

        if __browseClick__=="是"  and  "clicknum"  in qingganfenxi.getallcolumn(qingganfenxi,qingganfenxi):
            try:
                clicknum=int(data[0].get("clicknum",0))+1
            except:
                clicknum=0+1
            click_dict={"id":int(id_),"clicknum":clicknum,"clicktime":datetime.datetime.now()}
            ret=qingganfenxi.updatebyparams(qingganfenxi,qingganfenxi,click_dict)
            if ret!=None:
                msg['code'] = crud_error_code
                msg['msg'] = ret
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def qingganfenxi_detail(request,id_):
    '''
    '''
    if request.method in ["POST", "GET"]:
        ensure_sentiment_spot_schema()
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}

        data =qingganfenxi.getbyid(qingganfenxi,qingganfenxi, int(id_))
        if len(data)>0:
            msg['data']=fill_poiname_for_records([data[0]])[0]
            if msg['data'].__contains__("reversetime"):
                if isinstance(msg['data']['reversetime'], datetime.datetime):
                    msg['data']['reversetime'] = msg['data']['reversetime'].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    if msg['data']['reversetime'] != None:
                        reversetime = datetime.datetime.strptime(msg['data']['reversetime'], '%Y-%m-%d %H:%M:%S')
                        msg['data']['reversetime'] = reversetime.strftime("%Y-%m-%d %H:%M:%S")

        #浏览点击次数
        try:
            __browseClick__= qingganfenxi.__browseClick__
        except:
            __browseClick__=None

        if __browseClick__=="是"   and  "clicknum"  in qingganfenxi.getallcolumn(qingganfenxi,qingganfenxi):
            try:
                clicknum=int(data[0].get("clicknum",0))+1
            except:
                clicknum=0+1
            click_dict={"id":int(id_),"clicknum":clicknum,"clicktime":datetime.datetime.now()}

            ret=qingganfenxi.updatebyparams(qingganfenxi,qingganfenxi,click_dict)
            if ret!=None:
                msg['code'] = crud_error_code
                msg['msg'] = ret
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def qingganfenxi_update(request):
    '''
    '''
    if request.method in ["POST", "GET"]:
        ensure_sentiment_spot_schema()
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        fill_poiname_for_request(req_dict)
        if 'clicktime' in req_dict.keys() and req_dict['clicktime']=="None":
            del req_dict['clicktime']
        if req_dict.get("mima") and "mima" not in qingganfenxi.getallcolumn(qingganfenxi,qingganfenxi) :
            del req_dict["mima"]
        if req_dict.get("password") and "password" not in qingganfenxi.getallcolumn(qingganfenxi,qingganfenxi) :
            del req_dict["password"]
        try:
            del req_dict["clicknum"]
        except:
            pass


        error = qingganfenxi.updatebyparams(qingganfenxi, qingganfenxi, req_dict)
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error

        return JsonResponse(msg)


def qingganfenxi_delete(request):
    '''
    批量删除
    '''
    if request.method in ["POST", "GET"]:
        ensure_sentiment_spot_schema()
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")

        error=qingganfenxi.deletes(qingganfenxi,
            qingganfenxi,
             req_dict.get("ids")
        )
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error
        return JsonResponse(msg)


def qingganfenxi_vote(request,id_):
    '''
    浏览点击次数（表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1）
统计商品或新闻的点击次数；提供新闻的投票功能
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code}


        data= qingganfenxi.getbyid(qingganfenxi, qingganfenxi, int(id_))
        for i in data:
            votenum=i.get('votenum')
            if votenum!=None:
                params={"id":int(id_),"votenum":votenum+1}
                error=qingganfenxi.updatebyparams(qingganfenxi,qingganfenxi,params)
                if error!=None:
                    msg['code'] = crud_error_code
                    msg['msg'] = error
        return JsonResponse(msg)

def qingganfenxi_importExcel(request):
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
                    qingganfenxi.createbyreq(qingganfenxi, qingganfenxi, req_dict)
                    
            except:
                pass
                
        else:
            msg = {
                "msg": "文件类型错误",
                "code": 500
            }
                
        return JsonResponse(msg)

def qingganfenxi_autoSort2(request):
    return JsonResponse({"code": 0, "msg": '',  "data":{}})



def qingganfenxi_count(request):
    '''
    总数接口
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}
        req_dict = request.session.get("req_dict")
        where = ' where 1 = 1 '
        for key in req_dict:
            if req_dict[key] != None:
                where = where + " and key like '{0}'".format(req_dict[key])
        
        sql = "SELECT count(*) AS count FROM T_Sentiment_Analysis {0}".format(where)
        count = 0
        cursor = connection.cursor()
        cursor.execute(sql)
        desc = cursor.description
        data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()] 
        for online_dict in data_dict:
            count = online_dict['count']
        msg['data'] = count

        return JsonResponse(msg, encoder=CustomJsonEncoder)

#对日期进行排序
def order_time(data,type,xColumnName,rev):
    if type=="日":
        result_data = sorted(
            data,
            key=lambda x: (
                int(x[xColumnName].split("-")[0]),
                int(x[xColumnName].split("-")[1]),
                int(x[xColumnName].split("-")[2]),
            ),
            reverse=rev  # 设置排列
        )
    elif type=="月":
        result_data = sorted(
            data,
            key=lambda x: (
                int(x[xColumnName].split("-")[0]),
                int(x[xColumnName].split("-")[1])
            ),
            reverse=rev  # 设置排列
        )
    elif type=="年":
        result_data = sorted(
            data,
            key=lambda x: (
                int(x[xColumnName].split("-")[0]),  # 提取年份并转为整数
            ),
            reverse=rev  # 设置排列
        )
    else:
        result_data = sorted(data, key=lambda x: x[xColumnName], reverse=rev)
    return result_data

# （按值统计）时间统计类型
def qingganfenxi_value(request, xColumnName, yColumnName, timeStatType):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}
        #获取hadoop分析后的数据文件
        date_type = ""
        if timeStatType == '日':
            date_type = "date"
        if timeStatType == '月':
            date_type = "month"
        if timeStatType == '季':
            date_type = "quarter"
        if timeStatType == '年':
            date_type = "year"
        json_filename = f'qingganfenxi_value{xColumnName}{yColumnName}{date_type}.json'

        if os.path.exists(json_filename) == True:
            with open(json_filename, encoding='utf-8') as f:
                msg['data'] = json.load(f)
        else:
            where = ' where 1 = 1 '
            raw_query_string = request.META.get('QUERY_STRING', '')
            raw_query_string = unquote(raw_query_string)
            conditionColumn = ""
            conditionValue = ""
            if "conditionColumn=" in raw_query_string:
                conditionColumn = raw_query_string.split("conditionColumn=")[1].split("&")[0]
            if "conditionValue=" in raw_query_string:
                conditionValue = raw_query_string.split("conditionValue=")[1].split("&")[0]
            if conditionColumn != "":
                for index, value in enumerate(conditionColumn.split(";")):
                    if ',' in value:
                        where = where + f''' and {value.split(',')[0]} >= \'{conditionValue.split(";")[index].split(",")[0]}\''''
                        where = where + f''' and {value.split(',')[1]} <= \'{conditionValue.split(";")[index].split(",")[1]}\''''
                    else:
                        where = where + f''' and {value} = \'{conditionValue.split(";")[index]}\''''
            req_dict = request.session.get("req_dict")
            statistics_func = "SUM"
            func_params = req_dict.get("func")
            if func_params == "平均":
                statistics_func = "AVG"
            elif func_params == "最大":
                statistics_func = "MAX"
            elif func_params == "最小":
                statistics_func = "MIN"
            elif func_params == "总和":
                statistics_func = "COUNT"
            try:
                del req_dict["func"]
            except:
                pass
            #定义查询统计语句
            for key, value in req_dict.items():
                if key!="limit" and key!="order" and key!="orderType" and key!="conditionColumn"and key!="conditionValue":
                    where = where + " and {0} ='{1}' ".format(key,value)
            sql = ''
            if timeStatType == '日':
                sql = "SELECT DATE_FORMAT({0}, '%Y-%m-%d') {0}, ROUND({1}({2}),2) total FROM T_Sentiment_Analysis {3} GROUP BY DATE_FORMAT({0}, '%Y-%m-%d')".format(xColumnName, statistics_func,yColumnName, where, '%Y-%m-%d')

            if timeStatType == '月':
                sql = "SELECT DATE_FORMAT({0}, '%Y-%m') {0}, ROUND({1}({2}),2) total FROM T_Sentiment_Analysis {3} GROUP BY DATE_FORMAT({0}, '%Y-%m')".format(xColumnName, statistics_func,yColumnName, where, '%Y-%m')

            if timeStatType == '季':
                sql = "SELECT CONCAT(YEAR(MIN({0})), '-Q', QUARTER(MIN({0}))) AS {0}, {1}({2}) AS total FROM T_Sentiment_Analysis {3} GROUP BY YEAR({0}), QUARTER({0})".format(xColumnName,statistics_func, yColumnName, where)

            if timeStatType == '年':
                sql = "SELECT DATE_FORMAT({0}, '%Y') {0}, ROUND({1}({2}),2) total FROM T_Sentiment_Analysis {3} GROUP BY DATE_FORMAT({0}, '%Y')".format(xColumnName,statistics_func, yColumnName, where, '%Y')
            L = []
            cursor = connection.cursor()
            cursor.execute(sql)
            desc = cursor.description
            data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
            for online_dict in data_dict:
                for key in online_dict:
                    if 'datetime.datetime' in str(type(online_dict[key])):
                        online_dict[key] = online_dict[key].strftime(
                            "%Y-%m-%d %H:%M:%S")
                    else:
                        pass
                L.append(online_dict)
            msg['data'] = L
        req_dict = request.session.get("req_dict")
        #对结果进行排序
        order = req_dict.get('order')
        orderType = req_dict.get('orderType')
        if orderType=='x' :
            if order == "desc":
                msg['data'] = order_time(msg['data'], timeStatType, xColumnName, True)
            else:
                msg['data'] = order_time(msg['data'], timeStatType, xColumnName, False)
        else:
            if order == "desc":
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None), key=lambda x: x['total'],
                                     reverse=True)
            else:
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None), key=lambda x: x['total'])

        if "limit" in req_dict and int(req_dict["limit"]) < len(L):
            msg['data'] = msg['data'][:int(req_dict["limit"])]
        return JsonResponse(msg, encoder=CustomJsonEncoder)

# 按值统计
def qingganfenxi_o_value(request, xColumnName, yColumnName):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}
        #获取hadoop分析后的数据文件
        json_filename = f'qingganfenxi_value{xColumnName}{yColumnName}.json'

        if os.path.exists(json_filename) == True:
            with open(json_filename, encoding='utf-8') as f:
                msg['data'] = json.load(f)
        else:
            where = ' where 1 = 1 '
            raw_query_string = request.META.get('QUERY_STRING', '')
            raw_query_string = unquote(raw_query_string)
            conditionColumn = ""
            conditionValue = ""
            if "conditionColumn=" in raw_query_string:
                conditionColumn = raw_query_string.split("conditionColumn=")[1].split("&")[0]
            if "conditionValue=" in raw_query_string:
                conditionValue = raw_query_string.split("conditionValue=")[1].split("&")[0]
            if conditionColumn != "":
                for index, value in enumerate(conditionColumn.split(";")):
                    if "," in value:
                        where = where + f''' and {value.split(',')[0]} >= \'{conditionValue.split(";")[index].split(",")[0]}\''''
                        where = where + f''' and {value.split(',')[1]} <= \'{conditionValue.split(";")[index].split(",")[1]}\''''
                    else:
                        where = where + f''' and {value} = \'{conditionValue.split(";")[index]}\''''
            req_dict = request.session.get("req_dict")
            statistics_func = "SUM"
            func_params = req_dict.get("func")
            if func_params == "平均":
                statistics_func = "AVG"
            elif func_params == "最大":
                statistics_func = "MAX"
            elif func_params == "最小":
                statistics_func = "MIN"
            elif func_params == "总和":
                statistics_func = "COUNT"
            try:
                del req_dict["func"]
            except:
                pass
            sql = "SELECT {0}, ROUND({1}({2}),2) AS total FROM T_Sentiment_Analysis {3} GROUP BY {0}".format(xColumnName,statistics_func, yColumnName, where)
            L = []
            cursor = connection.cursor()
            cursor.execute(sql)
            desc = cursor.description
            data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
            for online_dict in data_dict:
                for key in online_dict:
                    if 'datetime.datetime' in str(type(online_dict[key])):
                        online_dict[key] = online_dict[key].strftime(
                            "%Y-%m-%d %H:%M:%S")
                    else:
                        pass
                L.append(online_dict)
            msg['data'] = L
        req_dict = request.session.get("req_dict")
        if "order" in req_dict:
            order = req_dict["order"]
            if order == "desc":
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None),key=lambda x: x['total'],reverse=True)
            else:
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None),key=lambda x: x['total'])

        if "limit" in req_dict and int(req_dict["limit"]) < len(L):
            msg['data'] = msg['data'][:int(req_dict["limit"])]
        return JsonResponse(msg, encoder=CustomJsonEncoder)

# （按值统计）时间统计类型(多)
def qingganfenxi_valueMul(request, xColumnName, timeStatType):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": []}
        req_dict = request.session.get("req_dict") or {}
        y_column_names = _safe_y_column_names(req_dict)
        if not y_column_names:
            return JsonResponse(msg, encoder=CustomJsonEncoder)
        #获取hadoop分析后的数据文件
        date_type = ""
        if timeStatType == '日':
            date_type = "date"
        if timeStatType == '月':
            date_type = "month"
        if timeStatType == '季':
            date_type = "quarter"
        if timeStatType == '年':
            date_type = "year"
        #获取hadoop分析后的数据文件
        json_filename = f'''qingganfenxi_value{xColumnName}{_safe_y_column_filename(req_dict)}{date_type}.json'''

        if os.path.exists(json_filename) == True:
            with open(json_filename, encoding='utf-8') as f:
                msg['data'] = json.load(f)
        else:
            where = ' where 1 = 1 '
            raw_query_string = request.META.get('QUERY_STRING', '')
            raw_query_string = unquote(raw_query_string)
            conditionColumn = ""
            conditionValue = ""
            if "conditionColumn=" in raw_query_string:
                conditionColumn = raw_query_string.split("conditionColumn=")[1].split("&")[0]
            if "conditionValue=" in raw_query_string:
                conditionValue = raw_query_string.split("conditionValue=")[1].split("&")[0]
            if conditionColumn != "":
                for index, value in enumerate(conditionColumn.split(";")):
                    if "," in value:
                        where = where + f''' and {value.split(',')[0]} >= \'{conditionValue.split(";")[index].split(",")[0]}\''''
                        where = where + f''' and {value.split(',')[1]} <= \'{conditionValue.split(";")[index].split(",")[1]}\''''
                    else:
                        where = where + f''' and {value} = \'{conditionValue.split(";")[index]}\''''

            statistics_func = "SUM"
            func_params = req_dict.get("func")
            if func_params == "平均":
                statistics_func = "AVG"
            elif func_params == "最大":
                statistics_func = "MAX"
            elif func_params == "最小":
                statistics_func = "MIN"
            elif func_params == "总和":
                statistics_func = "COUNT"
            try:
                del req_dict["func"]
            except:
                pass
              # 定义查询统计语句
            for key, value in req_dict.items():
                if key != "limit" and key != "order" and key != "orderType" and key != "yColumnNameMul" and key != "conditionColumn" and key != "conditionValue":
                    where = where + " and {0} ='{1}' ".format(key, value)

            for item in y_column_names:
                sql = ''
                if timeStatType == '日':
                    sql = "SELECT DATE_FORMAT({0}, '%Y-%m-%d') {0}, ROUND({1}({2}),2) total FROM T_Sentiment_Analysis {3} GROUP BY DATE_FORMAT({0}, '%Y-%m-%d')".format(xColumnName, statistics_func,item, where, '%Y-%m-%d')

                if timeStatType == '月':
                    sql = "SELECT DATE_FORMAT({0}, '%Y-%m') {0}, ROUND({1}({2}),2) total FROM T_Sentiment_Analysis {3} GROUP BY DATE_FORMAT({0}, '%Y-%m')".format(xColumnName,statistics_func, item, where, '%Y-%m')

                if timeStatType == '季':
                    sql = "SELECT CONCAT(YEAR(MIN({0})), '-Q', QUARTER(MIN({0}))) {0}, {1}({2}) total FROM T_Sentiment_Analysis {3} GROUP BY YEAR({0}), QUARTER({0})".format(xColumnName, statistics_func,item, where)

                if timeStatType == '年':
                    sql = "SELECT DATE_FORMAT({0}, '%Y') {0}, ROUND({1}({2}),2) total FROM T_Sentiment_Analysis {3} GROUP BY DATE_FORMAT({0}, '%Y')".format(xColumnName, statistics_func,item, where, '%Y')

                L = []
                cursor = connection.cursor()
                cursor.execute(sql)
                desc = cursor.description
                data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
                for online_dict in data_dict:
                    for key in online_dict:
                        if 'datetime.datetime' in str(type(online_dict[key])):
                            online_dict[key] = online_dict[key].strftime(
                                "%Y-%m-%d %H:%M:%S")
                        else:
                            pass
                    L.append(online_dict)
                    # 结果进行排序
                    order = req_dict.get('order')
                    orderType = req_dict.get('orderType')
                    if orderType == 'x':
                        if order == "desc":
                            L = order_time(L, timeStatType, xColumnName, True)
                        else:
                            L = order_time(L, timeStatType, xColumnName, False)
                    else:
                        if order == "desc":
                            L = sorted((x for x in L if x['total'] is not None),
                                       key=lambda x: x['total'],
                                       reverse=True)
                        else:
                            L = sorted((x for x in L if x['total'] is not None),
                                       key=lambda x: x['total'])
                    # 截取列表个数
                    if "limit" in req_dict and int(req_dict["limit"]) < len(msg['data']):
                        L = L[:int(req_dict["limit"])]
                msg['data'].append(L)
        return JsonResponse(msg, encoder=CustomJsonEncoder)

# （按值统计(多)）
def qingganfenxi_o_valueMul(request, xColumnName):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": []}

        req_dict = request.session.get("req_dict") or {}
        y_column_names = _safe_y_column_names(req_dict)
        if not y_column_names:
            return JsonResponse(msg, encoder=CustomJsonEncoder)
        #获取hadoop分析后的数据文件
        json_filename = f'''qingganfenxi_value{xColumnName}{_safe_y_column_filename(req_dict)}.json'''

        if os.path.exists(json_filename) == True:
            with open(json_filename, encoding='utf-8') as f:
                msg['data'] = json.load(f)
        else:
            where = ' where 1 = 1 '
            raw_query_string = request.META.get('QUERY_STRING', '')
            raw_query_string = unquote(raw_query_string)
            conditionColumn = ""
            conditionValue = ""
            if "conditionColumn=" in raw_query_string:
                conditionColumn = raw_query_string.split("conditionColumn=")[1].split("&")[0]
            if "conditionValue=" in raw_query_string:
                conditionValue = raw_query_string.split("conditionValue=")[1].split("&")[0]
            if conditionColumn != "":
                for index, value in enumerate(conditionColumn.split(";")):
                    if "," in value:
                        where = where + f''' and {value.split(',')[0]} >= \'{conditionValue.split(";")[index].split(",")[0]}\''''
                        where = where + f''' and {value.split(',')[0]} <= \'{conditionValue.split(";")[index].split(",")[1]}\''''
                    else:
                        where = where + f''' and {value} = \'{conditionValue.split(";")[index]}\''''
            statistics_func = "SUM"
            func_params = req_dict.get("func")
            if func_params == "平均":
                statistics_func = "AVG"
            elif func_params == "最大":
                statistics_func = "MAX"
            elif func_params == "最小":
                statistics_func = "MIN"
            elif func_params == "总和":
                statistics_func = "COUNT"
            try:
                del req_dict["func"]
            except:
                pass
            for item in y_column_names:
                sql = "SELECT {0}, ROUND({1}({2}),2) AS total FROM T_Sentiment_Analysis {3} GROUP BY {0}".format(xColumnName, statistics_func,item, where)
                L = []
                cursor = connection.cursor()
                cursor.execute(sql)
                desc = cursor.description
                data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
                for online_dict in data_dict:
                    for key in online_dict:
                        if 'datetime.datetime' in str(type(online_dict[key])):
                            online_dict[key] = online_dict[key].strftime(
                                "%Y-%m-%d %H:%M:%S")
                        else:
                            pass
                    L.append(online_dict)
                msg['data'].append(L)
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def qingganfenxi_group(request, columnName):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}

        #获取hadoop分析后的数据文件
        json_filename = f'qingganfenxi_group{columnName}.json'

        if os.path.exists(json_filename) == True:
            with open(json_filename, encoding='utf-8') as f:
                msg['data'] = json.load(f)
        else:
            where = ' where 1 = 1 '
            raw_query_string = request.META.get('QUERY_STRING', '')
            raw_query_string = unquote(raw_query_string)
            conditionColumn = ""
            conditionValue = ""
            if "conditionColumn=" in raw_query_string:
                conditionColumn = raw_query_string.split("conditionColumn=")[1].split("&")[0]
            if "conditionValue=" in raw_query_string:
                conditionValue = raw_query_string.split("conditionValue=")[1].split("&")[0]
            if conditionColumn != "":
                for index, value in enumerate(conditionColumn.split(";")):
                    if ',' in value:
                        where = where + f''' and {value.split(',')[0]} >= \'{conditionValue.split(";")[index].split(",")[0]}\''''
                        where = where + f''' and {value.split(',')[1]} <= \'{conditionValue.split(";")[index].split(",")[1]}\''''
                    else:
                        where = where + f''' and {value} = \'{conditionValue.split(";")[index]}\''''

            sql = "SELECT COUNT(*) AS total, " + columnName + " FROM T_Sentiment_Analysis " + where + " GROUP BY " + columnName
            L = []
            cursor = connection.cursor()
            cursor.execute(sql)
            desc = cursor.description
            data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
            for online_dict in data_dict:
                for key in online_dict:
                    if 'datetime.datetime' in str(type(online_dict[key])):
                        online_dict[key] = online_dict[key].strftime("%Y-%m-%d")
                    else:
                        pass
                L.append(online_dict)
            msg['data'] = L
        req_dict = request.session.get("req_dict")
        if "order" in req_dict:
            order = req_dict["order"]
            if order == "desc":
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None),key=lambda x: x['total'],reverse=True)
            else:
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None),key=lambda x: x['total'])

        if "limit" in req_dict and int(req_dict["limit"]) < len(L):
            msg['data'] = msg['data'][:int(req_dict["limit"])]
        return JsonResponse(msg, encoder=CustomJsonEncoder)


def qingganfenxi_batchAnalyze(request):
    '''
    Batch-build sentiment analysis rows from imported attraction reviews.
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict") or {}
        limit = req_dict.get("limit")
        dry_run = str(req_dict.get("dryRun") or req_dict.get("dry_run") or "").lower() in ["1", "true", "yes"]
        deduplicate = str(req_dict.get("deduplicate") or "").lower() in ["1", "true", "yes"]
        if dry_run:
            msg["data"] = preview_sentiment_results_from_reviews()
        else:
            msg["data"] = build_sentiment_results_from_reviews(limit=limit, deduplicate=deduplicate)
        return JsonResponse(msg, encoder=CustomJsonEncoder)



def qingganfenxi_baidu_sa(request):
    '''
    百度情感倾向分析接口1
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "data": ""}
        req_dict = request.session.get("req_dict")
        text = req_dict.get("text")
        bdb = BaiDuBce()
        info = bdb.sentiment_classify(text)
        msg['data'] = info
        return JsonResponse(msg)






