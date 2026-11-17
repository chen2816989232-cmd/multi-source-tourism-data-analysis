# coding:utf-8
import csv
import hashlib
import json
import os
import re
from datetime import datetime
from urllib.parse import urlparse

from .normalizer import clean_text, normalize_name, to_float


PLATFORM = "qunar_travel_dataset"
EXPECTED_FIELDS = [
    "名字",
    "链接",
    "地址",
    "介绍",
    "开放时间",
    "图片链接",
    "评分",
    "建议游玩时间",
    "建议季节",
    "门票",
    "小贴士",
    "Page",
]


def trim(value, max_length=190):
    value = (clean_text(value) or "").replace("\xa0", " ")
    if len(value) <= max_length:
        return value
    return value[:max_length]


def display_name(value):
    value = clean_text(value)
    if not value:
        return ""
    match = re.match(r"^([\u4e00-\u9fff0-9·\-\(\)（）\s]+)", value)
    if match and re.search(r"[\u4e00-\u9fff]", match.group(1)):
        return clean_text(match.group(1))
    return value


def source_id_from_url(url, city, name):
    url = clean_text(url)
    if url:
        parsed = urlparse(url)
        last_part = parsed.path.rstrip("/").split("/")[-1]
        if last_part:
            return last_part
        return hashlib.md5(url.encode("utf-8")).hexdigest()
    raw_key = "{}|{}".format(city, name)
    return hashlib.md5(raw_key.encode("utf-8")).hexdigest()


def extract_address(value):
    text = clean_text(value)
    if not text:
        return ""
    match = re.search(r"地址[:：]\s*(.*?)(?:电话[:：]|官网[:：]|$)", text)
    if match:
        return trim(match.group(1))
    text = re.sub(r"(电话|官网)[:：].*$", "", text)
    return trim((text or "").replace("地址:", "").replace("地址：", ""))


def extract_min_price(value):
    text = clean_text(value)
    if not text:
        return None
    if "免费" in text or "免票" in text or "无需门票" in text:
        return 0.0
    prices = re.findall(r"[\u00a5\uffe5]\s*([0-9]+(?:\.[0-9]+)?)", text)
    if not prices:
        prices = re.findall(r"([0-9]+(?:\.[0-9]+)?)\s*元", text)
    if not prices:
        return None
    return min(float(price) for price in prices)


def build_other_tags(row):
    parts = []
    for label, field in [
        ("开放时间", "开放时间"),
        ("建议游玩", "建议游玩时间"),
        ("建议季节", "建议季节"),
    ]:
        value = clean_text(row.get(field))
        if value:
            parts.append("{}:{}".format(label, value))
    return trim("; ".join(parts))


def normalize_qunar_row(row, city):
    raw_name = clean_text(row.get("名字"))
    name = display_name(raw_name)
    source_url = clean_text(row.get("链接"))
    score = to_float(row.get("评分"), None)
    price = extract_min_price(row.get("门票"))
    raw_payload = dict(row)
    raw_payload.update({
        "_city": city,
        "_platform": PLATFORM,
        "_display_name": name,
        "_source_id": source_id_from_url(source_url, city, raw_name),
        "_price": price,
    })

    return {
        "source_platform": PLATFORM,
        "source_id": raw_payload["_source_id"],
        "source_url": source_url,
        "poiname": trim(name),
        "standard_name": normalize_name(name),
        "imgurl": clean_text(row.get("图片链接")),
        "commentscore": score,
        "commentcount": None,
        "heatscore": round(score * 2, 2) if score is not None else None,
        "jiage": price,
        "districtname": trim(city),
        "zonename": extract_address(row.get("地址")),
        "sightcategoryinfo": "去哪儿景点",
        "tagname": "去哪儿攻略",
        "shortfeatures": trim(row.get("介绍")),
        "distancestr": "",
        "othertaglist": build_other_tags(row),
        "detailurl": source_url,
        "longitude": "",
        "latitude": "",
        "address": extract_address(row.get("地址")),
        "crawl_time": datetime.now(),
        "raw_json": json.dumps(raw_payload, ensure_ascii=False),
        "data_status": "normal",
    }


def iter_csv_paths(folder_path, cities=None, limit_files=0):
    cities = {clean_text(city) for city in (cities or []) if clean_text(city)}
    paths = []
    for filename in sorted(os.listdir(folder_path)):
        if not filename.lower().endswith(".csv"):
            continue
        city = os.path.splitext(filename)[0]
        if cities and city not in cities:
            continue
        paths.append(os.path.join(folder_path, filename))
        if limit_files and len(paths) >= limit_files:
            break
    return paths


def read_qunar_travel_dataset(folder_path, encoding="utf-8-sig", cities=None, limit_files=0, limit_rows=0):
    if not os.path.isdir(folder_path):
        raise RuntimeError("Dataset folder not found: {}".format(folder_path))

    records = []
    seen_source_ids = set()
    summary = {
        "platform": PLATFORM,
        "folder": folder_path,
        "files": 0,
        "rows": 0,
        "records": 0,
        "duplicate_source_ids": 0,
        "empty_name": 0,
        "bad_files": [],
    }

    for path in iter_csv_paths(folder_path, cities=cities, limit_files=limit_files):
        city = os.path.splitext(os.path.basename(path))[0]
        summary["files"] += 1
        try:
            with open(path, "r", encoding=encoding, newline="") as file_obj:
                reader = csv.DictReader(file_obj)
                if reader.fieldnames != EXPECTED_FIELDS:
                    summary["bad_files"].append({
                        "file": path,
                        "fields": reader.fieldnames,
                    })
                    continue
                for row in reader:
                    summary["rows"] += 1
                    raw_name = clean_text(row.get("名字"))
                    if not raw_name:
                        summary["empty_name"] += 1
                        continue
                    record = normalize_qunar_row(row, city)
                    source_id = record.get("source_id")
                    if source_id in seen_source_ids:
                        summary["duplicate_source_ids"] += 1
                        continue
                    seen_source_ids.add(source_id)
                    records.append(record)
                    summary["records"] += 1
                    if limit_rows and len(records) >= limit_rows:
                        return records, summary
        except Exception as exc:
            summary["bad_files"].append({"file": path, "error": str(exc)})

    return records, summary
