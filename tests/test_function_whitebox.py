# coding: utf-8
import json
import os
import unittest

import django
from django.db import connection
from django.test import RequestFactory


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj2.settings")
django.setup()

from main.Qingganfenxi_v import (  # noqa: E402
    NEGATIVE_SENTIMENT,
    NEUTRAL_SENTIMENT,
    POSITIVE_SENTIMENT,
    analyze_sentiment_text,
    build_sentiment_results_from_reviews,
    find_poiname_by_plurl,
    preview_sentiment_results_from_reviews,
)
from main.decision_views import decision_summary  # noqa: E402
from main.models import ctripjd, ctrippinglun, qingganfenxi  # noqa: E402


class FunctionWhiteBoxTests(unittest.TestCase):
    """White-box tests for model fields and core analysis functions."""

    def test_wt_001_sentiment_positive_rule(self):
        result = analyze_sentiment_text("景色很美，体验很棒，非常值得推荐")
        self.assertEqual(result, POSITIVE_SENTIMENT)

    def test_wt_002_sentiment_negative_rule(self):
        result = analyze_sentiment_text("排队太久，人太多，体验很差，不推荐")
        self.assertEqual(result, NEGATIVE_SENTIMENT)

    def test_wt_003_sentiment_neutral_rule(self):
        result = analyze_sentiment_text("今天参观景区，路线包括主展区和周边区域")
        self.assertEqual(result, NEUTRAL_SENTIMENT)

    def test_wt_004_sentiment_model_has_spot_link_fields(self):
        field_names = {field.name for field in qingganfenxi._meta.fields}
        self.assertIn("poiname", field_names)
        self.assertIn("reviewid", field_names)

    def test_wt_005_core_model_has_decision_fields(self):
        field_names = {field.name for field in ctripjd._meta.fields}
        for field_name in ("poiname", "commentscore", "commentcount", "heatscore", "jiage", "districtname"):
            self.assertIn(field_name, field_names)

    def test_wt_006_reviews_model_has_source_url(self):
        field_names = {field.name for field in ctrippinglun._meta.fields}
        for field_name in ("content", "usernick", "dptime", "plurl"):
            self.assertIn(field_name, field_names)

    def test_wt_007_sentiment_records_have_spot_name(self):
        total = qingganfenxi.objects.count()
        named = qingganfenxi.objects.exclude(poiname__isnull=True).exclude(poiname="").count()
        self.assertGreater(total, 0)
        self.assertEqual(total, named)

    def test_wt_008_find_spot_name_from_review_url(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT plurl FROM T_Attraction_Reviews "
                "WHERE plurl IS NOT NULL AND plurl<>'' "
                "ORDER BY id ASC LIMIT 1"
            )
            row = cursor.fetchone()
        if not row:
            self.skipTest("评论表没有可用于关联景点的 plurl 数据")

        poiname = find_poiname_by_plurl(row[0])
        self.assertTrue(poiname)

    def test_wt_009_batch_builder_keeps_reviews_linked(self):
        before = qingganfenxi.objects.count()
        result = preview_sentiment_results_from_reviews()
        after = qingganfenxi.objects.count()
        self.assertEqual(after, before)
        self.assertTrue(result.get("dry_run"))
        self.assertEqual(result.get("remaining"), 0)

    def test_wt_010_decision_summary_structure(self):
        request = RequestFactory().get("/lvxing2f63wq5x/decision/summary")
        response = decision_summary(request)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data.get("code"), 0)
        self.assertIn("summary", data["data"])
        self.assertIn("charts", data["data"])
        self.assertIn("decisions", data["data"])
        self.assertIn("recommendTop", data["data"]["decisions"])

    def test_wt_011_value_top_items_have_price(self):
        request = RequestFactory().get("/lvxing2f63wq5x/decision/summary")
        response = decision_summary(request)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data.get("code"), 0)
        value_top = data["data"]["decisions"]["valueTop"]
        self.assertGreater(len(value_top), 0)
        self.assertTrue(all(item.get("jiage") is not None for item in value_top))


if __name__ == "__main__":
    unittest.main(verbosity=2)
