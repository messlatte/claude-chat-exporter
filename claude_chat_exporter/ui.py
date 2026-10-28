"""Offline user interface for the Claude Chat Exporter.

The page lives in web/index.html, web/app.css and web/app.js. pywebview gets
it as one HTML string, so the stylesheet and script are inlined at load time.
"""

from importlib import resources

_STYLESHEET_TAG = '<link rel="stylesheet" href="app.css">'
_SCRIPT_TAG = '<script src="app.js"></script>'


def load_html() -> str:
    web = resources.files(__package__) / "web"
    page = (web / "index.html").read_text(encoding="utf-8")
    for tag in (_STYLESHEET_TAG, _SCRIPT_TAG):
        if page.count(tag) != 1:
            raise RuntimeError(f"web/index.html must contain {tag} exactly once.")
    stylesheet = (web / "app.css").read_text(encoding="utf-8")
    script = (web / "app.js").read_text(encoding="utf-8")
    page = page.replace(_STYLESHEET_TAG, f"<style>\n{stylesheet}</style>")
    return page.replace(_SCRIPT_TAG, f"<script>\n{script}</script>")
