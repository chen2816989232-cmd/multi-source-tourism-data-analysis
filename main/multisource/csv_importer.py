# coding:utf-8
import csv

from .normalizer import normalize_csv_row


DEFAULT_MAPPING = {
    "source_id": "source_id",
    "source_url": "source_url",
    "poiname": "poiname",
    "imgurl": "imgurl",
    "commentscore": "commentscore",
    "commentcount": "commentcount",
    "heatscore": "heatscore",
    "jiage": "jiage",
    "districtname": "districtname",
    "zonename": "zonename",
    "address": "address",
    "sightcategoryinfo": "sightcategoryinfo",
    "tagname": "tagname",
    "shortfeatures": "shortfeatures",
    "distancestr": "distancestr",
    "othertaglist": "othertaglist",
    "detailurl": "detailurl",
    "longitude": "longitude",
    "latitude": "latitude",
}


def read_csv_spots(path, platform, mapping=None, encoding="utf-8-sig"):
    mapping = mapping or DEFAULT_MAPPING
    with open(path, "r", encoding=encoding, newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        return [normalize_csv_row(platform, row, mapping) for row in reader]

