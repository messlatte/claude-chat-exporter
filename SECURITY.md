# Sicherheit

## Unterstützte Versionen

Sicherheitskorrekturen werden für die neueste veröffentlichte Version bereitgestellt.

## Vertrauliche Meldungen

Bitte melde Sicherheits- oder Datenschutzprobleme nicht in einem öffentlichen Issue. Nutze stattdessen die privaten [GitHub Security Advisories](https://github.com/messlatte/claude-chat-exporter/security/advisories/new).

Beschreibe das Problem mit synthetischen Beispieldaten und den notwendigen Reproduktionsschritten. Übermittle niemals einen echten Claude-Datenexport, persönliche Chat-Inhalte, Zugangsdaten oder API-Schlüssel.

Besonders relevant sind:

- unbeabsichtigte Netzwerkübertragung oder Telemetrie;
- Offenlegung versteckter oder technischer Inhalte im kompakten Export;
- Pfadmanipulation und Überschreiben bestehender Dateien;
- unsichere Verarbeitung speziell präparierter JSON-Dateien;
- Zwischenablage- oder Dateiverlust bei großen Exporten.

## Release-Sicherheit

Release-EXEs werden automatisiert aus dem markierten Quellstand gebaut und mit einer SHA-256-Prüfsumme veröffentlicht. Die Binärdateien sind derzeit nicht code-signiert; Windows kann daher eine SmartScreen-Warnung anzeigen.
