"""Run with the application's Python environment; no database is accessed."""

import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
from html.parser import HTMLParser

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
import django
django.setup()

from django.conf import settings
from django.http import Http404, HttpResponse
from django.template import Context, Engine
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import path

if os.environ.get("SEARCH_VIEW_FILE"):
    spec = importlib.util.spec_from_file_location("search_under_test", os.environ["SEARCH_VIEW_FILE"])
    views = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(views)
else:
    from apps.search import views

urlpatterns = [path("", lambda request: HttpResponse(), name="home"),
               path("search/", views.SearchPageView.as_view(), name="search")]


class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = {}
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("rel") in ("prev", "next"):
            self.links[attrs["rel"]] = attrs["href"]


@override_settings(ROOT_URLCONF=__name__)
class SearchTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.results = [SimpleNamespace(title=f"Товар {n}", meta={"name": f"Товар {n}"},
                                       content_type=SimpleNamespace(name="товар"),
                                       url=f"/result/{n}/") for n in range(41)]
        filename = os.environ.get("SEARCH_TEMPLATE_FILE", str(Path(settings.BASE_DIR) / "templates/search.html"))
        self.template = Engine(loaders=[("django.template.loaders.locmem.Loader", {
            "html/_layout.html": "{% block content %}{% endblock %}",
            "search.html": Path(filename).read_text(),
        })], libraries={"base_tags": "apps.content.templatetags.base_tags",
                        "search_tags": "apps.search.templatetags.search_tags"}).get_template("search.html")

    def page(self, params, results=None):
        request = self.factory.get("/search/", params)
        ordered = self.results if results is None else results
        queryset = SimpleNamespace(order_by=lambda *fields: ordered)
        with patch.object(views.search, "search", return_value=queryset):
            response = views.SearchPageView.as_view()(request)
        html = self.template.render(Context(dict(response.context_data, request=request)))
        return response, html

    def test_pages_bound_rendered_results_without_overlap(self):
        first, first_html = self.page({"query": "ковш"})
        second, second_html = self.page({"query": "ковш", "page": "2"})
        last, last_html = self.page({"query": "ковш", "page": "3"})
        self.assertEqual(first_html.count('class="block-found"'), 20)
        self.assertEqual(second_html.count('class="block-found"'), 20)
        self.assertEqual(last_html.count('class="block-found"'), 1)
        self.assertEqual(list(first.context_data["results"]), self.results[:20])
        self.assertEqual(list(second.context_data["results"]), self.results[20:40])
        self.assertEqual(list(last.context_data["results"]), self.results[40:])

    def test_navigation_preserves_query_and_only_shows_available_directions(self):
        query = 'ковш & "тест" + /'
        _, first = self.page({"query": query})
        _, middle = self.page({"query": query, "page": "2"})
        _, last = self.page({"query": query, "page": "3"})
        self.assertNotIn("prev", Links(first).links)
        self.assertNotIn("next", Links(last).links)
        for direction, number in (("prev", "1"), ("next", "3")):
            self.assertEqual(parse_qs(urlsplit(Links(middle).links[direction]).query),
                             {"query": [query], "page": [number]})

    def test_no_results_keeps_empty_message_and_hides_pagination(self):
        _, html = self.page({"query": "нет совпадений"}, results=[])
        self.assertIn("По вашему запросу ничего не найдено", html)
        self.assertNotIn('class="search-pagination"', html)

    def test_missing_query_redirects_without_searching(self):
        with patch.object(views.search, "search") as search:
            response = views.SearchPageView.as_view()(self.factory.get("/search/"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        search.assert_not_called()

    def test_invalid_or_missing_pages_return_404(self):
        for page in ("invalid", "0", "-1", "999"):
            with self.subTest(page=page), self.assertRaises(Http404):
                self.page({"query": "ковш", "page": page})


if __name__ == "__main__":
    unittest.main()
