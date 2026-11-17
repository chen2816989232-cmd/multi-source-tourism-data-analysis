# coding:utf-8
import time

import requests

from .normalizer import normalize_amap_poi


AMAP_PLACE_TEXT_URL = "https://restapi.amap.com/v3/place/text"


def crawl_amap_spots(api_key, keyword, city="", max_page=5, sleep_seconds=1.0):
    records = []
    session = requests.Session()
    session.trust_env = False

    for page in range(1, max_page + 1):
        params = {
            "key": api_key,
            "keywords": keyword,
            "city": city,
            "offset": 20,
            "page": page,
            "extensions": "all",
            "output": "JSON",
        }
        response = session.get(AMAP_PLACE_TEXT_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "1":
            raise RuntimeError("AMap API error: {}".format(data))

        pois = data.get("pois") or []
        if not pois:
            break

        records.extend(normalize_amap_poi(poi) for poi in pois)
        time.sleep(sleep_seconds)

    return records
