[CmdletBinding()]
param(
    [string]$PythonExecutable = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = if ([string]::IsNullOrWhiteSpace($PythonExecutable)) {
    Join-Path $projectRoot ".venv\Scripts\python.exe"
}
else {
    (Resolve-Path -LiteralPath $PythonExecutable).Path
}
$distPath = Join-Path $projectRoot "dist"
$workPath = Join-Path $projectRoot "build\pyinstaller"
$specFile = Join-Path $projectRoot "Claude-Chat-Exporter.spec"

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Der Python-Interpreter für den Build fehlt. Bitte zuerst die Abhängigkeiten aus requirements-build.txt installieren."
}
if (-not (Test-Path -LiteralPath $specFile)) {
    throw "Die PyInstaller-Konfiguration fehlt: $specFile"
}

$arguments = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--distpath", $distPath,
    "--workpath", $workPath,
    $specFile
)

Push-Location $projectRoot
try {
    & $venvPython @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller wurde mit Exitcode $LASTEXITCODE beendet."
    }
}
finally {
    Pop-Location
}

$exePath = Join-Path $distPath "Claude-Chat-Exporter.exe"
if (-not (Test-Path -LiteralPath $exePath)) {
    throw "Die erwartete EXE wurde nicht erzeugt: $exePath"
}

$hash = Get-FileHash -LiteralPath $exePath -Algorithm SHA256
Write-Output ("Fertig: " + $exePath)
Write-Output ("SHA-256: " + $hash.Hash)
