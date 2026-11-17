# coding:utf-8
import argparse
import json
import os
import sys


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj2.settings")

import django  # noqa: E402

django.setup()

from main.multisource.amap_collector import crawl_amap_spots  # noqa: E402
from main.multisource.csv_importer import read_csv_spots  # noqa: E402
from main.multisource.public_page_collector import load_xpath_mapping, parse_public_spot_page  # noqa: E402
from main.multisource.qunar_travel_dataset_importer import read_qunar_travel_dataset  # noqa: E402
from main.multisource.storage import bulk_insert_new_spots, ensure_multisource_schema, save_spots  # noqa: E402
from django.db import connection  # noqa: E402


def command_init_db(_args):
    ensure_multisource_schema()
    print("multi-source schema ready")


def command_amap(args):
    api_key = args.key or os.environ.get("AMAP_KEY")
    if not api_key:
        raise RuntimeError("Please pass --key or set AMAP_KEY")
    records = crawl_amap_spots(
        api_key=api_key,
        keyword=args.keyword,
        city=args.city,
        max_page=args.max_page,
        sleep_seconds=args.sleep,
    )
    stats, errors = save_spots(records)
    print({"platform": "amap", "fetched": len(records), "stats": stats, "errors": errors[:5]})


def command_csv(args):
    records = read_csv_spots(args.path, platform=args.platform, encoding=args.encoding)
    stats, errors = save_spots(records)
    print({"platform": args.platform, "fetched": len(records), "stats": stats, "errors": errors[:5]})


def command_public_page(args):
    mapping = load_xpath_mapping(args.mapping)
    records = [
        parse_public_spot_page(url, args.platform, mapping, sleep_seconds=args.sleep)
        for url in args.url
    ]
    stats, errors = save_spots(records)
    print({"platform": args.platform, "fetched": len(records), "stats": stats, "errors": errors[:5]})


def filter_missing_raw_records(records, platform, chunk_size=500):
    if not records:
        return records
    ensure_multisource_schema()
    source_ids = [record.get("source_id") for record in records if record.get("source_id")]
    existing = set()
    with connection.cursor() as cursor:
        for index in range(0, len(source_ids), chunk_size):
            chunk = source_ids[index:index + chunk_size]
            placeholders = ",".join(["%s"] * len(chunk))
            cursor.execute(
                "SELECT source_id FROM T_Raw_Platform_Spot "
                "WHERE source_platform=%s AND source_id IN ({})".format(placeholders),
                [platform] + chunk,
            )
            existing.update(row[0] for row in cursor.fetchall())
    return [record for record in records if record.get("source_id") not in existing]


def command_qunar_travel_csv(args):
    records, summary = read_qunar_travel_dataset(
        args.path,
        encoding=args.encoding,
        cities=args.city,
        limit_files=args.limit_files,
        limit_rows=args.limit_rows,
    )
    if args.dry_run:
        payload = {
            "platform": summary["platform"],
            "summary": summary,
            "samples": records[:args.sample],
        }
        print(json.dumps(payload, ensure_ascii=False, default=str, indent=2))
        return

    if args.skip_existing_raw:
        before_count = len(records)
        records = filter_missing_raw_records(records, summary["platform"])
        summary["skipped_existing_raw"] = before_count - len(records)

    if args.bulk_insert_missing:
        before_count = len(records)
        records = filter_missing_raw_records(records, summary["platform"])
        summary["skipped_existing_raw"] = summary.get("skipped_existing_raw", 0) + before_count - len(records)
        stats, errors = bulk_insert_new_spots(records, chunk_size=args.chunk_size)
    else:
        stats, errors = save_spots(records)
    payload = {
        "platform": summary["platform"],
        "fetched": len(records),
        "summary": summary,
        "stats": stats,
        "errors": errors[:5],
    }
    print(json.dumps(payload, ensure_ascii=False, default=str, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(description="Collect and merge multi-source travel spot data.")
    sub = parser.add_subparsers(dest="command", required=True)

    init_db = sub.add_parser("init-db", help="Create raw table and add source columns.")
    init_db.set_defaults(func=command_init_db)

    amap = sub.add_parser("amap", help="Collect POI data from AMap official WebService API.")
    amap.add_argument("--key", default="")
    amap.add_argument("--keyword", required=True)
    amap.add_argument("--city", default="")
    amap.add_argument("--max-page", type=int, default=5)
    amap.add_argument("--sleep", type=float, default=1.0)
    amap.set_defaults(func=command_amap)

    csv_cmd = sub.add_parser("csv", help="Import normalized or mapped CSV data.")
    csv_cmd.add_argument("--platform", required=True)
    csv_cmd.add_argument("--path", required=True)
    csv_cmd.add_argument("--encoding", default="utf-8-sig")
    csv_cmd.set_defaults(func=command_csv)

    public_page = sub.add_parser("public-page", help="Fetch public pages only when robots.txt allows it.")
    public_page.add_argument("--platform", required=True)
    public_page.add_argument("--mapping", required=True)
    public_page.add_argument("--url", action="append", required=True)
    public_page.add_argument("--sleep", type=float, default=1.0)
    public_page.set_defaults(func=command_public_page)

    qunar_csv = sub.add_parser("qunar-travel-csv", help="Import Qunar travel city CSV dataset.")
    qunar_csv.add_argument("--path", required=True)
    qunar_csv.add_argument("--encoding", default="utf-8-sig")
    qunar_csv.add_argument("--city", action="append", default=[], help="Import one city; can be repeated.")
    qunar_csv.add_argument("--limit-files", type=int, default=0)
    qunar_csv.add_argument("--limit-rows", type=int, default=0)
    qunar_csv.add_argument("--dry-run", action="store_true")
    qunar_csv.add_argument("--skip-existing-raw", action="store_true")
    qunar_csv.add_argument("--bulk-insert-missing", action="store_true")
    qunar_csv.add_argument("--chunk-size", type=int, default=500)
    qunar_csv.add_argument("--sample", type=int, default=3)
    qunar_csv.set_defaults(func=command_qunar_travel_csv)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
