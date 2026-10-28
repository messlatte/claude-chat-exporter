# Changelog

## 1.0.2 (2026-10-28)

- Fixed a hang at startup: pywebview walked the window object stored on the JavaScript API and could block. All `DesktopApi` state is now private, so the page reaches only the API methods.
- Updated dependencies: PyInstaller 6.22.3, pyinstaller-hooks-contrib 2026.9, pefile 2024.8.26, Pillow 13.0.0, pythonnet 3.2.1, pycparser 3.12, setuptools 84.2.1 and actions/setup-python 7.1.0
- `requirements.txt` holds only the direct runtime dependency, `requirements-build.txt` adds PyInstaller and Pillow; pip resolves the indirect dependencies
- Licence texts taken from the new packages; the PyInstaller bootloader now embeds zlib 1.3.2, and the NETStandard facades of pythonnet are gone
- The interface moved from `ui.py` into `claude_chat_exporter/web/` (`index.html`, `app.css`, `app.js`)
- Added `pyproject.toml`; CI installs the package and runs `ruff check`
- Removed code for platforms other than Windows

## 1.0.1 (2026-08-26)

First public release.

- Import of `conversations.json` and design chats
- Search, preview, clipboard and export of several chats at once
- Formats ChatGPT Markdown, complete Markdown and original JSON
- Branched conversations without repeated history
- Exports are written atomically and never overwrite existing files
- Single Windows EXE that runs without installation
