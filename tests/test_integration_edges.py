from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from claude_chat_exporter.app import DesktopApi, SOURCE_FILE_TYPES, _copy_to_clipboard, _format_warnings
from claude_chat_exporter.core import (
    ConversationStore,
    load_conversations,
    render_conversation,
    safe_export_filename,
    write_exports,
)


def _message(uuid: str, text: str, *, role: str = "human") -> dict:
    return {
        "uuid": uuid,
        "parent_message_uuid": "",
        "sender": role,
        "text": text,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "content": [{"type": "text", "text": text}],
        "attachments": [],
        "files": [],
    }


def _conversation(uuid: str = "01234567-89ab-cdef-0000-000000000001") -> dict:
    return {
        "uuid": uuid,
        "name": "Integration",
        "summary": "",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "chat_messages": [_message("m1", "Hallo")],
    }


class LoaderAndFilenameTests(unittest.TestCase):
    def test_design_chats_are_discovered_and_renderable(self) -> None:
        regular = _conversation()
        design = {
            "uuid": "design-chat-1",
            "title": "Design-Arbeit",
            "created_at": "2026-01-02T00:00:00Z",
            "updated_at": "2026-01-02T00:00:00Z",
            "project": {"uuid": "project-1", "name": "Projekt"},
            "messages": [
                {
                    "uuid": "d1",
                    "role": "user",
                    "created_at": "2026-01-02T00:00:00Z",
                    "content": {
                        "id": "inner-1",
                        "role": "user",
                        "timestamp": "2026-01-02T00:00:00Z",
                        "content": "Design-Frage",
                        "attachments": [
                            {"id": "a1", "name": "design.txt", "type": "text", "content": "Design-Anhang"}
                        ],
                    },
                },
                {
                    "uuid": "d2",
                    "role": "assistant",
                    "created_at": "2026-01-02T00:01:00Z",
                    "content": {
                        "id": "inner-2",
                        "role": "assistant",
                        "timestamp": "2026-01-02T00:01:00Z",
                        "content": "Design-Antwort",
                        "contentBlocks": [
                            {"type": "text", "text": "Design-Antwort"},
                            {"type": "thinking", "text": "INTERNES_DESIGN_DENKEN"},
                            {"type": "tool_call", "toolCall": {"name": "edit", "input": {"secret": "INTERNES_TOOL"}}},
                        ],
                    },
                },
            ],
        }
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temporary:
            root = Path(temporary)
            source = root / "conversations.json"
            source.write_text(json.dumps([regular]), encoding="utf-8")
            design_folder = root / "design_chats"
            design_folder.mkdir()
            (design_folder / "design.json").write_text(json.dumps(design), encoding="utf-8")
            (design_folder / "broken.json").write_text("{broken", encoding="utf-8")
            store = load_conversations(source)
        self.assertEqual(len(store.conversations), 2)
        summary = next(item for item in store.summaries() if item["uuid"] == "design-chat-1")
        self.assertEqual(summary["title"], "Design-Arbeit")
        self.assertEqual(summary["message_count"], 2)
        self.assertEqual(summary["attachment_count"], 1)
        self.assertGreaterEqual(summary["char_count"], len("Design-FrageDesign-AntwortDesign-Anhang"))
        self.assertTrue(summary["has_technical"])
        self.assertEqual(len(store.load_warnings), 1)
        compact = render_conversation(design, "chatgpt_markdown")
        self.assertIn("Design-Frage", compact)
        self.assertIn("Design-Antwort", compact)
        self.assertIn("Design-Anhang", compact)
        self.assertNotIn("INTERNES_DESIGN_DENKEN", compact)
        self.assertNotIn("INTERNES_TOOL", compact)
        self.assertTrue(any("2 technische" in value for value in _format_warnings(design, "chatgpt_markdown", len(compact))))
        complete = render_conversation(design, "complete_markdown")
        self.assertIn("Nachricht 1 — user", complete)
        self.assertIn("Nachricht 2 — assistant", complete)
        self.assertIn("Design-Arbeit", safe_export_filename(design, "raw_json"))

    def test_similar_uuid_prefixes_produce_distinct_stable_filenames(self) -> None:
        first = _conversation("01234567-89ab-cdef-AAAA-000000000001")
        second = _conversation("01234567-89ab-cdef-BBBB-000000000002")
        self.assertNotEqual(
            safe_export_filename(first, "raw_json"),
            safe_export_filename(second, "raw_json"),
        )

    def test_hidden_design_text_is_not_exposed_via_aggregate_content(self) -> None:
        conversation = {
            "uuid": "hidden-design",
            "title": "Hidden",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "messages": [
                {
                    "uuid": "m1",
                    "role": "assistant",
                    "created_at": "2026-01-01T00:00:00Z",
                    "content": {
                        "content": "SICHTBAR_GEHEIM",
                        "contentBlocks": [
                            {"type": "text", "text": "SICHTBAR_"},
                            {"type": "text", "text": "GEHEIM", "hidden_in_chat": True},
                        ],
                    },
                }
            ],
        }
        compact = render_conversation(conversation, "chatgpt_markdown")
        self.assertIn("SICHTBAR_", compact)
        self.assertNotIn("GEHEIM", compact)

    def test_technical_only_design_blocks_do_not_fall_back_to_aggregate_content(self) -> None:
        secret = "DESIGN_TECH_ONLY_SECRET"
        conversation = {
            "uuid": "technical-only-design",
            "title": "Technical only",
            "messages": [
                {
                    "uuid": "m1",
                    "role": "assistant",
                    "content": {
                        "content": secret,
                        "contentBlocks": [{"type": "thinking", "text": secret}],
                    },
                }
            ],
        }
        compact = render_conversation(conversation, "chatgpt_markdown")
        self.assertNotIn(secret, compact)

    def test_size_api_is_exact_and_cached_lazily(self) -> None:
        conversation = _conversation()
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temporary:
            api = DesktopApi(settings_path=Path(temporary) / "settings.json")
            api._store = ConversationStore([conversation], Path("conversations.json"))
            with patch("claude_chat_exporter.app.render_conversation", wraps=render_conversation) as renderer:
                first = api.get_sizes([conversation["uuid"]], "raw_json")
                second = api.get_sizes([conversation["uuid"]], "raw_json")
        self.assertTrue(first["ok"])
        self.assertEqual(first, second)
        self.assertEqual(first["total_chars"], len(render_conversation(conversation, "raw_json")))
        self.assertEqual(renderer.call_count, 1)


class SourceDialogTests(unittest.TestCase):
    def test_project_and_third_party_licenses_are_available_in_app(self) -> None:
        result = DesktopApi(settings_path=Path("unused-settings.json")).get_legal_notices()

        self.assertTrue(result["ok"])
        self.assertGreater(result["file_count"], 20)
        self.assertIn("LICENSE", result["text"])
        self.assertIn("THIRD_PARTY_NOTICES.md", result["text"])
        self.assertIn("PyInstaller", result["text"])
        self.assertIn("zlib 1.3.2", result["text"])

    def test_source_file_filters_match_pinned_pywebview_syntax(self) -> None:
        from webview.util import parse_file_type

        self.assertEqual(
            [parse_file_type(value)[1] for value in SOURCE_FILE_TYPES],
            ["*.json", "*.json"],
        )

    def test_cancelled_source_dialog_preserves_loaded_store(self) -> None:
        import webview
        from webview.util import parse_file_type

        captured: dict = {}

        class FakeWindow:
            def create_file_dialog(self, dialog_type, **kwargs):
                captured["dialog_type"] = dialog_type
                captured.update(kwargs)
                for value in kwargs["file_types"]:
                    parse_file_type(value)
                return None

        conversation = _conversation()
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temporary:
            api = DesktopApi(settings_path=Path(temporary) / "settings.json")
            existing_store = ConversationStore([conversation], Path("conversations.json"))
            api._store = existing_store
            api._source_path = Path("conversations.json")
            api.bind_window(FakeWindow())
            result = api.choose_source()

        self.assertEqual(result, {"ok": False, "cancelled": True})
        self.assertIs(api._store, existing_store)
        self.assertEqual(captured["dialog_type"], webview.FileDialog.OPEN)
        self.assertFalse(captured["allow_multiple"])
        self.assertEqual(captured["file_types"], SOURCE_FILE_TYPES)


def _is_plain(value: object) -> bool:
    if value is None or isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, list):
        return all(_is_plain(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _is_plain(item) for key, item in value.items())
    return False


class JsApiSurfaceTests(unittest.TestCase):
    def test_public_attributes_are_plain_values(self) -> None:
        # pywebview walks the public attributes of js_api from a background
        # thread and recurses into objects; walking the window hung startup.
        class FakeWindow:
            native = object()

        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temporary:
            source = Path(temporary) / "conversations.json"
            source.write_text(json.dumps([_conversation()]), encoding="utf-8")
            api = DesktopApi(settings_path=Path(temporary) / "settings.json", startup_source=source)
            api.bind_window(FakeWindow())
            before_load = {name: getattr(api, name) for name in dir(api) if not name.startswith("_")}
            self.assertTrue(api.initialize()["loaded"])
            after_load = {name: getattr(api, name) for name in dir(api) if not name.startswith("_")}

        for attributes in (before_load, after_load):
            for name, value in attributes.items():
                if callable(value):
                    continue
                with self.subTest(attribute=name):
                    self.assertTrue(_is_plain(value), f"DesktopApi.{name} is a {type(value).__name__}")


class SideEffectSafetyTests(unittest.TestCase):
    def test_multi_export_renders_everything_before_creating_files(self) -> None:
        conversations = [_conversation(), _conversation("other")]
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temporary:
            with patch(
                "claude_chat_exporter.core.render_conversation",
                side_effect=["first", ValueError("late render failure")],
            ):
                with self.assertRaisesRegex(ValueError, "late render failure"):
                    write_exports(conversations, "chatgpt_markdown", temporary)
            self.assertEqual(list(Path(temporary).iterdir()), [])

    def test_successful_copy_is_not_masked_by_settings_failure(self) -> None:
        conversation = _conversation()
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temporary:
            api = DesktopApi(settings_path=Path(temporary) / "settings.json")
            api._store = ConversationStore([conversation], Path("conversations.json"))
            with patch("claude_chat_exporter.app._copy_to_clipboard") as clipboard:
                with patch.object(api._settings, "save", side_effect=OSError("read only")):
                    result = api.copy_selected(conversation["uuid"])
        clipboard.assert_called_once()
        self.assertTrue(result["ok"])
        self.assertTrue(any("kopiert" in warning for warning in result["warnings"]))

    def test_embedded_nul_is_rejected_before_platform_clipboard_access(self) -> None:
        with self.assertRaisesRegex(ValueError, "Nullzeichen"):
            _copy_to_clipboard("vorher\x00nachher")


if __name__ == "__main__":
    unittest.main()
