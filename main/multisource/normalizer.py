# coding:utf-8
import json
import re
from datetime import datetime


def clean_text(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def to_float(value, default=None):
    if value is None or value == "":
        return default
    try:
        match = re.search(r"-?\d+(\.\d+)?", str(value))
        return float(match.group(0)) if match else default
    except Exception:
        return default


def to_int(value, default=None):
    number = to_float(value, None)
    return int(number) if number is not None else default


def normalize_name(value):
    value = clean_text(value)
    value = re.sub(r"[\(\[（【].*?[\)\]）】]", "", value)
    value = re.sub(r"(景区|风景区|旅游区|公园)$", "", value)
    return value.strip().lower()


def split_location(location):
    if not location:
        return "", ""
    parts = str(location).split(",")
    if len(parts) != 2:
        return "", ""
    return parts[0].strip(), parts[1].strip()


def first_photo_url(poi):
    photos = poi.get("photos") or []
    if isinstance(photos, list) and photos:
        return photos[0].get("url") or ""
    return ""


def amap_uri(name, location):
    if not location:
        return ""
    return "https://uri.amap.com/marker?position={}&name={}".format(location, clean_text(name))


def normalize_amap_poi(poi):
    biz_ext = poi.get("biz_ext") or {}
    rating = to_float(biz_ext.get("rating"), None)
    cost = to_float(biz_ext.get("cost"), None)
    location = poi.get("location") or ""
    longitude, latitude = split_location(location)
    name = clean_text(poi.get("name"))
    city = clean_text(poi.get("cityname") or poi.get("pname") or poi.get("adname"))

    return {
        "source_platform": "amap",
        "source_id": clean_text(poi.get("id")),
        "source_url": amap_uri(name, location),
        "poiname": name,
        "standard_name": normalize_name(name),
        "imgurl": first_photo_url(poi),
        "commentscore": rating,
        "commentcount": None,
        "heatscore": round(rating * 2, 2) if rating is not None else None,
        "jiage": cost,
        "districtname": city,
        "zonename": clean_text(poi.get("address")),
        "sightcategoryinfo": "",
        "tagname": clean_text(poi.get("type")),
        "shortfeatures": "",
        "distancestr": location,
        "othertaglist": clean_text(poi.get("typecode")),
        "detailurl": amap_uri(name, location),
        "longitude": longitude,
        "latitude": latitude,
        "address": clean_text(poi.get("address")),
        "crawl_time": datetime.now(),
        "raw_json": json.dumps(poi, ensure_ascii=False),
        "data_status": "normal",
    }


def normalize_csv_row(platform, row, mapping):
    def pick(name):
        source_key = mapping.get(name, name)
        return row.get(source_key)

    name = clean_text(pick("poiname"))
    city = clean_text(pick("districtname"))
    source_url = clean_text(pick("source_url") or pick("detailurl"))

    return {
        "source_platform": platform,
        "source_id": clean_text(pick("source_id") or source_url or name),
        "source_url": source_url,
        "poiname": name,
        "standard_name": normalize_name(name),
        "imgurl": clean_text(pick("imgurl")),
        "commentscore": to_float(pick("commentscore"), None),
        "commentcount": to_int(pick("commentcount"), None),
        "heatscore": to_float(pick("heatscore"), None),
        "jiage": to_float(pick("jiage"), None),
        "districtname": city,
        "zonename": clean_text(pick("zonename") or pick("address")),
        "sightcategoryinfo": clean_text(pick("sightcategoryinfo")),
        "tagname": clean_text(pick("tagname")),
        "shortfeatures": clean_text(pick("shortfeatures")),
        "distancestr": clean_text(pick("distancestr")),
        "othertaglist": clean_text(pick("othertaglist")),
        "detailurl": source_url,
        "longitude": clean_text(pick("longitude")),
        "latitude": clean_text(pick("latitude")),
        "address": clean_text(pick("address") or pick("zonename")),
        "crawl_time": datetime.now(),
        "raw_json": json.dumps(row, ensure_ascii=False),
        "data_status": "normal",
    }


def spot_key(record):
    return "{}|{}".format(
        normalize_name(record.get("poiname")),
        clean_text(record.get("districtname")).lower(),
    )

