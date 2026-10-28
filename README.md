# Claude Chat Exporter

[![CI](https://github.com/messlatte/claude-chat-exporter/actions/workflows/ci.yml/badge.svg)](https://github.com/messlatte/claude-chat-exporter/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/messlatte/claude-chat-exporter)](https://github.com/messlatte/claude-chat-exporter/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Windows-App, die einzelne Chats aus einem Claude-Datenexport herauslöst, etwa um sie in ChatGPT weiterzuführen. Sie liest die `conversations.json` und speichert Chats als Markdown oder als Original-JSON. Alles läuft lokal, die App hat keine Netzwerkfunktionen.

## Download

Unter [Releases](https://github.com/messlatte/claude-chat-exporter/releases/latest) gibt es die EXE, die ohne Installation läuft, und ein ZIP mit derselben EXE und allen Lizenzhinweisen. Die App braucht die Microsoft Edge WebView2 Runtime, die auf aktuellen Windows-Systemen meist schon installiert ist.

Die EXE ist nicht signiert, deshalb zeigt Windows SmartScreen „Unbekannter Herausgeber“. Die Prüfsummen stehen in `SHA256SUMS.txt`.

## Bedienung

1. Bei Claude einen Datenexport anfordern und entpacken.
2. Die EXE starten und die `conversations.json` auswählen. Liegt sie neben der EXE, findet die App sie selbst.
3. Einen Chat anklicken, um die Vorschau zu sehen. Mit dem Haken wählt man Chats für den Export aus.
4. „Für ChatGPT kopieren“ kopiert den offenen Chat, „Exportieren“ speichert alle markierten Chats als einzelne Dateien.

## Formate

- **ChatGPT-Markdown:** sichtbarer Text, Anhänge und Verzweigungen, ohne interne Denk- und Tool-Blöcke.
- **Vollständiges Markdown:** zusätzlich alle Metadaten und technischen Blöcke.
- **Original-JSON:** das unveränderte Chat-Objekt.

Die beiden vollständigen Formate können interne Prompts und Tool-Daten enthalten, also vor dem Weitergeben prüfen. Bei verzweigten Gesprächen steht die gemeinsame Vorgeschichte nur einmal im Export. Vorhandene Dateien überschreibt die App nicht.

## Datenschutz

Die App liest nur die gewählte Datei und, falls vorhanden, den Ordner `design_chats` daneben. Sie merkt sich den letzten Quellpfad, den Ausgabeordner und das Format, sonst nichts. Bitte keine echten Exporte oder Chatinhalte in Issues hochladen.

## Aus dem Quellcode

Voraussetzungen: Windows, Python 3.13 und die WebView2 Runtime.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe run_claude_chat_exporter.py
```

Tests laufen mit `.\.venv\Scripts\python.exe -m unittest discover -s tests`, die EXE baut `.\build_windows.ps1` nach `dist\Claude-Chat-Exporter.exe`.

## Lizenz

[MIT](LICENSE). Die Lizenzen der gebündelten Abhängigkeiten stehen in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) und `third_party_licenses/`, in der App unter „Lizenzen“.

Das Projekt ist nicht mit Anthropic oder OpenAI verbunden. „Claude“ und „ChatGPT“ sind Marken ihrer Inhaber.
