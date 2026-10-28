from __future__ import annotations

import argparse
import json
from pathlib import Path

from claude_chat_exporter.core import _messages, load_conversations, render_conversation


def validate(source: Path) -> dict[str, int]:
    store = load_conversations(source)
    checked_messages = 0
    checked_visible_blocks = 0
    checked_attachments = 0
    checked_file_references = 0

    for conversation in store.conversations:
        compact = render_conversation(conversation, "chatgpt_markdown")
        complete = render_conversation(conversation, "complete_markdown")
        raw = render_conversation(conversation, "raw_json")
        if json.loads(raw) != conversation:
            raise AssertionError("Raw-JSON roundtrip mismatch")
        messages = _messages(conversation)
        if compact.count(":MESSAGE:") != len(messages) or compact.count(":END:") != len(messages):
            raise AssertionError("Compact tree omitted or duplicated a message")
        for message in messages:
            checked_messages += 1
            serialized = json.dumps(message, ensure_ascii=False, indent=2)
            if serialized not in complete:
                raise AssertionError("Complete Markdown omitted a message object")
            content = message.get("content")
            if isinstance(content, list):
                visible_values = [
                    block.get("text")
                    for block in content
                    if isinstance(block, dict)
                    and block.get("type") == "text"
                    and block.get("hidden") is not True
                    and block.get("hidden_in_chat") is not True
                ]
            elif isinstance(content, dict):
                blocks = content.get("contentBlocks")
                text_blocks = [
                    block
                    for block in blocks
                    if isinstance(block, dict) and block.get("type") == "text"
                ] if isinstance(blocks, list) else []
                if text_blocks:
                    visible_values = [
                        block.get("text")
                        for block in text_blocks
                        if block.get("hidden") is not True and block.get("hidden_in_chat") is not True
                    ]
                elif isinstance(content.get("content"), str):
                    visible_values = [content["content"]]
                else:
                    visible_values = []
            else:
                visible_values = []
            for value in visible_values:
                if isinstance(value, str) and value:
                    checked_visible_blocks += 1
                    if value not in compact:
                        raise AssertionError("Compact Markdown omitted a visible text block")
            attachments = message.get("attachments")
            if not isinstance(attachments, list) and isinstance(content, dict):
                attachments = content.get("attachments")
            if isinstance(attachments, list):
                for attachment in attachments:
                    if not isinstance(attachment, dict):
                        continue
                    value = attachment.get("extracted_content")
                    if not isinstance(value, str):
                        value = attachment.get("content")
                    if isinstance(value, str):
                        checked_attachments += 1
                        if value not in compact:
                            raise AssertionError("Compact Markdown omitted extracted attachment content")
            files = message.get("files")
            if isinstance(files, list):
                for file_reference in files:
                    if not isinstance(file_reference, dict):
                        continue
                    value = file_reference.get("file_uuid")
                    if isinstance(value, str) and value:
                        checked_file_references += 1
                        if value not in compact:
                            raise AssertionError("Compact Markdown omitted a file reference")

    return {
        "conversations": len(store.conversations),
        "messages_once": checked_messages,
        "visible_text_blocks": checked_visible_blocks,
        "attachments": checked_attachments,
        "file_references": checked_file_references,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.source), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
