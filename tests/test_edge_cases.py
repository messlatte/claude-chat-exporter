from __future__ import annotations

import json
from pathlib import Path
import unittest

from claude_chat_exporter.core import (
    ConversationStore,
    conversation_graph,
    render_conversation,
    safe_export_filename,
)


def _message(
    uuid: str,
    parent: str = "",
    *,
    sender: str = "human",
    text: str = "",
    content: object | None = None,
) -> dict:
    return {
        "uuid": uuid,
        "parent_message_uuid": parent,
        "sender": sender,
        "text": text,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "content": [{"type": "text", "text": text}] if content is None else content,
        "attachments": [],
        "files": [],
    }


def _conversation(messages: list[dict]) -> dict:
    return {
        "uuid": "abcdef00-1111-2222-3333-444455556666",
        "name": "Randfall",
        "summary": "",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "chat_messages": messages,
    }


class GraphHardeningTests(unittest.TestCase):
    def test_forward_parent_reference_is_resolved_independent_of_array_order(self) -> None:
        conversation = _conversation(
            [
                _message("child", "parent", text="Kind"),
                _message("parent", "", text="Wurzel"),
            ]
        )
        graph = conversation_graph(conversation)
        self.assertEqual(graph.paths, ((1, 0),))
        self.assertTrue(any("spätere" in warning for warning in graph.warnings))

    def test_parent_cycle_is_cut_without_recursion(self) -> None:
        conversation = _conversation(
            [
                _message("a", "b", text="A"),
                _message("b", "a", text="B"),
            ]
        )
        graph = conversation_graph(conversation)
        self.assertFalse(graph.truncated)
        self.assertEqual(set(graph.paths[0]), {0, 1})
        self.assertTrue(any("zyklische" in warning for warning in graph.warnings))

    def test_duplicate_message_uuid_links_to_nearest_earlier_copy(self) -> None:
        conversation = _conversation(
            [
                _message("dup", text="Erste Kopie"),
                _message("dup", text="Zweite Kopie"),
                _message("child", "dup", text="Antwort"),
            ]
        )
        graph = conversation_graph(conversation)
        self.assertEqual(graph.children, ((), (2,), ()))
        self.assertEqual(graph.paths, ((0,), (1, 2)))
        self.assertTrue(any("mehrfach" in warning for warning in graph.warnings))

    def test_self_parent_becomes_root_and_is_reported_as_cycle(self) -> None:
        conversation = _conversation([_message("self", "self", text="Selbst")])
        graph = conversation_graph(conversation)
        self.assertEqual(graph.roots, (0,))
        self.assertEqual(graph.paths, ((0,),))
        self.assertTrue(any("zyklische" in warning for warning in graph.warnings))

    def test_compact_markdown_keeps_tree_when_path_list_is_not_materialized(self) -> None:
        root = _message("root", text="Wurzel")
        children = [_message(f"child-{index}", "root", text=str(index)) for index in range(10_001)]
        conversation = _conversation([root, *children])
        graph = conversation_graph(conversation)
        self.assertTrue(graph.truncated)
        self.assertEqual(graph.path_count, 10_001)
        self.assertEqual(graph.paths, ())
        rendered = render_conversation(conversation, "chatgpt_markdown")
        self.assertIn("child-10000", rendered)
        self.assertEqual(rendered.count(":MESSAGE:"), 10_002)


class RenderingHardeningTests(unittest.TestCase):
    def test_hidden_text_is_omitted_from_compact_but_preserved_elsewhere(self) -> None:
        secret = "VERSTECKTER_TEXT_123"
        conversation = _conversation(
            [
                _message(
                    "m1",
                    sender="assistant",
                    text=secret,
                    content=[{"type": "text", "text": secret, "hidden_in_chat": True}],
                )
            ]
        )
        self.assertNotIn(secret, render_conversation(conversation, "chatgpt_markdown"))
        self.assertIn(secret, render_conversation(conversation, "complete_markdown"))
        self.assertEqual(json.loads(render_conversation(conversation, "raw_json")), conversation)

    def test_nested_unknown_technical_values_are_searchable(self) -> None:
        needle = "TIEF_VERSCHACHTELTER_SUCHWERT"
        conversation = _conversation(
            [
                _message(
                    "m1",
                    content=[{"type": "future", "payload": {"items": [{"value": needle}]}}],
                )
            ]
        )
        store = ConversationStore([conversation], Path("conversations.json"))
        self.assertEqual(store.summaries(query=needle)[0]["uuid"], conversation["uuid"])
        self.assertEqual(store.summaries(query="parent_message_uuid"), [])

    def test_complete_markdown_preserves_null_missing_and_unknown_fields(self) -> None:
        first = _message("m1", content=[])
        first["nullable"] = None
        second = _message("m2", "m1", content=[])
        second.pop("text")
        second["future"] = {"enabled": False, "count": 0}
        conversation = _conversation([first, second])
        rendered = render_conversation(conversation, "complete_markdown")
        self.assertIn('"nullable": null', rendered)
        self.assertIn('"future": {', rendered)
        self.assertNotIn('"text"', rendered.split("### Nachricht 2", 1)[1])

    def test_missing_uuid_filename_uses_long_deterministic_suffix(self) -> None:
        conversation = _conversation([])
        conversation.pop("uuid")
        first = safe_export_filename(conversation, "raw_json", fallback_index=7)
        second = safe_export_filename(conversation, "raw_json", fallback_index=7)
        self.assertEqual(first, second)
        suffix = first.rsplit("__", 1)[1].removesuffix(".json")
        self.assertGreaterEqual(len(suffix), 16)


if __name__ == "__main__":
    unittest.main()
