from __future__ import annotations

from importlib import resources
import re
import unittest

from claude_chat_exporter.core import VALID_FORMATS
from claude_chat_exporter.ui import load_html


WEB = resources.files("claude_chat_exporter") / "web"


class LoadHtmlTests(unittest.TestCase):
    def test_stylesheet_and_script_are_inlined(self) -> None:
        html = load_html()
        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertNotIn('href="app.css"', html)
        self.assertNotIn('src="app.js"', html)
        self.assertEqual(html.count("<style>"), 1)
        self.assertEqual(html.count("<script>"), 1)
        self.assertLess(html.index("--bg: #0b0c0d;"), html.index("</head>"))
        self.assertLess(html.index('addEventListener("pywebviewready"'), html.index("</body>"))


class FormatListTests(unittest.TestCase):
    # core.VALID_FORMATS is the source; the page keeps its own copies for
    # validation in app.js and for the labels of the format menu.
    def test_script_formats_match_core(self) -> None:
        script = (WEB / "app.js").read_text(encoding="utf-8")
        match = re.search(r"const VALID_FORMATS = new Set\(\[([^\]]*)\]\);", script)
        self.assertIsNotNone(match)
        self.assertEqual(set(re.findall(r'"([^"]+)"', match.group(1))), VALID_FORMATS)

    def test_format_menu_matches_core(self) -> None:
        page = (WEB / "index.html").read_text(encoding="utf-8")
        match = re.search(r'<select id="formatSelect"[^>]*>(.*?)</select>', page, re.DOTALL)
        self.assertIsNotNone(match)
        values = re.findall(r'<option value="([^"]+)"', match.group(1))
        self.assertEqual(len(values), len(set(values)))
        self.assertEqual(set(values), VALID_FORMATS)


if __name__ == "__main__":
    unittest.main()
