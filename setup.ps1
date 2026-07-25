# Jarvis - Setup Script (Windows PowerShell)
# Ejecutar con: powershell -ExecutionPolicy Bypass -File setup.ps1

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  JARVIS — Setup Asistente Financiero" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "[1/4] Verificando Python..." -ForegroundColor Yellow
try {
    $pyVersion = python --version 2>&1
    Write-Host "  OK: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python no encontrado. Instalar desde https://python.org" -ForegroundColor Red
    exit 1
}

# 2. Instalar dependencias
Write-Host ""
Write-Host "[2/4] Instalando dependencias Python..." -ForegroundColor Yellow
Set-Location $ROOT
python -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "  ERROR al instalar dependencias" -ForegroundColor Red
    exit 1
}

# 3. Crear .env si no existe
Write-Host ""
Write-Host "[3/4] Configurando variables de entorno..." -ForegroundColor Yellow
$envFile = Join-Path $ROOT ".env"
$envExample = Join-Path $ROOT ".env.example"
if (-not (Test-Path $envFile)) {
    Copy-Item $envExample $envFile
    Write-Host "  OK: .env creado desde .env.example — COMPLETAR LAS CLAVES" -ForegroundColor Yellow
} else {
    Write-Host "  OK: .env ya existe" -ForegroundColor Green
}

# 4. Test rápido
Write-Host ""
Write-Host "[4/4] Probando conexión con Yahoo Finance..." -ForegroundColor Yellow
$testResult = python jarvis\scripts\fetch_market.py SPY --period 5d --no-history 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: Conexión exitosa con Yahoo Finance" -ForegroundColor Green
} else {
    Write-Host "  ADVERTENCIA: No se pudo conectar. Verificar internet o dependencias." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Setup completado." -ForegroundColor Green
Write-Host ""
Write-Host "  Proximos pasos:" -ForegroundColor White
Write-Host "  1. Completar las API keys en .env" -ForegroundColor White
Write-Host "  2. Ejecutar onboarding: python jarvis\scripts\onboarding.py" -ForegroundColor White
Write-Host "  3. Abrir esta carpeta con Claude Code Desktop" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
