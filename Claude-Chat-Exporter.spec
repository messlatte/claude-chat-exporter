# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import re


project_root = Path(SPECPATH).resolve()
entry_point = project_root / "run_claude_chat_exporter.py"
icon_path = project_root / "assets" / "claude-chat-exporter.ico"
version_path = project_root / "assets" / "version_info.txt"
license_path = project_root / "LICENSE"
notices_path = project_root / "THIRD_PARTY_NOTICES.md"
third_party_path = project_root / "third_party_licenses"

for required_file in (license_path, notices_path):
    if not required_file.is_file() or required_file.stat().st_size == 0:
        raise FileNotFoundError(f"Erforderlicher Lizenztext fehlt oder ist leer: {required_file.name}")
if not third_party_path.is_dir() or not any(path.is_file() and path.stat().st_size > 0 for path in third_party_path.rglob("*")):
    raise FileNotFoundError("third_party_licenses fehlt oder enthält keine Lizenztexte.")

analysis = Analysis(
    [str(entry_point)],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(license_path), "."),
        (str(notices_path), "."),
        (str(third_party_path), "third_party_licenses"),
    ],
    hiddenimports=["webview.platforms.edgechromium"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
        "setuptools",
        "tkinter",
        "webview.platforms.android",
        "webview.platforms.cef",
        "webview.platforms.cocoa",
        "webview.platforms.gtk",
        "webview.platforms.mshtml",
        "webview.platforms.qt",
    ],
    noarchive=False,
    optimize=0,
)

# Windows 10/11 provide the Universal CRT and API-set forwarders. Filtering
# them keeps the result independent of unrelated SDK/JDK folders on PATH and
# avoids redistributing system DLLs from an accidental third-party source.
system_dll = re.compile(r"^(?:api-ms-win-.*|ucrtbase)\.dll$", re.IGNORECASE)
analysis.binaries = [entry for entry in analysis.binaries if not system_dll.fullmatch(entry[0])]

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="Claude-Chat-Exporter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=str(version_path),
    icon=[str(icon_path)],
)
