# coding:utf-8
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum
from django.db import connection
from util.codes import normal_code, other_code
from util.CustomJSONEncoder import CustomJsonEncoder
from .models import ctripjd, qingganfenxi


def to_float(value, default=0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def to_int(value, default=0):
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def has_price(value):
    return value is not None and value != ""


def normalize(value, max_value):
    if not max_value:
        return 0
    return value / max_value


def table_exists(table_name):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE %s", [table_name])
            return cursor.fetchone() is not None
    except Exception:
        return False


def source_distribution():
    if not table_exists("T_Raw_Platform_Spot"):
        return []
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT source_platform, COUNT(*) AS total "
            "FROM T_Raw_Platform_Spot "
            "GROUP BY source_platform "
            "ORDER BY total DESC"
        )
        return [
            {"source_platform": row[0] or "unknown", "total": row[1]}
            for row in cursor.fetchall()
        ]


def decision_summary(request):
    """
    旅游数据分析与辅助决策接口
    """
    if request.method not in ["GET", "POST"]:
        return JsonResponse({"code": other_code, "msg": "请求方式错误"})

    try:
        scenic_list = list(
            ctripjd.objects.all().values(
                "id",
                "poiname",
                "commentscore",
                "commentcount",
                "heatscore",
                "jiage",
                "districtname",
                "imgurl",
            )
        )

        max_comment = max([to_int(i.get("commentcount")) for i in scenic_list] or [1])
        max_heat = max([to_float(i.get("heatscore")) for i in scenic_list] or [1])
        prices = [to_float(i.get("jiage")) for i in scenic_list if has_price(i.get("jiage"))]
        max_price = max(prices or [1]) or 1
        avg_price = sum(prices) / len(prices) if prices else 0

        for item in scenic_list:
            score = to_float(item.get("commentscore"))
            heat = to_float(item.get("heatscore"))
            comment = to_int(item.get("commentcount"))
            price = to_float(item.get("jiage"))

            score_part = score * 20
            heat_part = normalize(heat, max_heat) * 100
            comment_part = normalize(comment, max_comment) * 100
            price_part = (1 - normalize(price, max_price)) * 100 if has_price(item.get("jiage")) else 60

            item["decision_score"] = round(
                score_part * 0.4 + heat_part * 0.3 + comment_part * 0.2 + price_part * 0.1,
                2,
            )

        recommend_top = sorted(
            scenic_list,
            key=lambda x: x["decision_score"],
            reverse=True,
        )[:10]

        value_top = sorted(
            [
                i for i in scenic_list
                if to_float(i.get("commentscore")) >= 4.2 and has_price(i.get("jiage"))
            ],
            key=lambda x: (
                to_float(x.get("commentscore")) * 20 * 0.7
                + (100 - normalize(to_float(x.get("jiage")), max_price) * 100) * 0.3
            ),
            reverse=True,
        )[:10]

        warning_items = sorted(
            [
                i for i in scenic_list
                if to_float(i.get("jiage")) > avg_price and to_float(i.get("commentscore")) < 4.2
            ],
            key=lambda x: to_float(x.get("jiage")),
            reverse=True,
        )[:10]

        hot_top = sorted(
            scenic_list,
            key=lambda x: to_float(x.get("heatscore")),
            reverse=True,
        )[:10]

        district_data = list(
            ctripjd.objects.values("districtname")
            .annotate(
                total=Count("id"),
                avg_score=Avg("commentscore"),
                avg_heat=Avg("heatscore"),
                total_comment=Sum("commentcount"),
            )
            .order_by("-total")[:10]
        )

        sentiment_data = list(
            qingganfenxi.objects.values("fenxijieguo")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        source_data = source_distribution()

        avg_score = ctripjd.objects.aggregate(value=Avg("commentscore")).get("value") or 0
        avg_heat = ctripjd.objects.aggregate(value=Avg("heatscore")).get("value") or 0

        messages = []
        if recommend_top:
            names = "、".join([i.get("poiname") for i in recommend_top[:3] if i.get("poiname")])
            messages.append("综合评分较高的景点为{}，可作为游客优先推荐对象。".format(names))

        if value_top:
            names = "、".join([i.get("poiname") for i in value_top[:3] if i.get("poiname")])
            messages.append("从评分与价格综合比较看，{}性价比较高，适合预算敏感型游客。".format(names))

        if district_data:
            top_city = district_data[0].get("districtname") or "未知地区"
            messages.append("{}景点数量较多、热度集中，可作为重点旅游推荐区域。".format(top_city))

        if warning_items:
            names = "、".join([i.get("poiname") for i in warning_items[:3] if i.get("poiname")])
            messages.append("{}存在价格较高但评分偏低的情况，建议重点关注服务质量和游客反馈。".format(names))

        msg = {
            "code": normal_code,
            "msg": "成功",
            "data": {
                "summary": {
                    "scenicCount": len(scenic_list),
                    "sourceCount": len(source_data) or 1,
                    "avgScore": round(to_float(avg_score), 2),
                    "avgHeat": round(to_float(avg_heat), 2),
                    "avgPrice": round(avg_price, 2),
                },
                "charts": {
                    "hotTop": hot_top,
                    "districts": district_data,
                    "sentiments": sentiment_data,
                    "sources": source_data,
                },
                "decisions": {
                    "recommendTop": recommend_top,
                    "valueTop": value_top,
                    "warningItems": warning_items,
                    "messages": messages,
                },
            },
        }
        return JsonResponse(msg, encoder=CustomJsonEncoder)

    except Exception as e:
        return JsonResponse({"code": other_code, "msg": str(e)})
