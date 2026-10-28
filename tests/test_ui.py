from __future__ import annotations

import unittest

from claude_chat_exporter.ui import load_html


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


if __name__ == "__main__":
    unittest.main()
