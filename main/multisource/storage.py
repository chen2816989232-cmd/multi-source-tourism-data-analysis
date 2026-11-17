# coding:utf-8
import json
import time
from datetime import datetime

from django.db import connection, transaction

from .normalizer import clean_text


_TABLE_EXISTS_CACHE = {}
_TABLE_COLUMNS_CACHE = {}
_LAST_ID = 0


RAW_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS T_Raw_Platform_Spot (
  id BIGINT NOT NULL PRIMARY KEY,
  source_platform VARCHAR(50) NOT NULL,
  source_id VARCHAR(255) DEFAULT NULL,
  source_url TEXT,
  poiname VARCHAR(255) DEFAULT NULL,
  standard_name VARCHAR(255) DEFAULT NULL,
  districtname VARCHAR(255) DEFAULT NULL,
  address VARCHAR(255) DEFAULT NULL,
  longitude VARCHAR(50) DEFAULT NULL,
  latitude VARCHAR(50) DEFAULT NULL,
  commentscore DOUBLE DEFAULT NULL,
  commentcount INT DEFAULT NULL,
  heatscore DOUBLE DEFAULT NULL,
  jiage DOUBLE DEFAULT NULL,
  crawl_time DATETIME DEFAULT NULL,
  raw_json LONGTEXT,
  data_status VARCHAR(50) DEFAULT 'normal',
  KEY idx_raw_source (source_platform, source_id),
  KEY idx_raw_name_city (standard_name, districtname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""


CTRIPJD_EXTENSIONS = {
    "source_platform": "VARCHAR(100) DEFAULT 'ctrip'",
    "source_id": "VARCHAR(255) DEFAULT NULL",
    "source_url": "TEXT",
    "standard_name": "VARCHAR(255) DEFAULT NULL",
    "source_count": "INT DEFAULT 1",
    "longitude": "VARCHAR(50) DEFAULT NULL",
    "latitude": "VARCHAR(50) DEFAULT NULL",
    "raw_json": "LONGTEXT",
    "data_status": "VARCHAR(50) DEFAULT 'normal'",
}


CTRIPJD_BASE_COLUMNS = [
    "poiname",
    "imgurl",
    "commentscore",
    "commentcount",
    "heatscore",
    "jiage",
    "districtname",
    "zonename",
    "sightcategoryinfo",
    "tagname",
    "shortfeatures",
    "distancestr",
    "othertaglist",
    "detailurl",
]


def make_id():
    global _LAST_ID
    candidate = int(time.time() * 1000000)
    if candidate <= _LAST_ID:
        candidate = _LAST_ID + 1
    _LAST_ID = candidate
    return candidate


def clear_schema_cache():
    _TABLE_EXISTS_CACHE.clear()
    _TABLE_COLUMNS_CACHE.clear()


def table_exists(table_name):
    if table_name in _TABLE_EXISTS_CACHE:
        return _TABLE_EXISTS_CACHE[table_name]
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE %s", [table_name])
        exists = cursor.fetchone() is not None
    _TABLE_EXISTS_CACHE[table_name] = exists
    return exists


def table_columns(table_name):
    if table_name in _TABLE_COLUMNS_CACHE:
        return _TABLE_COLUMNS_CACHE[table_name]
    if not table_exists(table_name):
        return set()
    with connection.cursor() as cursor:
        cursor.execute("SHOW COLUMNS FROM `{}`".format(table_name))
        columns = {row[0] for row in cursor.fetchall()}
    _TABLE_COLUMNS_CACHE[table_name] = columns
    return columns


def ensure_multisource_schema():
    clear_schema_cache()
    with connection.cursor() as cursor:
        cursor.execute(RAW_TABLE_SQL)

    clear_schema_cache()
    existing = table_columns("T_Core_attractions")
    with connection.cursor() as cursor:
        for column, ddl in CTRIPJD_EXTENSIONS.items():
            if column not in existing:
                cursor.execute("ALTER TABLE T_Core_attractions ADD COLUMN `{}` {}".format(column, ddl))

        clear_schema_cache()
        if "standard_name" in table_columns("T_Core_attractions"):
            cursor.execute(
                "UPDATE T_Core_attractions SET source_platform='ctrip' "
                "WHERE source_platform IS NULL OR source_platform=''"
            )
            cursor.execute(
                "UPDATE T_Core_attractions SET standard_name=LOWER(poiname) "
                "WHERE (standard_name IS NULL OR standard_name='') AND poiname IS NOT NULL"
            )


def filter_columns(table_name, record):
    columns = table_columns(table_name)
    return {key: value for key, value in record.items() if key in columns}


def execute_insert(table_name, record):
    record = filter_columns(table_name, record)
    if not record:
        return None
    names = list(record.keys())
    placeholders = ["%s"] * len(names)
    sql = "INSERT INTO `{}` ({}) VALUES ({})".format(
        table_name,
        ",".join("`{}`".format(name) for name in names),
        ",".join(placeholders),
    )
    with connection.cursor() as cursor:
        cursor.execute(sql, [record[name] for name in names])
    return record.get("id")


def execute_bulk_insert(table_name, records):
    if not records:
        return 0
    columns = table_columns(table_name)
    names = [name for name in records[0].keys() if name in columns]
    if not names:
        return 0
    placeholders = ["%s"] * len(names)
    sql = "INSERT INTO `{}` ({}) VALUES ({})".format(
        table_name,
        ",".join("`{}`".format(name) for name in names),
        ",".join(placeholders),
    )
    values = [[record.get(name) for name in names] for record in records]
    with connection.cursor() as cursor:
        cursor.executemany(sql, values)
    return len(records)


def execute_update(table_name, record_id, values):
    values = filter_columns(table_name, values)
    values.pop("id", None)
    if not values:
        return
    sql = "UPDATE `{}` SET {} WHERE id=%s".format(
        table_name,
        ",".join("`{}`=%s".format(name) for name in values.keys()),
    )
    with connection.cursor() as cursor:
        cursor.execute(sql, list(values.values()) + [record_id])


def find_raw_record(record):
    platform = record.get("source_platform")
    source_id = record.get("source_id")
    if not platform or not source_id or not table_exists("T_Raw_Platform_Spot"):
        return None
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM T_Raw_Platform_Spot "
            "WHERE source_platform=%s AND source_id=%s LIMIT 1",
            [platform, source_id],
        )
        row = cursor.fetchone()
        return row[0] if row else None


def find_unified_spot(record):
    columns = table_columns("T_Core_attractions")
    standard_name = record.get("standard_name")
    districtname = record.get("districtname")
    source_url = record.get("source_url") or record.get("detailurl")

    with connection.cursor() as cursor:
        if "source_platform" in columns and record.get("source_platform") and record.get("source_id"):
            cursor.execute(
                "SELECT id FROM T_Core_attractions WHERE source_platform=%s AND source_id=%s LIMIT 1",
                [record.get("source_platform"), record.get("source_id")],
            )
            row = cursor.fetchone()
            if row:
                return row[0]

        if standard_name and districtname and "standard_name" in columns:
            cursor.execute(
                "SELECT id FROM T_Core_attractions WHERE standard_name=%s AND districtname=%s LIMIT 1",
                [standard_name, districtname],
            )
            row = cursor.fetchone()
            if row:
                return row[0]

        if source_url:
            cursor.execute("SELECT id FROM T_Core_attractions WHERE detailurl=%s LIMIT 1", [source_url])
            row = cursor.fetchone()
            if row:
                return row[0]

        if record.get("poiname") and districtname:
            cursor.execute(
                "SELECT id FROM T_Core_attractions WHERE poiname=%s AND districtname=%s LIMIT 1",
                [record.get("poiname"), districtname],
            )
            row = cursor.fetchone()
            if row:
                return row[0]

    return None


def build_ctripjd_record(record):
    data = {key: record.get(key) for key in CTRIPJD_BASE_COLUMNS}
    data.update({
        "id": make_id(),
        "source_platform": record.get("source_platform"),
        "source_id": record.get("source_id"),
        "source_url": record.get("source_url"),
        "standard_name": record.get("standard_name"),
        "source_count": 1,
        "longitude": record.get("longitude"),
        "latitude": record.get("latitude"),
        "raw_json": record.get("raw_json"),
        "data_status": record.get("data_status") or "normal",
    })
    return data


def build_raw_record(record):
    return {
        "id": make_id(),
        "source_platform": record.get("source_platform"),
        "source_id": record.get("source_id"),
        "source_url": record.get("source_url"),
        "poiname": record.get("poiname"),
        "standard_name": record.get("standard_name"),
        "districtname": record.get("districtname"),
        "address": record.get("address") or record.get("zonename"),
        "longitude": record.get("longitude"),
        "latitude": record.get("latitude"),
        "commentscore": record.get("commentscore"),
        "commentcount": record.get("commentcount"),
        "heatscore": record.get("heatscore"),
        "jiage": record.get("jiage"),
        "crawl_time": record.get("crawl_time") or datetime.now(),
        "raw_json": record.get("raw_json") or json.dumps(record, ensure_ascii=False),
        "data_status": record.get("data_status") or "normal",
    }


def merge_unified_values(existing_id, record):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT commentscore, commentcount, heatscore, jiage, source_platform, source_count "
            "FROM T_Core_attractions WHERE id=%s",
            [existing_id],
        )
        row = cursor.fetchone()

    if not row:
        return

    old_score, old_comment, old_heat, old_price, old_sources, old_count = row
    new_source = clean_text(record.get("source_platform"))
    source_set = set(filter(None, clean_text(old_sources).split(",")))
    if new_source:
        source_set.add(new_source)

    update_values = {
        "source_platform": ",".join(sorted(source_set)) if source_set else old_sources,
        "source_count": max(int(old_count or 1), len(source_set) or 1),
        "source_url": record.get("source_url"),
        "raw_json": record.get("raw_json"),
    }

    if old_score in (None, 0) and record.get("commentscore") is not None:
        update_values["commentscore"] = record.get("commentscore")
    if old_comment in (None, 0) and record.get("commentcount") is not None:
        update_values["commentcount"] = record.get("commentcount")
    if old_heat in (None, 0) and record.get("heatscore") is not None:
        update_values["heatscore"] = record.get("heatscore")
    if old_price in (None, 0) and record.get("jiage") is not None:
        update_values["jiage"] = record.get("jiage")
    if record.get("longitude"):
        update_values["longitude"] = record.get("longitude")
    if record.get("latitude"):
        update_values["latitude"] = record.get("latitude")

    execute_update("T_Core_attractions", existing_id, update_values)


@transaction.atomic
def save_spot(record, ensure_schema=True):
    if not record.get("poiname"):
        return {"status": "skip", "reason": "empty poiname"}

    if ensure_schema:
        ensure_multisource_schema()

    raw_id = find_raw_record(record)
    if raw_id:
        execute_update("T_Raw_Platform_Spot", raw_id, build_raw_record(record))
    else:
        raw_id = execute_insert("T_Raw_Platform_Spot", build_raw_record(record))

    unified_id = find_unified_spot(record)
    if unified_id:
        merge_unified_values(unified_id, record)
        return {"status": "merged", "raw_id": raw_id, "unified_id": unified_id}

    unified_id = execute_insert("T_Core_attractions", build_ctripjd_record(record))
    return {"status": "inserted", "raw_id": raw_id, "unified_id": unified_id}


def save_spots(records):
    ensure_multisource_schema()
    stats = {"inserted": 0, "merged": 0, "skip": 0, "error": 0}
    errors = []
    with transaction.atomic():
        for record in records:
            try:
                result = save_spot(record, ensure_schema=False)
                stats[result["status"]] = stats.get(result["status"], 0) + 1
            except Exception as exc:
                stats["error"] += 1
                errors.append({"poiname": record.get("poiname"), "error": str(exc)})
    return stats, errors


def bulk_insert_new_spots(records, chunk_size=500):
    ensure_multisource_schema()
    stats = {"inserted": 0, "merged": 0, "skip": 0, "error": 0}
    errors = []
    for index in range(0, len(records), chunk_size):
        chunk = records[index:index + chunk_size]
        raw_records = [build_raw_record(record) for record in chunk]
        unified_records = [build_ctripjd_record(record) for record in chunk]
        try:
            with transaction.atomic():
                execute_bulk_insert("T_Raw_Platform_Spot", raw_records)
                execute_bulk_insert("T_Core_attractions", unified_records)
            stats["inserted"] += len(chunk)
        except Exception:
            for record in chunk:
                try:
                    with transaction.atomic():
                        execute_insert("T_Raw_Platform_Spot", build_raw_record(record))
                        execute_insert("T_Core_attractions", build_ctripjd_record(record))
                    stats["inserted"] += 1
                except Exception as exc:
                    stats["error"] += 1
                    errors.append({"poiname": record.get("poiname"), "error": str(exc)})
    return stats, errors
