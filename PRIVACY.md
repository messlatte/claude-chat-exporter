# Datenschutz

Claude Chat Exporter ist als lokale Desktop-Anwendung konzipiert. Die Anwendung enthält keine Telemetrie, Analytics, Benutzerkonten, Werbung oder Upload-Funktion.

## Lokal verarbeitete Daten

Nach ausdrücklicher Auswahl kann die App folgende Daten lesen:

- eine `conversations.json` aus einem Claude-Datenexport oder eine einzelne Design-Chat-JSON;
- JSON-Dateien im benachbarten Ordner `design_chats`;
- Metadaten, Nachrichten, Anhänge und Dateireferenzen innerhalb dieser Konversationen.

Die Verarbeitung umfasst lokalen Suchindex, Vorschau, Größenberechnung, Zwischenablage und Dateiexport. Die Quelldateien werden nicht verändert.

## Nicht automatisch gelesene Daten

Andere Bestandteile eines Claude-Datenexports werden bewusst nicht automatisch importiert, darunter `users.json`, `login_history.json`, `memories.json` und der Ordner `projects`.

## Lokale Einstellungen

Unter Windows speichert die App eine kleine Einstellungsdatei unter `%APPDATA%\ClaudeChatExporter\settings.json`. Sie enthält ausschließlich:

- Pfad der zuletzt verwendeten Quelldatei;
- zuletzt verwendeten Ausgabeordner;
- zuletzt gewähltes Exportformat.

Diese Datei kann jederzeit gelöscht werden. Sie wird nicht übertragen.

## Netzwerk

Die Anwendung selbst stellt keine Netzwerkverbindungen her. Externe Links werden in der eingebetteten Oberfläche nicht geöffnet. Der Download einer Release-Datei über GitHub findet außerhalb der Anwendung statt.

## Zwischenablage und Exporte

Beim Kopieren wird der gewählte Chat in die Systemzwischenablage geschrieben. Exportierte Dateien werden ausschließlich im gewählten lokalen Ordner gespeichert. Ab diesem Zeitpunkt entscheidet die verwendende Zielanwendung beziehungsweise der Benutzer über eine mögliche Übertragung.

## Meldung eines Datenschutzproblems

Bitte nutze für vertrauliche Meldungen die privaten [GitHub Security Advisories](https://github.com/messlatte/claude-chat-exporter/security/advisories/new). Füge keinen echten Datenexport und keine persönlichen Chat-Inhalte bei; verwende eine minimierte synthetische Reproduktion.
