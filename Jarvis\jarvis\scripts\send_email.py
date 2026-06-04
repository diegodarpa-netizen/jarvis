"""
Jarvis - Email Sender
Envía reportes HTML por email. Soporta SMTP y Resend API.
Uso: python send_email.py --file jarvis/reports/reporte.html [--to email] [--subject "Asunto"]
"""

import argparse
import json
import os
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests no instalado. Ejecutá: pip install requests")
    sys.exit(1)

ROOT = Path(__file__).parent.parent.parent
ENV_FILE = ROOT / ".env"


def load_env() -> dict:
    env = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    env.update(os.environ)
    return env


def send_via_resend(api_key: str, to: str, subject: str, html: str, from_email: str) -> dict:
    resp = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"from": from_email, "to": [to], "subject": subject, "html": html},
        timeout=15
    )
    data = resp.json()
    if resp.status_code in (200, 201):
        return {"success": True, "method": "resend", "id": data.get("id")}
    return {"success": False, "method": "resend", "error": data.get("message", "Unknown error")}


def send_via_smtp(smtp_host: str, smtp_port: int, smtp_user: str, smtp_pass: str,
                  to: str, subject: str, html: str, from_email: str) -> dict:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, [to], msg.as_string())
        return {"success": True, "method": "smtp"}
    except Exception as e:
        return {"success": False, "method": "smtp", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Jarvis Email Sender")
    parser.add_argument("--file", required=True, help="Ruta al archivo HTML del reporte")
    parser.add_argument("--to", help="Email destinatario (override del .env)")
    parser.add_argument("--subject", help="Asunto del email")

    args = parser.parse_args()

    report_path = Path(args.file)
    if not report_path.exists():
        print(json.dumps({"success": False, "error": f"Archivo no encontrado: {args.file}"}))
        sys.exit(1)

    with open(report_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    env = load_env()

    to_email = args.to or env.get("JARVIS_EMAIL_TO", "")
    from_email = env.get("JARVIS_EMAIL_FROM", "jarvis@tudominio.com")
    subject = args.subject or f"Jarvis — Reporte Financiero {datetime.now().strftime('%d/%m/%Y')}"

    if not to_email:
        print(json.dumps({"success": False, "error": "No se configuró JARVIS_EMAIL_TO en .env"}))
        sys.exit(1)

    resend_key = env.get("RESEND_API_KEY", "")
    if resend_key:
        result = send_via_resend(resend_key, to_email, subject, html_content, from_email)
    else:
        smtp_host = env.get("SMTP_HOST", "")
        smtp_port = int(env.get("SMTP_PORT", "465"))
        smtp_user = env.get("SMTP_USER", "")
        smtp_pass = env.get("SMTP_PASS", "")

        if not smtp_host or not smtp_user:
            print(json.dumps({"success": False, "error": "Configurá RESEND_API_KEY o SMTP_* en .env"}))
            sys.exit(1)

        result = send_via_smtp(smtp_host, smtp_port, smtp_user, smtp_pass,
                               to_email, subject, html_content, from_email)

    result["to"] = to_email
    result["subject"] = subject
    result["file"] = str(report_path)
    result["sent_at"] = datetime.utcnow().isoformat()

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
