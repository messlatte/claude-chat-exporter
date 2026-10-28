# Changelog

## 1.0.2 (unveröffentlicht)

- Abhängigkeiten aktualisiert: PyInstaller 6.22.3, pyinstaller-hooks-contrib 2026.9, pefile 2024.8.26, Pillow 13.0.0, pythonnet 3.2.1, pycparser 3.12, setuptools 84.2.1 und actions/setup-python 7.1.0
- `requirements.txt` enthält nur die direkte Laufzeitabhängigkeit, `requirements-build.txt` zusätzlich PyInstaller und Pillow; indirekte Abhängigkeiten löst pip auf
- Lizenztexte aus den neuen Paketen übernommen; der PyInstaller-Bootloader enthält jetzt zlib 1.3.2, die NETStandard-Fassaden von pythonnet entfallen

## 1.0.1 (26.08.2026)

Erste öffentliche Version.

- Import von `conversations.json` und Design-Chats
- Suche, Vorschau, Zwischenablage und Export mehrerer Chats auf einmal
- Formate ChatGPT-Markdown, vollständiges Markdown und Original-JSON
- Verzweigte Gespräche ohne doppelte Vorgeschichte
- Exporte werden atomar geschrieben und überschreiben keine vorhandenen Dateien
- Einzelne Windows-EXE, die ohne Installation läuft
