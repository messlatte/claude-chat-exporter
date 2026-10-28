from __future__ import annotations

import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import threading
import time
from typing import Any

from .core import (
    VALID_FORMATS,
    ConversationStore,
    estimate_tokens,
    load_conversations,
    render_conversation,
    technical_block_count,
    write_exports,
)
from .ui import load_html


APP_NAME = "Claude Chat Exporter"
APP_FOLDER = "ClaudeChatExporter"
PREVIEW_LIMIT = 160_000
# Above this size the app suggests uploading the export instead of pasting it.
LARGE_CHAT_CHARS = 400_000
SOURCE_FILE_TYPES = (
    "Claude JSON (*.json)",
    "JSON Dateien (*.json)",
)


def _resource_root() -> Path:
    bundled_root = getattr(sys, "_MEIPASS", None)
    if bundled_root:
        return Path(bundled_root)
    return Path(__file__).resolve().parents[1]


def _settings_path() -> Path:
    system = platform.system()
    if system == "Windows":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif system == "Darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / APP_FOLDER / "settings.json"


class SettingsStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or _settings_path()
        self.values: dict[str, Any] = {
            "last_source": "",
            "export_folder": "",
            "last_format": "chatgpt_markdown",
        }
        self.load()

    def load(self) -> None:
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                for key in self.values:
                    value = loaded.get(key)
                    if isinstance(value, str):
                        self.values[key] = value
        except (OSError, ValueError, TypeError):
            return

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(f".{self.path.name}.{os.getpid()}.tmp")
        temporary.write_text(
            json.dumps(self.values, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, self.path)


class DesktopApi:
    def __init__(
        self,
        *,
        settings_path: Path | None = None,
        startup_source: Path | None = None,
    ) -> None:
        # All state stays private. pywebview builds the JavaScript API by
        # walking the public attributes of js_api from a background thread:
        # walking the window reaches the WinForms form and can hang startup,
        # and walking a Path would expose methods such as unlink to the page.
        self._settings = SettingsStore(settings_path)
        self._startup_source = startup_source
        self._store: ConversationStore | None = None
        self._source_path: Path | None = None
        self._window: Any = None
        self._lock = threading.RLock()
        self._size_cache: dict[tuple[str, str], tuple[int, int]] = {}
        self._legal_notices_cache: str | None = None
        self._legal_notices_file_count = 0

    def bind_window(self, window: Any) -> None:
        self._window = window

    def initialize(self) -> dict[str, Any]:
        with self._lock:
            if self._store is None:
                self._try_automatic_source()
            return self._state()

    def choose_source(self) -> dict[str, Any]:
        try:
            if self._window is None:
                return self._error("Das Dateifenster ist noch nicht bereit.")
            import webview

            previous = self._settings.values.get("last_source", "")
            directory = str(Path(previous).parent) if previous else ""
            selected = self._window.create_file_dialog(
                webview.FileDialog.OPEN,
                directory=directory,
                allow_multiple=False,
                file_types=SOURCE_FILE_TYPES,
            )
            if not selected:
                return {"ok": False, "cancelled": True}
            path = Path(selected[0])
            with self._lock:
                self._load_source(path)
                return self._state()
        except Exception as exc:  # UI boundary: return a friendly error, never chat content.
            return self._error(_friendly_exception(exc))

    def choose_export_folder(self) -> dict[str, Any]:
        try:
            if self._window is None:
                return self._error("Das Ordnerfenster ist noch nicht bereit.")
            import webview

            current = self._export_folder(create=False)
            selected = self._window.create_file_dialog(
                webview.FileDialog.FOLDER,
                directory=str(current.parent if current and not current.exists() else current or ""),
                allow_multiple=False,
            )
            if not selected:
                return {"ok": False, "cancelled": True}
            folder = Path(selected[0]).resolve()
            self._settings.values["export_folder"] = str(folder)
            self._settings.save()
            return {"ok": True, "folder": str(folder)}
        except Exception as exc:
            return self._error(_friendly_exception(exc))

    def search(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        sort: str = "updated_desc",
    ) -> list[dict[str, Any]]:
        with self._lock:
            if self._store is None:
                return []
            return self._store.summaries(query=query or "", filters=filters or {}, sort=sort)

    def get_preview(self, uuid: str, format: str = "chatgpt_markdown") -> dict[str, Any]:
        try:
            selected_format = _valid_format(format)
            with self._lock:
                conversation = self._conversation(uuid)
                text = render_conversation(conversation, selected_format)
                total = len(text)
                estimated_tokens = estimate_tokens(total)
                self._size_cache[(uuid, selected_format)] = (total, estimated_tokens)
            truncated = total > PREVIEW_LIMIT
            preview = text[:PREVIEW_LIMIT]
            if truncated:
                preview += (
                    "\n\n---\n\n"
                    f"Vorschau nach {PREVIEW_LIMIT:,} Zeichen gekürzt. "
                    "Kopie und Export werden gegenüber dem gewählten Format nicht zusätzlich gekürzt."
                )
            return {
                "text": preview,
                "truncated": truncated,
                "total_chars": total,
                "estimated_tokens": estimated_tokens,
                "warnings": _format_warnings(conversation, selected_format, total),
            }
        except Exception as exc:
            return {
                "text": "",
                "truncated": False,
                "total_chars": 0,
                "estimated_tokens": 0,
                "warnings": [],
                "error": _friendly_exception(exc),
            }


    def get_sizes(self, uuids: list[str], format: str = "chatgpt_markdown") -> dict[str, Any]:
        try:
            selected_format = _valid_format(format)
            unique_uuids = list(dict.fromkeys(uuids or []))
            total_chars = 0
            total_tokens = 0
            with self._lock:
                for uuid in unique_uuids:
                    cache_key = (uuid, selected_format)
                    size = self._size_cache.get(cache_key)
                    if size is None:
                        conversation = self._conversation(uuid)
                        characters = len(render_conversation(conversation, selected_format))
                        size = (characters, estimate_tokens(characters))
                        self._size_cache[cache_key] = size
                    total_chars += size[0]
                    total_tokens += size[1]
            return {
                "ok": True,
                "count": len(unique_uuids),
                "total_chars": total_chars,
                "estimated_tokens": total_tokens,
            }
        except Exception as exc:
            return self._error(_friendly_exception(exc))


    def export_selected(self, uuids: list[str], format: str = "chatgpt_markdown") -> dict[str, Any]:
        try:
            selected_format = _valid_format(format)
            if not uuids:
                return self._error("Bitte zuerst mindestens einen Chat auswählen.")
            warnings: list[str] = []
            with self._lock:
                conversations = [self._conversation(value) for value in dict.fromkeys(uuids)]
                folder = self._export_folder(create=True)
                files = write_exports(conversations, selected_format, folder)
                self._settings.values["last_format"] = selected_format
                try:
                    self._settings.save()
                except OSError:
                    warnings.append("Die Dateien wurden exportiert; nur die letzte Formatauswahl konnte nicht gespeichert werden.")
            if selected_format == "complete_markdown":
                warnings.append("Der technische Export kann interne Prompts und Tool-Daten enthalten.")
            return {
                "ok": True,
                "count": len(files),
                "folder": str(folder),
                "files": [Path(value).name for value in files],
                "warnings": warnings,
            }
        except Exception as exc:
            return self._error(_friendly_exception(exc))


    def copy_selected(self, uuid: str, format: str = "chatgpt_markdown") -> dict[str, Any]:
        try:
            selected_format = _valid_format(format)
            with self._lock:
                conversation = self._conversation(uuid)
                text = render_conversation(conversation, selected_format)
                warnings = _format_warnings(conversation, selected_format, len(text))
            _copy_to_clipboard(text)
            with self._lock:
                self._settings.values["last_format"] = selected_format
                try:
                    self._settings.save()
                except OSError:
                    warnings.append("Der Chat wurde kopiert; nur die letzte Formatauswahl konnte nicht gespeichert werden.")
            return {
                "ok": True,
                "chars": len(text),
                "estimated_tokens": estimate_tokens(len(text)),
                "warnings": warnings,
            }
        except Exception as exc:
            return self._error(_friendly_exception(exc))


    def reveal_export_folder(self) -> dict[str, Any]:
        try:
            folder = self._export_folder(create=True)
            system = platform.system()
            if system == "Windows":
                os.startfile(str(folder))  # type: ignore[attr-defined]
            elif system == "Darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
            return {"ok": True}
        except Exception as exc:
            return self._error(_friendly_exception(exc))

    def get_legal_notices(self) -> dict[str, Any]:
        try:
            if self._legal_notices_cache is not None:
                return {
                    "ok": True,
                    "text": self._legal_notices_cache,
                    "file_count": self._legal_notices_file_count,
                }

            root = _resource_root()
            paths = [root / "LICENSE", root / "THIRD_PARTY_NOTICES.md"]
            license_folder = root / "third_party_licenses"
            paths.extend(
                sorted(
                    (path for path in license_folder.rglob("*") if path.is_file()),
                    key=lambda value: value.relative_to(license_folder).as_posix().casefold(),
                )
            )
            if not paths[0].is_file() or not paths[1].is_file() or len(paths) == 2:
                raise FileNotFoundError

            sections: list[str] = []
            for path in paths:
                content = path.read_text(encoding="utf-8-sig").strip()
                if not content:
                    raise OSError
                label = path.name if path.parent == root else f"third_party_licenses/{path.relative_to(license_folder).as_posix()}"
                sections.append(f"{'=' * 76}\n{label}\n{'=' * 76}\n\n{content}")
            self._legal_notices_cache = "\n\n".join(sections) + "\n"
            self._legal_notices_file_count = len(paths)
            return {
                "ok": True,
                "text": self._legal_notices_cache,
                "file_count": len(paths),
            }
        except (OSError, UnicodeError):
            return self._error("Die eingebetteten Lizenzhinweise konnten nicht geladen werden.")

    def _try_automatic_source(self) -> None:
        candidates: list[Path] = []
        if self._startup_source:
            candidates.append(self._startup_source)
        candidates.extend(
            [
                Path(sys.argv[0]).resolve().parent / "conversations.json",
                Path.cwd() / "conversations.json",
            ]
        )
        recent = self._settings.values.get("last_source", "")
        if recent:
            candidates.append(Path(recent))

        seen: set[str] = set()
        for candidate in candidates:
            key = os.path.normcase(str(candidate.resolve()))
            if key in seen:
                continue
            seen.add(key)
            if candidate.is_file():
                try:
                    self._load_source(candidate)
                    return
                except (OSError, ValueError, TypeError):
                    continue

    def _load_source(self, path: Path) -> None:
        path = path.expanduser().resolve()
        store = load_conversations(path)
        self._store = store
        self._source_path = path
        self._size_cache.clear()
        self._settings.values["last_source"] = str(path)
        if not self._settings.values.get("export_folder"):
            self._settings.values["export_folder"] = str(path.parent / "ChatGPT Exporte")
        self._settings.save()

    def _state(self) -> dict[str, Any]:
        loaded = self._store is not None and self._source_path is not None
        return {
            "ok": True,
            "loaded": loaded,
            "source_name": self._source_path.name if self._source_path else "",
            "source_path": str(self._source_path) if self._source_path else "",
            "export_folder": str(self._export_folder(create=False)) if loaded else "",
            "conversations": self._store.summaries(sort="updated_desc") if self._store else [],
            "warnings": list(self._store.load_warnings) if self._store else [],
            "settings": {
                "last_format": self._settings.values.get("last_format", "chatgpt_markdown"),
            },
        }

    def _conversation(self, uuid: str) -> dict[str, Any]:
        if self._store is None:
            raise ValueError("Bitte zuerst eine conversations.json auswählen.")
        return self._store.get(uuid)

    def _export_folder(self, *, create: bool) -> Path:
        configured = self._settings.values.get("export_folder", "")
        if configured:
            folder = Path(configured).expanduser()
        elif self._source_path:
            folder = self._source_path.parent / "ChatGPT Exporte"
        else:
            folder = Path.home() / "Downloads" / "ChatGPT Exporte"
        folder = folder.resolve()
        if create:
            folder.mkdir(parents=True, exist_ok=True)
        return folder

    @staticmethod
    def _error(message: str) -> dict[str, Any]:
        return {"ok": False, "error": message}


def _valid_format(value: str) -> str:
    if value not in VALID_FORMATS:
        raise ValueError("Unbekanntes Exportformat.")
    return value


def _format_warnings(conversation: dict[str, Any], selected_format: str, characters: int) -> list[str]:
    warnings: list[str] = []
    if characters > LARGE_CHAT_CHARS:
        warnings.append("Sehr großer Chat: Als Datei in ChatGPT hochladen statt über die Zwischenablage einfügen.")
    if selected_format == "complete_markdown":
        warnings.append("Enthält technische Blöcke, interne Prompts und möglicherweise sensible Tool-Daten.")
    elif selected_format == "raw_json":
        warnings.append("Original-JSON ist strukturell verlustfrei, aber weniger angenehm zu lesen.")
    else:
        technical = technical_block_count(conversation)
        if technical:
            warnings.append(f"{technical} technische Blöcke werden im kompakten Markdown ausgelassen.")
    return warnings


def _friendly_exception(exc: Exception) -> str:
    if isinstance(exc, json.JSONDecodeError):
        return f"Die JSON-Datei ist an Zeile {exc.lineno}, Spalte {exc.colno} ungültig."
    if isinstance(exc, PermissionError):
        return "Auf die Datei oder den Ordner konnte nicht zugegriffen werden."
    if isinstance(exc, FileNotFoundError):
        return "Die ausgewählte Datei oder der Ordner wurde nicht gefunden."
    message = str(exc).strip()
    return message or "Die Aktion konnte nicht abgeschlossen werden."


def _copy_to_clipboard(text: str) -> None:
    if "\x00" in text:
        raise ValueError(
            "Dieser Chat enthält ein eingebettetes Nullzeichen. Nutze den Datei-Export, damit der Inhalt nicht abgeschnitten wird."
        )
    system = platform.system()
    if system == "Windows":
        _copy_windows(text)
        return
    if system == "Darwin":
        subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
        return
    command = shutil.which("wl-copy")
    if command:
        subprocess.run([command], input=text.encode("utf-8"), check=True)
        return
    command = shutil.which("xclip")
    if command:
        subprocess.run([command, "-selection", "clipboard"], input=text.encode("utf-8"), check=True)
        return
    raise RuntimeError("Keine unterstützte Zwischenablage gefunden.")


def _copy_windows(text: str) -> None:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    kernel32.GlobalAlloc.argtypes = (wintypes.UINT, ctypes.c_size_t)
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel32.GlobalLock.argtypes = (wintypes.HGLOBAL,)
    kernel32.GlobalLock.restype = wintypes.LPVOID
    kernel32.GlobalUnlock.argtypes = (wintypes.HGLOBAL,)
    kernel32.GlobalFree.argtypes = (wintypes.HGLOBAL,)
    user32.SetClipboardData.argtypes = (wintypes.UINT, wintypes.HANDLE)
    user32.SetClipboardData.restype = wintypes.HANDLE

    payload = text.encode("utf-16-le") + b"\x00\x00"
    handle = kernel32.GlobalAlloc(0x0002, len(payload))
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    pointer = kernel32.GlobalLock(handle)
    if not pointer:
        kernel32.GlobalFree(handle)
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        ctypes.memmove(pointer, payload, len(payload))
    finally:
        kernel32.GlobalUnlock(handle)

    opened = False
    for _ in range(8):
        if user32.OpenClipboard(None):
            opened = True
            break
        time.sleep(0.04)
    if not opened:
        kernel32.GlobalFree(handle)
        raise RuntimeError("Die Zwischenablage wird gerade von einem anderen Programm verwendet.")
    transferred = False
    try:
        if not user32.EmptyClipboard():
            raise ctypes.WinError(ctypes.get_last_error())
        if not user32.SetClipboardData(13, handle):
            raise ctypes.WinError(ctypes.get_last_error())
        transferred = True
    finally:
        user32.CloseClipboard()
        if not transferred:
            kernel32.GlobalFree(handle)


def _startup_source() -> Path | None:
    for argument in sys.argv[1:]:
        if not argument.startswith("-"):
            return Path(argument)
    return None


def main() -> None:
    import webview

    webview.settings["ALLOW_DOWNLOADS"] = False
    webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = False
    webview.settings["SHOW_DEFAULT_MENUS"] = False

    api = DesktopApi(startup_source=_startup_source())
    window = webview.create_window(
        APP_NAME,
        html=load_html(),
        js_api=api,
        width=1280,
        height=820,
        min_size=(980, 640),
        background_color="#151513",
        text_select=True,
        shadow=True,
    )
    api.bind_window(window)
    gui = "edgechromium" if platform.system() == "Windows" else None
    webview.start(gui=gui, debug=False, private_mode=True)


if __name__ == "__main__":
    main()
