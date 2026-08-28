$ErrorActionPreference = "Stop"

Write-Host "Validating production files..." -ForegroundColor Cyan

$RequiredFiles = @(
    "api.py",
    "main.py",
    "config.py",
    "Dockerfile",
    "docker-compose.yml",
    "cloud-run.yaml",
    ".dockerignore",
    ".env.example",
    "requirements.txt",
    "scripts\set-webhook.ps1",
    "scripts\delete-webhook.ps1",
    "scripts\run-production.ps1"
)

foreach ($File in $RequiredFiles) {
    if (-not (Test-Path $File)) {
        throw "Missing required file: $File"
    }
}

Write-Host "All production files are present." -ForegroundColor Green
