# coding: utf-8
import os
import unittest

import django
import requests


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj2.settings")
django.setup()

from main.models import users  # noqa: E402


BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000/lvxing2f63wq5x")
TIMEOUT = int(os.getenv("TEST_TIMEOUT", "8"))


class ApiBlackBoxTests(unittest.TestCase):
    """Black-box tests for the running Django HTTP APIs."""

    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()
        admin = users.objects.order_by("id").first()
        if admin is None:
            raise unittest.SkipTest("数据库中没有管理员账号，无法执行登录接口测试")

        try:
            response = cls.session.post(
                f"{BASE_URL}/users/login",
                json={"username": admin.username, "password": admin.password},
                timeout=TIMEOUT,
            )
        except requests.exceptions.RequestException as exc:
            raise AssertionError(
                "接口测试需要先启动后端服务："
                "python manage.py runserver 127.0.0.1:8000；"
                f"当前无法连接 {BASE_URL}，原因：{exc}"
            ) from None
        cls.assert_http_ok(response, "管理员登录接口")
        data = response.json()
        if data.get("code") != 0 or not data.get("token"):
            raise AssertionError(f"管理员登录失败: {data}")

        cls.token = data["token"]
        cls.session.headers.update({"token": cls.token})

    @staticmethod
    def assert_http_ok(response, api_name):
        if response.status_code != 200:
            raise AssertionError(
                f"{api_name} HTTP状态异常: {response.status_code}, {response.text[:300]}"
            )

    def assert_api_ok(self, response, api_name):
        self.assert_http_ok(response, api_name)
        data = response.json()
        self.assertEqual(data.get("code"), 0, msg=f"{api_name} 业务状态异常: {data}")
        return data

    def test_it_001_admin_login_returns_token(self):
        self.assertTrue(self.token)

    def test_it_002_admin_login_rejects_wrong_password(self):
        admin = users.objects.order_by("id").first()
        response = requests.post(
            f"{BASE_URL}/users/login",
            json={"username": admin.username, "password": "__wrong_password__"},
            timeout=TIMEOUT,
        )
        self.assert_http_ok(response, "管理员错误密码登录接口")
        self.assertNotEqual(response.json().get("code"), 0)

    def test_it_003_core_attractions_page(self):
        data = self.assert_api_ok(
            self.session.get(
                f"{BASE_URL}/ctripjd/page",
                params={"page": 1, "limit": 10},
                timeout=TIMEOUT,
            ),
            "景点分页接口",
        )
        self.assertIn("list", data["data"])
        self.assertGreater(data["data"].get("total", 0), 0)

    def test_it_004_core_attractions_search_by_name(self):
        first = self.assert_api_ok(
            self.session.get(
                f"{BASE_URL}/ctripjd/page",
                params={"page": 1, "limit": 1},
                timeout=TIMEOUT,
            ),
            "景点分页接口",
        )["data"]["list"][0]
        keyword = (first.get("poiname") or "")[:2]
        data = self.assert_api_ok(
            self.session.get(
                f"{BASE_URL}/ctripjd/page",
                params={"page": 1, "limit": 10, "poiname": keyword},
                timeout=TIMEOUT,
            ),
            "景点名称查询接口",
        )
        self.assertIn("list", data["data"])

    def test_it_005_attraction_reviews_page(self):
        data = self.assert_api_ok(
            self.session.get(
                f"{BASE_URL}/ctrippinglun/page",
                params={"page": 1, "limit": 10},
                timeout=TIMEOUT,
            ),
            "游客评论分页接口",
        )
        self.assertIn("list", data["data"])
        self.assertGreaterEqual(data["data"].get("total", 0), 0)

    def test_it_006_sentiment_page_contains_spot_name(self):
        data = self.assert_api_ok(
            self.session.get(
                f"{BASE_URL}/qingganfenxi/page",
                params={"page": 1, "limit": 10},
                timeout=TIMEOUT,
            ),
            "情感分析分页接口",
        )
        rows = data["data"]["list"]
        self.assertGreater(len(rows), 0)
        self.assertTrue(all(row.get("poiname") for row in rows))

    def test_it_007_sentiment_group_by_result(self):
        data = self.assert_api_ok(
            self.session.get(
                f"{BASE_URL}/qingganfenxi/group/fenxijieguo",
                params={"limit": 10},
                timeout=TIMEOUT,
            ),
            "情感分析统计接口",
        )
        self.assertIsInstance(data["data"], list)
        self.assertGreater(len(data["data"]), 0)
        self.assertIn("fenxijieguo", data["data"][0])
        self.assertIn("total", data["data"][0])

    def test_it_008_batch_sentiment_analysis_is_idempotent(self):
        data = self.assert_api_ok(
            self.session.get(
                f"{BASE_URL}/qingganfenxi/batchAnalyze",
                params={"dryRun": "true"},
                timeout=TIMEOUT,
            ),
            "批量情感分析接口",
        )
        self.assertTrue(data["data"].get("dry_run"))
        self.assertIn("review_total", data["data"])
        self.assertEqual(data["data"].get("remaining"), 0)

    def test_it_009_decision_summary_returns_decisions(self):
        data = self.assert_api_ok(
            self.session.get(f"{BASE_URL}/decision/summary", timeout=TIMEOUT),
            "分析决策汇总接口",
        )
        self.assertIn("summary", data["data"])
        self.assertIn("charts", data["data"])
        self.assertIn("decisions", data["data"])
        self.assertIn("messages", data["data"]["decisions"])
        value_top = data["data"]["decisions"]["valueTop"]
        self.assertGreater(len(value_top), 0)
        self.assertTrue(all(item.get("jiage") is not None for item in value_top))

    def test_it_010_comprehensive_tourism_data_page(self):
        data = self.assert_api_ok(
            self.session.get(
                f"{BASE_URL}/lvyoushuju/page",
                params={"page": 1, "limit": 10},
                timeout=TIMEOUT,
            ),
            "综合旅游数据分页接口",
        )
        self.assertIn("list", data["data"])

    def test_it_011_news_list(self):
        data = self.assert_api_ok(
            self.session.get(
                f"{BASE_URL}/news/list",
                params={"page": 1, "limit": 5},
                timeout=TIMEOUT,
            ),
            "系统公告列表接口",
        )
        self.assertIn("list", data["data"])

    def test_it_012_protected_page_requires_token(self):
        response = requests.get(
            f"{BASE_URL}/qingganfenxi/page",
            params={"page": 1, "limit": 1},
            timeout=TIMEOUT,
        )
        self.assert_http_ok(response, "未登录访问受保护接口")
        self.assertEqual(response.json().get("code"), 401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
