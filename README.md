# Claude Chat Exporter

[![CI](https://github.com/messlatte/claude-chat-exporter/actions/workflows/ci.yml/badge.svg)](https://github.com/messlatte/claude-chat-exporter/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/messlatte/claude-chat-exporter)](https://github.com/messlatte/claude-chat-exporter/releases/latest)

Windows app that pulls single chats out of a Claude data export, for example to continue them in ChatGPT. It reads `conversations.json` and saves the chosen chats as Markdown or as the original JSON. Everything runs locally; the app has no network features. The UI is in German.

![Chat list with four sample chats and the Markdown preview of the first one](docs/screenshot.png)

## Why

Claude's data export puts every conversation into one large `conversations.json`. I wanted to continue a few of those chats in ChatGPT, which means getting single conversations out of that file in a form another assistant can read, without uploading the export anywhere.

## Download

The [latest release](https://github.com/messlatte/claude-chat-exporter/releases/latest) has the EXE, which runs without installation, and a ZIP with the same EXE and all licence texts. `SHA256SUMS.txt` lists the checksums. The app needs the Microsoft Edge WebView2 runtime, which current Windows versions ship with.

The EXE is not signed, so Windows SmartScreen shows "Unknown publisher". "More info" and then "Run anyway" starts it.

## Usage

1. Request a data export from Claude and unzip it.
2. Start the EXE and choose `conversations.json`. If it sits next to the EXE, the app finds it on its own.
3. Click a chat to see the preview. Tick the box on a chat card to mark it for export.
4. "Für ChatGPT kopieren" copies the open chat, "Exportieren" saves every marked chat as its own file.

## Formats

- **ChatGPT Markdown:** visible text, attachments and branches, without internal thinking and tool blocks.
- **Complete Markdown:** additionally all metadata and technical blocks.
- **Original JSON:** the unchanged chat object.

Complete Markdown and original JSON can contain internal prompts and tool data, so check those files before passing them on. In branched conversations the shared history appears once. If a file name already exists, the new file gets "(2)" in its name.

## Privacy

The app reads only the chosen file and, if present, the `design_chats` folder next to it. It stores the last source path, the output folder and the format in `%APPDATA%\ClaudeChatExporter\settings.json`. Please do not upload real exports or chat content in issues.

## How it works

- `claude_chat_exporter/core.py` loads and validates `conversations.json`, builds the message tree of each chat, renders the formats and writes the files. It has no UI code.
- `claude_chat_exporter/app.py` opens the pywebview window and defines `DesktopApi`, whose methods the page calls.
- `claude_chat_exporter/web/` holds `index.html`, `app.css` and `app.js`. `app.py` inlines the CSS and JavaScript when it loads the page.
- `Claude-Chat-Exporter.spec` and `build_windows.ps1` build the single EXE with PyInstaller.

## Design decisions

- **pywebview and a plain Python core.** The window uses the WebView2 runtime that Windows already has, so the EXE bundles no browser. Because `core.py` has no UI code, parsing and rendering are tested without a window.
- **Only `DesktopApi` methods reach the page.** pywebview hands the page every public attribute of the API object and walks into nested objects. A public window attribute made the app hang at startup (2 of 10 measured starts), and a public settings path gave the page methods such as `unlink`. All state is private now, and `test_public_attributes_are_plain_values` checks it.
- **Exports are all or nothing.** Every chosen chat is rendered first. Each file is written to a temporary file in the target folder, flushed to disk and renamed; Windows refuses to rename onto an existing name, so a clash becomes "(2)". If one write fails, the files written in that run are removed.
- **Message boundaries cannot be faked.** ChatGPT Markdown wraps each message in a marker such as `<<<CLAUDE_EXPORT_1A2B3C4D5E6F:MESSAGE:…>>>`. The marker is derived from the chat id and salted until it appears nowhere in the chat's own text, so pasted text cannot end a message early.
- **Branches are kept.** Claude stores a chat as a tree of messages with parent links. The export follows every branch and writes the shared history once. Broken parent links from truncated or hand-edited exports are repaired, and each repair path names the test that covers it.
- **Licence texts come from the built EXE.** The ZIP and the "Lizenzen" dialog carry the licence texts of every bundled component, checked against what is actually inside the EXE.

## Limitations

- Windows only.
- Anthropic does not document the format of `conversations.json`. A change in the export can break the import.
- The export has to be unzipped first.
- Indirect build dependencies are not pinned, so `THIRD_PARTY_NOTICES.md` has to be checked against each release build.

## Development

Requirements: Windows, Python 3.13 and the WebView2 runtime.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt -e .
.\.venv\Scripts\python.exe run_claude_chat_exporter.py
```

`python scripts/render_ui_fixture.py` writes `build/ui-fixture.html` with sample data, which opens in a normal browser for UI work. `.\build_windows.ps1` builds the EXE into `dist\Claude-Chat-Exporter.exe`.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m ruff check .
```

CI runs ruff and the tests on pushes to `main` and on pull requests. Pushing a `v*` tag builds the EXE, the ZIP and the checksums and publishes the release.

## License

[MIT](LICENSE). The licences of the bundled dependencies are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and `third_party_licenses/`, and in the app under "Lizenzen".

This project is not affiliated with Anthropic or OpenAI. "Claude" and "ChatGPT" are trademarks of their owners.
