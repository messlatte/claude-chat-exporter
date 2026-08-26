# Mitwirken

Vielen Dank für das Interesse an Claude Chat Exporter.

## Entwicklungsumgebung

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Pull Requests

1. Erstelle einen kleinen, thematisch klaren Branch.
2. Ergänze für Fehlerkorrekturen einen Regressionstest.
3. Führe die vollständige Testsuite aus.
4. Beschreibe Verhalten, Motivation und manuelle UI-Prüfung im Pull Request.
5. Vermeide unnötige Abhängigkeiten und Netzwerkfunktionen.

## Datenschutzregeln für Beiträge

- Verwende ausschließlich synthetische Konversationen, IDs, Namen und Dateiinhalte.
- Committe niemals `conversations.json`, `users.json`, `login_history.json`, `memories.json`, `design_chats`, `projects` oder erzeugte Exporte.
- Lade keine Screenshots mit echten Chatnamen oder Inhalten hoch.
- Prüfe neue Fehlermeldungen darauf, dass sie keine Chattexte oder vollständigen lokalen Pfade protokollieren.
- Füge keine Telemetrie, versteckten Netzwerkanfragen oder Cloud-Verarbeitung hinzu.

Die `.gitignore` bietet eine zusätzliche Schutzschicht, ersetzt aber nicht die manuelle Prüfung von `git diff --cached` vor jedem Commit.

## Code-Stil

- Python 3.13, Typannotationen und verständliche, kleine Funktionen.
- Benutzertexte sind derzeit deutsch.
- Die Oberfläche bleibt offline und ohne externe Assets.
- Bestehende Quelldaten dürfen niemals mutiert werden.
