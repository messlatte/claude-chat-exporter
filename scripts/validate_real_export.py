from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from claude_chat_exporter.core import (
    conversation_graph,
    load_conversations,
    render_conversation,
    technical_block_count,
    write_exports,
)


def validate(source: Path) -> dict[str, int]:
    store = load_conversations(source)
    raw_characters = 0
    compact_characters = 0
    complete_characters = 0
    max_branches = 0
    technical_blocks = 0

    for conversation in store.conversations:
        raw = render_conversation(conversation, "raw_json")
        if json.loads(raw) != conversation:
            raise AssertionError("Der JSON-Roundtrip ist nicht strukturell identisch.")
        compact = render_conversation(conversation, "chatgpt_markdown")
        complete = render_conversation(conversation, "complete_markdown")
        if not compact or not complete:
            raise AssertionError("Ein Markdown-Export ist unerwartet leer.")
        raw_characters += len(raw)
        compact_characters += len(compact)
        complete_characters += len(complete)
        max_branches = max(max_branches, conversation_graph(conversation).path_count)
        technical_blocks += technical_block_count(conversation)

    summaries = store.summaries()
    representatives: list[dict] = []
    selectors = (
        lambda item: item["message_count"],
        lambda item: item["attachment_count"],
        lambda item: item["branch_count"],
    )
    for selector in selectors:
        summary = max(summaries, key=selector)
        conversation = store.get(summary["uuid"])
        if conversation not in representatives:
            representatives.append(conversation)
    empty = next((item for item in summaries if item["is_empty"]), None)
    if empty:
        representatives.append(store.get(empty["uuid"]))

    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        markdown_files = write_exports(representatives, "chatgpt_markdown", folder)
        json_files = write_exports(representatives, "raw_json", folder)
        if len(markdown_files) != len(representatives) or len(json_files) != len(representatives):
            raise AssertionError("Der Mehrfachexport hat Dateien ausgelassen.")
        for path, conversation in zip(json_files, representatives, strict=True):
            if json.loads(path.read_text(encoding="utf-8")) != conversation:
                raise AssertionError("Eine exportierte JSON-Datei ist nicht strukturell identisch.")

    return {
        "conversations": len(store.conversations),
        "messages": sum(item["message_count"] for item in summaries),
        "empty": sum(1 for item in summaries if item["is_empty"]),
        "max_branches": max_branches,
        "technical_blocks": technical_blocks,
        "raw_characters": raw_characters,
        "compact_characters": compact_characters,
        "complete_characters": complete_characters,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.source), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
