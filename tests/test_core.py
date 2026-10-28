from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from claude_chat_exporter.core import (
    conversation_graph,
    load_conversations,
    render_conversation,
    safe_export_filename,
    write_exports,
)


def message(
    uuid: str,
    parent: str,
    sender: str,
    text: str,
    content: list[dict] | None = None,
    *,
    attachments: list[dict] | None = None,
    files: list[dict] | None = None,
) -> dict:
    return {
        "uuid": uuid,
        "parent_message_uuid": parent,
        "sender": sender,
        "text": text,
        "created_at": f"2026-01-01T00:00:0{uuid[-1] if uuid[-1].isdigit() else '0'}Z",
        "updated_at": f"2026-01-01T00:00:0{uuid[-1] if uuid[-1].isdigit() else '0'}Z",
        "content": content if content is not None else ([{"type": "text", "text": text, "citations": []}] if text else []),
        "attachments": attachments or [],
        "files": files or [],
    }


def branched_conversation() -> dict:
    return {
        "uuid": "12345678-abcd-ef00-1111-222233334444",
        "name": 'Plan: Windows / macOS? <Test>',
        "summary": "A deliberately synthetic fixture summary",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-03T00:00:00Z",
        "account": {"uuid": "account"},
        "future_conversation_field": {"kept": True},
        "chat_messages": [
            message("m1", "outside-root", "human", "Startfrage"),
            message(
                "m2",
                "m1",
                "assistant",
                "Legacy mit internem Denken",
                [
                    {"type": "thinking", "thinking": "NICHT_IM_KOMPAKTEXPORT", "signature": "sig"},
                    {
                        "type": "text",
                        "text": "Sichtbare Antwort",
                        "citations": [{"uuid": "cite", "details": {"url": "https://example.invalid"}}],
                    },
                    {"type": "tool_use", "name": "secret_tool", "input": {"secret": "WERKZEUGDETAIL"}},
                    {"type": "future_type", "payload": "UNBEKANNTER_BLOCK"},
                ],
                attachments=[
                    {
                        "file_name": "notizen.md",
                        "file_type": "text/markdown",
                        "file_size": 42,
                        "extracted_content": "Vollständiger Anhang mit ``` Fence",
                    }
                ],
                files=[{"file_name": "scan.pdf", "file_uuid": "file-uuid"}],
            ),
            message("m3", "m2", "human", "Variante A"),
            message("m4", "m2", "human", "Variante B"),
        ],
    }


class GraphTests(unittest.TestCase):
    def test_all_root_to_leaf_variants_are_reconstructed(self) -> None:
        graph = conversation_graph(branched_conversation())
        self.assertEqual(graph.paths, ((0, 1, 2), (0, 1, 3)))
        self.assertTrue(any("Parent" in warning for warning in graph.warnings))

    def test_empty_graph(self) -> None:
        conversation = branched_conversation()
        conversation["chat_messages"] = []
        graph = conversation_graph(conversation)
        self.assertEqual(graph.paths, ())


class RenderingTests(unittest.TestCase):
    def test_chatgpt_markdown_contains_visible_data_and_all_variants(self) -> None:
        rendered = render_conversation(branched_conversation(), "chatgpt_markdown")
        self.assertIn("Verzweigung 1 von 2", rendered)
        self.assertIn("Verzweigung 2 von 2", rendered)
        self.assertEqual(rendered.count("Startfrage"), 1)
        self.assertEqual(rendered.count("Sichtbare Antwort"), 1)
        self.assertIn("Variante A", rendered)
        self.assertIn("Variante B", rendered)
        self.assertIn("Sichtbare Antwort", rendered)
        self.assertIn("Vollständiger Anhang mit ``` Fence", rendered)
        self.assertIn("scan.pdf", rendered)
        self.assertIn("file-uuid", rendered)
        self.assertIn("https://example.invalid", rendered)
        self.assertNotIn("NICHT_IM_KOMPAKTEXPORT", rendered)
        self.assertNotIn("WERKZEUGDETAIL", rendered)
        self.assertNotIn("UNBEKANNTER_BLOCK", rendered)

    def test_thinking_only_message_is_not_exposed_as_visible_fallback(self) -> None:
        conversation = branched_conversation()
        conversation["chat_messages"] = [
            message(
                "m1",
                "outside",
                "assistant",
                "INTERNES_LEGACY_DENKEN",
                [{"type": "thinking", "thinking": "INTERNES_LEGACY_DENKEN"}],
            )
        ]
        rendered = render_conversation(conversation, "chatgpt_markdown")
        self.assertNotIn("INTERNES_LEGACY_DENKEN", rendered)
        self.assertIn("rein technische Nachricht", rendered)

    def test_complete_markdown_preserves_known_and_unknown_values(self) -> None:
        rendered = render_conversation(branched_conversation(), "complete_markdown")
        for value in (
            "Legacy mit internem Denken",
            "NICHT_IM_KOMPAKTEXPORT",
            "WERKZEUGDETAIL",
            "UNBEKANNTER_BLOCK",
            "future_conversation_field",
            "Vollständiger Anhang",
        ):
            self.assertIn(value, rendered)

    def test_raw_json_roundtrip_is_deep_equal(self) -> None:
        conversation = branched_conversation()
        rendered = render_conversation(conversation, "raw_json")
        self.assertEqual(json.loads(rendered), conversation)


class StoreAndFileTests(unittest.TestCase):
    def test_loader_search_filters_sort_and_no_source_mutation(self) -> None:
        first = branched_conversation()
        second = {
            "uuid": "second-chat",
            "name": "",
            "summary": "",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "chat_messages": [],
        }
        original = json.loads(json.dumps([first, second]))
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temporary:
            path = Path(temporary) / "conversations.json"
            path.write_text(json.dumps([first, second], ensure_ascii=False), encoding="utf-8")
            store = load_conversations(path)
        self.assertEqual(store.conversations, original)
        self.assertEqual(len(store.summaries()), 2)
        self.assertEqual(store.summaries(query="vollständiger anhang")[0]["uuid"], first["uuid"])
        self.assertEqual(store.summaries(filters={"attachments": True})[0]["uuid"], first["uuid"])
        self.assertEqual(store.summaries(filters={"exclude_empty": True})[0]["uuid"], first["uuid"])
        self.assertEqual(store.summaries(sort="created_asc")[0]["title"], "Ohne Titel")

    def test_invalid_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temporary:
            path = Path(temporary) / "conversations.json"
            path.write_text('{"not": "a list"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Konversationsliste"):
                load_conversations(path)

    def test_non_conversation_json_list_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temporary:
            path = Path(temporary) / "users.json"
            path.write_text('[{"email": "private@example.test"}]', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Nachrichtenliste"):
                load_conversations(path)

    def test_safe_filename_handles_windows_characters_and_reserved_names(self) -> None:
        conversation = branched_conversation()
        filename = safe_export_filename(conversation, "chatgpt_markdown")
        self.assertEqual(filename, "2026-01-01__Plan- Windows - macOS- -Test__12345678abcdef001111222233334444.md")
        conversation["name"] = "CON"
        self.assertIn("__CON__", safe_export_filename(conversation, "raw_json"))

    def test_write_exports_is_atomic_and_never_overwrites(self) -> None:
        conversation = branched_conversation()
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temporary:
            first = write_exports([conversation], "raw_json", temporary)[0]
            first_content = first.read_text(encoding="utf-8")
            second = write_exports([conversation], "raw_json", temporary)[0]
            self.assertNotEqual(first, second)
            self.assertEqual(first.read_text(encoding="utf-8"), first_content)
            self.assertEqual(json.loads(second.read_text(encoding="utf-8")), conversation)
            leftovers = list(Path(temporary).glob(".claude-export-*.tmp"))
            self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
