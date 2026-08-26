<p align="center">
  <img src="assets/claude-chat-exporter.png" width="96" height="96" alt="Claude Chat Exporter icon">
</p>

# Claude Chat Exporter

[![CI](https://github.com/messlatte/claude-chat-exporter/actions/workflows/ci.yml/badge.svg)](https://github.com/messlatte/claude-chat-exporter/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/messlatte/claude-chat-exporter)](https://github.com/messlatte/claude-chat-exporter/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Eine lokale Windows-App, die einzelne Konversationen aus einem Claude-Datenexport für ChatGPT aufbereitet. Sie liest `conversations.json`, erkennt benachbarte Design-Chats und exportiert jeden gewünschten Chat als gut lesbares Markdown, technisch vollständiges Markdown oder Original-JSON.

Die App verarbeitet die Daten ausschließlich auf dem eigenen Rechner. Sie enthält weder Telemetrie noch Upload- oder Netzwerkfunktionen.

## Download

Die aktuelle Version für Windows 10 und 11 steht unter [Releases](https://github.com/messlatte/claude-chat-exporter/releases/latest) bereit. Für den schnellsten Start kann die einzelne EXE heruntergeladen werden; sie benötigt keine Installation und keine vorhandene Python-Installation. Das ebenfalls angebotene Paket `Claude-Chat-Exporter-<Version>-with-licenses.zip` enthält dieselbe EXE zusammen mit allen Lizenz- und Drittanbieterhinweisen und ist für Archivierung oder Weitergabe die empfohlene Variante. Benötigt wird die auf aktuellen Windows-Systemen üblicherweise vorhandene [Microsoft Edge WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/).

Die EXE ist derzeit nicht digital signiert. Windows SmartScreen kann deshalb „Unbekannter Herausgeber“ anzeigen. Vergleiche bei Bedarf die SHA-256-Prüfsumme mit `SHA256SUMS.txt` im jeweiligen Release.

## Funktionen

- `conversations.json` und einzelne Design-Chat-JSON-Dateien einlesen
- `design_chats` neben `conversations.json` automatisch erkennen
- Chats lokal durchsuchen, filtern und sortieren
- vollständige Vorschau mit Warnungen für sehr große Inhalte
- Kartenklick öffnet nur die Vorschau; das Hakenfeld steuert die Exportauswahl
- aktiven Chat direkt in die Zwischenablage kopieren
- mehrere ausgewählte Chats mit einem Klick in getrennte Dateien exportieren
- Gesprächsverzweigungen ohne wiederholte gemeinsame Vorgeschichte darstellen
- stabile Windows-Dateinamen, kein Überschreiben bestehender Exporte und atomisches Schreiben
- keinerlei Anmeldung, Telemetrie oder Cloud-Verarbeitung
- Projekt- und Drittanbieter-Lizenztexte direkt in der EXE über **Lizenzen** einsehbar

## Bedienung

1. Fordere bei Claude einen Datenexport an und entpacke ihn.
2. Starte die heruntergeladene `Claude-Chat-Exporter-<Version>.exe`.
3. Wähle beim ersten Start die `conversations.json` aus. Liegt sie neben der EXE, wird sie automatisch erkannt.
4. Klicke auf eine Chatkarte, um die Vorschau zu öffnen.
5. Nutze das Hakenfeld, um Chats für einen Datei-Export auszuwählen.
6. Wähle **Für ChatGPT kopieren** für den geöffneten Chat oder **Exportieren** für alle markierten Chats.

Tastatur: `Enter` öffnet einen Chat, die Leertaste markiert ihn für den Export und `Umschalt` + Leertaste markiert einen Bereich.

## Exportformate

| Format | Inhalt | Geeignet für |
| --- | --- | --- |
| ChatGPT-Markdown | Sichtbare Chattexte, extrahierte Anhangsinhalte und Gesprächsverzweigungen; interne Denk- und Toolblöcke werden ausgelassen und gezählt | Einfügen oder Hochladen in ChatGPT |
| Vollständiges Markdown | Lesbarer Verlauf plus vollständige Original-Metadaten und Nachrichtenobjekte, einschließlich technischer Blöcke | Technische Analyse und möglichst vollständiger Kontext |
| Original-JSON | Das unveränderte einzelne Conversation-Objekt | Archivierung und maschinelle Weiterverarbeitung |

Das vollständige Markdown und Original-JSON können interne Prompts, Tool-Daten und andere sensible technische Informationen enthalten. Prüfe Dateien vor einer Weitergabe.

## Datenschutz

Die Anwendung liest nur die ausgewählte Konversationsdatei und optional den benachbarten Ordner `design_chats`. Andere Dateien des Claude-Exports wie `users.json`, `login_history.json`, `memories.json` und Projektdokumente werden nicht automatisch importiert.

Suchindex, Vorschau, Größenberechnung, Zwischenablage und Export laufen lokal. Gespeichert werden lediglich der zuletzt verwendete Quellpfad, Ausgabeordner und das gewählte Format. Details stehen in [PRIVACY.md](PRIVACY.md).

**Wichtig für Beiträge und Bugreports:** Lade niemals einen echten Claude-Datenexport, Chatinhalt oder erzeugte Exportdateien in ein öffentliches Issue hoch. Verwende ausschließlich synthetische Beispieldaten.

## Grenzen

- ChatGPT hat ein Kontextlimit. Sehr große Chats sollten als Datei hochgeladen oder aufgeteilt werden.
- Claude-Dateireferenzen enthalten im Datenexport teilweise nur Dateiname und UUID. Fehlende Binärdateien kann die App nicht rekonstruieren.
- Die bereitgestellte Binärdatei unterstützt zunächst Windows. Die Codebasis ist für einen späteren macOS-Build vorbereitet, benötigt dort aber ein separat erzeugtes und signiertes App-Bundle.
- Microsoft Edge WebView2 Runtime wird benötigt und ist auf aktuellen Windows-Systemen üblicherweise vorhanden.

## Aus dem Quellcode starten

Voraussetzungen: Windows, Python 3.13 und Microsoft Edge WebView2 Runtime.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe run_claude_chat_exporter.py
```

## Tests und Windows-Build

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\build_windows.ps1
```

Die Ein-Datei-EXE wird unter `dist\Claude-Chat-Exporter.exe` erzeugt. Der Build gibt anschließend ihre SHA-256-Prüfsumme aus.

Optional können die Validatoren gegen einen eigenen lokalen Export ausgeführt werden. Die Quelldatei wird dabei nicht verändert:

```powershell
.\.venv\Scripts\python.exe -m scripts.validate_real_export "C:\Pfad\zu\conversations.json"
.\.venv\Scripts\python.exe -m scripts.validate_content_coverage "C:\Pfad\zu\conversations.json"
```

## Projektstruktur

```text
claude_chat_exporter/   Anwendung, Exportlogik und eingebettete Oberfläche
tests/                  Unit- und Regressionstests mit synthetischen Daten
scripts/                Icon-, UI- und Export-Validatoren
assets/                 App-Icon und Windows-Versionsinformationen
.github/workflows/      CI und reproduzierbarer Windows-Release-Build
```

Beiträge sind willkommen; siehe [CONTRIBUTING.md](CONTRIBUTING.md). Sicherheits- und Datenschutzprobleme bitte nach [SECURITY.md](SECURITY.md) melden.

## Lizenz und Markenhinweis

Der eigene Quellcode steht unter der [MIT-Lizenz](LICENSE). Hinweise und Lizenztexte gebündelter Abhängigkeiten stehen in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) und `third_party_licenses/`; sie sind zusätzlich in die Ein-Datei-EXE eingebettet und dort über **Lizenzen** lesbar. Bei einer Weitergabe kann direkt das vollständige `with-licenses.zip` verwendet werden.

Dieses Projekt ist unabhängig und weder mit Anthropic noch mit OpenAI verbunden oder von ihnen unterstützt. „Claude“, „ChatGPT“ und zugehörige Marken gehören ihren jeweiligen Inhabern.
