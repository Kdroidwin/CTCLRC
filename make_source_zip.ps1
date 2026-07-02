$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$zip = Join-Path $root "CTCLRC-source.zip"
$staging = Join-Path $root "_source_zip"

if (Test-Path -LiteralPath $staging) {
    Remove-Item -LiteralPath $staging -Recurse -Force
}

New-Item -ItemType Directory -Path $staging | Out-Null

$files = @(
    "README.md",
    "align.py",
    "lrc_export.py",
    "main.py",
    "ui.py",
    "requirements.txt",
    "CTCLRC.spec",
    "make_source_zip.ps1"
)

foreach ($file in $files) {
    Copy-Item -LiteralPath (Join-Path $root $file) -Destination $staging
}

if (Test-Path -LiteralPath $zip) {
    Remove-Item -LiteralPath $zip -Force
}

Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $zip -Force
Remove-Item -LiteralPath $staging -Recurse -Force

Write-Host "Created $zip"
