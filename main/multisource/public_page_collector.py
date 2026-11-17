# coding:utf-8
import json
import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from lxml import html

from .normalizer import normalize_csv_row


DEFAULT_USER_AGENT = "academic-research-crawler/1.0"


def can_fetch(url, user_agent=DEFAULT_USER_AGENT):
    parsed = urlparse(url)
    robots_url = "{}://{}/robots.txt".format(parsed.scheme, parsed.netloc)
    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.read()
    return parser.can_fetch(user_agent, url)


def fetch_public_html(url, user_agent=DEFAULT_USER_AGENT):
    if not can_fetch(url, user_agent):
        raise RuntimeError("robots.txt disallows fetching: {}".format(url))
    response = requests.get(url, headers={"User-Agent": user_agent}, timeout=15)
    response.raise_for_status()
    return response.text


def first_xpath_text(tree, xpath):
    if not xpath:
        return ""
    values = tree.xpath(xpath)
    if not values:
        return ""
    value = values[0]
    if hasattr(value, "text_content"):
        return value.text_content().strip()
    return str(value).strip()


def parse_public_spot_page(url, platform, xpath_mapping, sleep_seconds=1.0):
    html_text = fetch_public_html(url)
    tree = html.fromstring(html_text)
    row = {"source_url": url}
    for target_field, xpath in xpath_mapping.items():
        row[target_field] = first_xpath_text(tree, xpath)
    time.sleep(sleep_seconds)
    return normalize_csv_row(platform, row, {})


def load_xpath_mapping(path):
    with open(path, "r", encoding="utf-8") as file_obj:
        return json.load(file_obj)

