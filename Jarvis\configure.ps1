# Jarvis - Configurador interactivo de .env
# Ejecutar con: powershell -ExecutionPolicy Bypass -File configure.ps1

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ENV_FILE = Join-Path $ROOT ".env"
$ENV_EXAMPLE = Join-Path $ROOT ".env.example"

function Write-Header($text) {
    Write-Host ""
    Write-Host "  ============================================" -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor Cyan
    Write-Host "  ============================================" -ForegroundColor Cyan
    Write-Host ""
}

function Ask-Input($prompt, $default = "", $secret = $false) {
    if ($default) {
        $display = "$prompt [$default]"
    } else {
        $display = $prompt
    }
    Write-Host "  $display" -ForegroundColor Yellow -NoNewline
    Write-Host ": " -NoNewline
    if ($secret) {
        $secure = Read-Host -AsSecureString
        $val = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
        )
    } else {
        $val = Read-Host
    }
    if (-not $val -and $default) { $val = $default }
    return $val
}

function Ask-YesNo($prompt, $default = "s") {
    $d = if ($default -eq "s") { "S/n" } else { "s/N" }
    Write-Host "  $prompt ($d)" -ForegroundColor Yellow -NoNewline
    Write-Host ": " -NoNewline
    $val = Read-Host
    if (-not $val) { $val = $default }
    return $val.ToLower() -eq "s"
}

Clear-Host
Write-Host ""
Write-Host "  ╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║     JARVIS — Configuración de variables    ║" -ForegroundColor Cyan
Write-Host "  ╚════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Cargar .env existente si hay
$config = @{}
if (Test-Path $ENV_FILE) {
    Write-Host "  Se encontró un .env existente. Se va a actualizar." -ForegroundColor Green
    Get-Content $ENV_FILE | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $parts = $line.Split("=", 2)
            $config[$parts[0].Trim()] = $parts[1].Trim().Trim('"').Trim("'")
        }
    }
} else {
    Write-Host "  Creando nuevo .env..." -ForegroundColor Yellow
}

# --- NOTICIAS ---
Write-Header "NOTICIAS — NewsAPI"
Write-Host "  NewsAPI agrega cobertura adicional a Yahoo Finance." -ForegroundColor Gray
Write-Host "  Registrarse gratis en: https://newsapi.org" -ForegroundColor Gray
Write-Host ""

$useNewsAPI = Ask-YesNo "¿Tenés una API key de NewsAPI?"
if ($useNewsAPI) {
    $config["NEWSAPI_KEY"] = Ask-Input "API Key de NewsAPI" $config["NEWSAPI_KEY"]
} else {
    $config["NEWSAPI_KEY"] = ""
    Write-Host "  OK — Se usará solo Yahoo Finance para noticias." -ForegroundColor Gray
}

# --- EMAIL ---
Write-Header "EMAIL — Configuración de envío"
Write-Host "  Vamos a configurar Gmail con Contraseña de Aplicación." -ForegroundColor Gray
Write-Host ""
Write-Host "  Para obtener la contraseña de aplicación de Gmail:" -ForegroundColor White
Write-Host "  1. Ir a https://myaccount.google.com/security" -ForegroundColor Gray
Write-Host "  2. Activar verificación en dos pasos (si no está activa)" -ForegroundColor Gray
Write-Host "  3. Buscar 'Contraseñas de aplicaciones'" -ForegroundColor Gray
Write-Host "  4. Crear una para 'Correo' / 'Windows'" -ForegroundColor Gray
Write-Host "  5. Copiar los 16 caracteres generados" -ForegroundColor Gray
Write-Host ""

$gmailUser = Ask-Input "Tu email de Gmail (remitente)" $config["SMTP_USER"]
$gmailPass = Ask-Input "Contraseña de aplicación de Gmail (16 chars)" $config["SMTP_PASS"] -secret $true
$emailTo   = Ask-Input "Email de Diego (destinatario de reportes)" $config["JARVIS_EMAIL_TO"]

$config["SMTP_HOST"] = "smtp.gmail.com"
$config["SMTP_PORT"] = "465"
$config["SMTP_USER"] = $gmailUser
$config["SMTP_PASS"] = $gmailPass
$config["JARVIS_EMAIL_FROM"] = $gmailUser
$config["JARVIS_EMAIL_TO"] = $emailTo
$config["TZ"] = "America/Argentina/Buenos_Aires"

# --- GUARDAR ---
Write-Header "Guardando configuración"

$lines = @(
    "# Jarvis — Variables de entorno (generado por configure.ps1)",
    "# No compartir este archivo",
    "",
    "# Noticias",
    "NEWSAPI_KEY=$($config['NEWSAPI_KEY'])",
    "",
    "# Email — Gmail SMTP",
    "SMTP_HOST=$($config['SMTP_HOST'])",
    "SMTP_PORT=$($config['SMTP_PORT'])",
    "SMTP_USER=$($config['SMTP_USER'])",
    "SMTP_PASS=$($config['SMTP_PASS'])",
    "JARVIS_EMAIL_FROM=$($config['JARVIS_EMAIL_FROM'])",
    "JARVIS_EMAIL_TO=$($config['JARVIS_EMAIL_TO'])",
    "",
    "# Zona horaria",
    "TZ=$($config['TZ'])"
)

$lines | Out-File -FilePath $ENV_FILE -Encoding utf8
Write-Host "  .env guardado en: $ENV_FILE" -ForegroundColor Green

# --- TEST EMAIL ---
Write-Host ""
$testEmail = Ask-YesNo "¿Querés probar el envío de email ahora?"
if ($testEmail) {
    Write-Host ""
    Write-Host "  Probando envío de email..." -ForegroundColor Yellow
    $testHtml = "<html><body style='background:#0d1117;color:#e6edf3;font-family:sans-serif;padding:32px'><h1 style='color:#58a6ff'>Jarvis — Test de Email</h1><p>Si recibís esto, el email está configurado correctamente.</p></body></html>"
    $testFile = Join-Path $ROOT "jarvis\reports\test_email.html"
    $testHtml | Out-File -FilePath $testFile -Encoding utf8
    $result = python "$ROOT\jarvis\scripts\send_email.py" --file $testFile --subject "Jarvis — Test de configuración" 2>&1
    Write-Host $result
    Remove-Item $testFile -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Green
Write-Host "  Configuración completada." -ForegroundColor Green
Write-Host "  Siguiente paso: python jarvis\scripts\onboarding.py" -ForegroundColor White
Write-Host "  ============================================" -ForegroundColor Green
Write-Host ""
