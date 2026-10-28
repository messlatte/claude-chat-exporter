from __future__ import annotations

import json
from pathlib import Path

from claude_chat_exporter.ui import load_html


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build" / "ui-fixture.html"


CONVERSATIONS = [
    {
        "uuid": "chat-001",
        "title": "Windows-App für Claude-Exporte planen",
        "summary": "Eine moderne lokale Anwendung mit verlustfreiem JSON und einem kompakten ChatGPT-Export.",
        "created_at": "2026-08-20T09:15:00Z",
        "updated_at": "2026-08-21T00:48:00Z",
        "message_count": 48,
        "attachment_count": 3,
        "file_count": 5,
        "branch_count": 3,
        "char_count": 184220,
        "estimated_tokens": 48479,
        "has_technical": True,
        "is_empty": False,
    },
    {
        "uuid": "chat-002",
        "title": "Reiseplanung: Japan im Frühling",
        "summary": "Route, Bahnpass, ruhige Unterkünfte und eine knappe Packliste.",
        "created_at": "2026-07-02T18:30:00Z",
        "updated_at": "2026-07-06T12:20:00Z",
        "message_count": 22,
        "attachment_count": 1,
        "file_count": 1,
        "branch_count": 1,
        "char_count": 68200,
        "estimated_tokens": 17947,
        "has_technical": False,
        "is_empty": False,
    },
    {
        "uuid": "chat-003",
        "title": "Quartalsbericht analysieren",
        "summary": "Kennzahlen, Risiken und offene Rückfragen aus einem PDF-Dokument.",
        "created_at": "2026-05-18T08:00:00Z",
        "updated_at": "2026-05-18T10:42:00Z",
        "message_count": 16,
        "attachment_count": 2,
        "file_count": 2,
        "branch_count": 2,
        "char_count": 126400,
        "estimated_tokens": 33263,
        "has_technical": True,
        "is_empty": False,
    },
    {
        "uuid": "chat-004",
        "title": "Ohne Titel",
        "summary": "",
        "created_at": "2026-03-01T11:00:00Z",
        "updated_at": "2026-03-01T11:00:00Z",
        "message_count": 0,
        "attachment_count": 0,
        "file_count": 0,
        "branch_count": 0,
        "char_count": 0,
        "estimated_tokens": 0,
        "has_technical": False,
        "is_empty": True,
    },
]


PREVIEW = """# Windows-App für Claude-Exporte planen

> Importierter historischer Gesprächsverlauf · 100 % lokal verarbeitet

## Gesprächsverlauf

<<<CLAUDE_EXPORT_DEMO:MESSAGE:1:ROLE:HUMAN>>>
Ich möchte meine Claude-Konversationen mit möglichst wenigen Klicks für ChatGPT exportieren.
<<<CLAUDE_EXPORT_DEMO:END:1>>>

<<<CLAUDE_EXPORT_DEMO:MESSAGE:2:ROLE:ASSISTANT>>>
Wir bauen eine schnelle lokale App mit Suche, Vorschau und drei klaren Exportformaten.

- ChatGPT-freundliches Markdown
- technisch vollständiges Markdown
- strukturell verlustfreies JSON
<<<CLAUDE_EXPORT_DEMO:END:2>>>
"""


def render() -> None:
    conversations = json.dumps(CONVERSATIONS, ensure_ascii=False)
    preview = json.dumps(PREVIEW, ensure_ascii=False)
    bridge = f"""
<script>
window.pywebview = {{ api: {{
  initialize: async () => ({{
    ok: true,
    loaded: true,
    source_name: "conversations.json",
    source_path: "C:/Claude Daten/conversations.json",
    export_folder: "C:/Claude Daten/ChatGPT Exporte",
    conversations: {conversations},
    settings: {{ last_format: "chatgpt_markdown", format: "chatgpt_markdown", sort: "updated_desc" }}
  }}),
  choose_source: async () => ({{ ok: false, cancelled: true }}),
  search: async () => {conversations},
  get_preview: async () => ({{ text: {preview}, truncated: false, total_chars: 184220, estimated_tokens: 48479, warnings: [] }}),
  get_sizes: async (ids) => ({{ ok: true, count: ids.length, total_chars: ids.length * 184220, estimated_tokens: ids.length * 48479 }}),
  export_selected: async (ids) => ({{ ok: true, count: ids.length, folder: "C:/Claude Daten/ChatGPT Exporte", files: [], warnings: [] }}),
  copy_selected: async () => ({{ ok: true, chars: 184220, estimated_tokens: 48479, warnings: [] }}),
  choose_export_folder: async () => ({{ ok: true, folder: "C:/Claude Daten/ChatGPT Exporte" }}),
  reveal_export_folder: async () => ({{ ok: true }}),
  get_legal_notices: async () => ({{
    ok: true,
    file_count: 3,
    text: "LICENSE\\nMIT License\\n\\nTHIRD_PARTY_NOTICES.md\\nDrittanbieter-Hinweise\\n\\nzlib-1.3.2.txt\\nzlib License"
  }})
}} }};
</script>
"""
    rendered = load_html().replace("</head>", bridge + "\n</head>", 1)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    render()
