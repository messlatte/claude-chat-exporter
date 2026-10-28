# Drittanbieter-Hinweise

Der eigene Projektcode steht unter der MIT-Lizenz. Der automatisierte Windows-Build bündelt außerdem Drittanbieterkomponenten. Diese Komponenten bleiben unter ihren jeweiligen Lizenzen; die MIT-Lizenz dieses Projekts ersetzt diese Bedingungen nicht.

Die Versionsangaben stammen aus dem Windows-Build vom 28.10.2026. Indirekte Abhängigkeiten sind in `requirements-build.txt` nicht festgelegt und können in späteren Builds neuer sein.

## Im Windows-Release gebündelt

| Komponente | Version | Lizenz | Lizenztext |
| --- | --- | --- | --- |
| CPython und Standardbibliothek | 3.13.12 | PSF License Agreement und enthaltene Drittanbieterhinweise | [`Python-3.13.12-PSF.txt`](third_party_licenses/Python-3.13.12-PSF.txt), [`Python-3.13.12-Doc-license.rst.txt`](third_party_licenses/Python-3.13.12-Doc-license.rst.txt) |
| OpenSSL | 3.0.18 | Apache-2.0 | [`OpenSSL-3.0.18-Apache-2.0.txt`](third_party_licenses/OpenSSL-3.0.18-Apache-2.0.txt) |
| libffi | 3.4.4 | MIT | [`libffi-3.4.4-MIT.txt`](third_party_licenses/libffi-3.4.4-MIT.txt) |
| pywebview | 6.2.1 | BSD-3-Clause | [`pywebview-BSD-3-Clause.txt`](third_party_licenses/pywebview-BSD-3-Clause.txt) |
| domJSON.js (über pywebview) | 0.1.2 | MIT | [`domJSON-0.1.2-MIT.txt`](third_party_licenses/domJSON-0.1.2-MIT.txt) |
| Native Promise Only (über pywebview) | 0.8.1 | MIT | [`Native-Promise-Only-0.8.1-MIT.txt`](third_party_licenses/Native-Promise-Only-0.8.1-MIT.txt) |
| Symbol-ES6 (über pywebview) | 0.1.2 | MIT | [`Symbol-ES6-0.1.2-MIT.txt`](third_party_licenses/Symbol-ES6-0.1.2-MIT.txt) |
| Microsoft WebView2 SDK-Binärdateien | 1.0.3856.49 | BSD-3-Clause | [`Microsoft-WebView2-1.0.3856.49-BSD-3-Clause.txt`](third_party_licenses/Microsoft-WebView2-1.0.3856.49-BSD-3-Clause.txt) |
| pythonnet | 3.2.1 | MIT | [`pythonnet-3.2.1-MIT.txt`](third_party_licenses/pythonnet-3.2.1-MIT.txt) |
| clr-loader | 0.3.1 | MIT | [`clr-loader-0.3.1-MIT.txt`](third_party_licenses/clr-loader-0.3.1-MIT.txt) |
| cffi | 2.1.1 | MIT-0 | [`cffi-2.1.1-MIT-0.txt`](third_party_licenses/cffi-2.1.1-MIT-0.txt) |
| pycparser | 3.12 | BSD-3-Clause | [`pycparser-3.12-BSD-3-Clause.txt`](third_party_licenses/pycparser-3.12-BSD-3-Clause.txt) |
| proxy-tools | 0.1.0 | BSD-Lizenz gemäß Upstream-`LICENSE.txt` | [`proxy-tools-0.1.0-BSD.txt`](third_party_licenses/proxy-tools-0.1.0-BSD.txt) |
| Bottle | 0.13.4 | MIT | [`bottle-0.13.4-MIT.txt`](third_party_licenses/bottle-0.13.4-MIT.txt) |
| typing-extensions | 4.16.0 | PSF-2.0 | [`typing-extensions-4.16.0-PSF-2.0.txt`](third_party_licenses/typing-extensions-4.16.0-PSF-2.0.txt) |
| PyInstaller-Bootloader und Runtime Hooks | 6.22.3 | GPL-2.0-or-later mit Bootloader Exception; Runtime Hooks Apache-2.0 | [`PyInstaller-GPL-2.0-with-exception.txt`](third_party_licenses/PyInstaller-GPL-2.0-with-exception.txt) |
| zlib-Code im PyInstaller-Bootloader | 1.3.2 | zlib License | [`zlib-1.3.2.txt`](third_party_licenses/zlib-1.3.2.txt) |

Die EXE enthält außerdem `VCRUNTIME140.dll` und `VCRUNTIME140_1.dll` aus der offiziellen CPython-Windows-Laufzeit. Für diese Microsoft-Komponenten gelten die [Microsoft Visual C++ Runtime 2015–2022 Software License Terms](https://visualstudio.microsoft.com/license-terms/vs2022-cruntime/).

Die Microsoft Edge WebView2 Runtime selbst wird nicht mitgeliefert; die App verwendet die auf dem System installierte Runtime.

## Nur für Build und Entwicklung

Diese Komponenten werden für den reproduzierbaren Build oder die Icon-Erzeugung verwendet. Abgesehen von den oben ausdrücklich genannten PyInstaller-Bestandteilen werden sie nicht als eigene Laufzeitpakete in die EXE aufgenommen.

| Komponente | Version | Lizenz | Lizenztext |
| --- | --- | --- | --- |
| altgraph | 0.17.5 | MIT | [`altgraph-0.17.5-MIT.txt`](third_party_licenses/altgraph-0.17.5-MIT.txt) |
| packaging | 26.3 | Apache-2.0 oder BSD-2-Clause | [`Auswahl`](third_party_licenses/packaging-26.3-LICENSE.txt), [`Apache-2.0`](third_party_licenses/packaging-26.3-Apache-2.0.txt), [`BSD-2-Clause`](third_party_licenses/packaging-26.3-BSD-2-Clause.txt) |
| pefile | 2024.8.26 | MIT | [`pefile-2024.8.26-MIT.txt`](third_party_licenses/pefile-2024.8.26-MIT.txt) |
| PyInstaller Community Hooks | 2026.9 | GPL-2.0-or-later; Runtime Hooks Apache-2.0 | [`pyinstaller-hooks-contrib-2026.9.txt`](third_party_licenses/pyinstaller-hooks-contrib-2026.9.txt) |
| pywin32-ctypes | 0.2.3 | BSD-3-Clause | [`pywin32-ctypes-0.2.3-BSD-3-Clause.txt`](third_party_licenses/pywin32-ctypes-0.2.3-BSD-3-Clause.txt) |
| setuptools | 84.2.1 | MIT | [`setuptools-84.2.1-MIT.txt`](third_party_licenses/setuptools-84.2.1-MIT.txt) |
| Pillow | 13.0.0 | MIT-CMU sowie im Paket aufgeführte Drittanbieterbedingungen | [`Pillow-MIT-CMU.txt`](third_party_licenses/Pillow-MIT-CMU.txt) |

Die vollständigen Lizenztexte werden im Quellrepository geführt, in die Ein-Datei-EXE eingebettet und dort über **Lizenzen** angezeigt. Jedes GitHub-Release enthält außerdem das vollständige Paket `Claude-Chat-Exporter-<Version>-with-licenses.zip` mit EXE, Projektlizenz, diesen Hinweisen und allen Drittanbieter-Lizenztexten.
