"""
Integración WhatsApp Business para seguimiento de leads de cirugía plástica.
Envía mensajes automáticos a leads, recordatorios de consulta y seguimiento post-consulta.
"""
import json
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

CONFIG_PATH = Path(__file__).parent.parent / "data" / "config.json"
LEADS_PATH = Path(__file__).parent.parent / "data" / "leads.json"

WA_TOKEN = os.getenv("META_ACCESS_TOKEN")
WA_API_VERSION = os.getenv("META_API_VERSION", "v21.0")
# El Phone Number ID lo obtenés en Meta Business Suite > WhatsApp > Configuración
WA_PHONE_NUMBER_ID = os.getenv("WA_PHONE_NUMBER_ID", "")


def load_leads():
    if LEADS_PATH.exists():
        return json.loads(LEADS_PATH.read_text())
    return {"leads": []}


def save_leads(data):
    LEADS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def send_whatsapp_message(phone_number: str, message: str) -> dict:
    """Envía un mensaje de texto via WhatsApp Business API."""
    if not WA_PHONE_NUMBER_ID:
        print("⚠️  WA_PHONE_NUMBER_ID no configurado. Ver instrucciones abajo.")
        return {"error": "WA_PHONE_NUMBER_ID requerido"}

    url = f"https://graph.facebook.com/{WA_API_VERSION}/{WA_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WA_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,  # formato: 5491112345678
        "type": "text",
        "text": {"body": message}
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def send_lead_welcome(phone_number: str, name: str, procedure: str) -> dict:
    """Mensaje de bienvenida cuando entra un lead desde Meta Ads."""
    message = f"""Hola {name}! 👋

Gracias por tu consulta sobre *{procedure}*.

Soy del equipo de la clínica y me comunico para coordinar tu consulta gratuita con el especialista.

¿Cuándo tenés disponibilidad? Contamos con turnos de lunes a sábado.

Respondé este mensaje y te ayudo a coordinar todo 😊"""

    return send_whatsapp_message(phone_number, message)


def send_consultation_reminder(phone_number: str, name: str, date: str, time: str) -> dict:
    """Recordatorio 24hs antes de la consulta."""
    message = f"""Hola {name}!

Te recordamos tu consulta mañana *{date} a las {time}*.

📍 Dirección: [tu dirección]
🅿️ Hay estacionamiento disponible

Si necesitás reprogramar, respondé este mensaje.

¡Hasta mañana! 😊"""

    return send_whatsapp_message(phone_number, message)


def send_post_consultation_followup(phone_number: str, name: str, procedure: str) -> dict:
    """Seguimiento 48hs después de la consulta."""
    message = f"""Hola {name}!

Queríamos saber cómo te sentiste después de tu consulta sobre *{procedure}*.

¿Quedaron dudas que podamos responder? ¿Estás considerando avanzar?

Estamos para ayudarte en cada paso del proceso 💙"""

    return send_whatsapp_message(phone_number, message)


def add_lead(name: str, phone: str, procedure: str, source: str = "Meta Ads"):
    """Registra un nuevo lead en el sistema."""
    data = load_leads()
    lead = {
        "id": len(data["leads"]) + 1,
        "name": name,
        "phone": phone,
        "procedure": procedure,
        "source": source,
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "nuevo",
        "notes": []
    }
    data["leads"].append(lead)
    save_leads(data)
    print(f"✅ Lead agregado: {name} - {procedure}")

    # Auto-send welcome message
    if WA_PHONE_NUMBER_ID:
        result = send_lead_welcome(phone, name, procedure)
        print(f"📱 WhatsApp enviado: {result}")
    return lead


def list_leads():
    """Muestra todos los leads registrados."""
    data = load_leads()
    leads = data["leads"]

    if not leads:
        print("No hay leads registrados aún.")
        return

    print(f"\n{'='*60}")
    print(f"LEADS REGISTRADOS: {len(leads)}")
    print(f"{'='*60}")
    for lead in leads:
        print(f"\n#{lead['id']} {lead['name']}")
        print(f"   📱 {lead['phone']}")
        print(f"   💉 {lead['procedure']}")
        print(f"   📊 Estado: {lead['status']}")
        print(f"   📅 {lead['date_added']}")


def print_setup_instructions():
    """Instrucciones para completar la configuración de WhatsApp."""
    print("""
╔══════════════════════════════════════════════════════════╗
║     CONFIGURACIÓN WHATSAPP BUSINESS API                  ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Tu token YA está configurado ✅                         ║
║                                                          ║
║  Solo falta el Phone Number ID:                          ║
║                                                          ║
║  1. Entrá a: business.facebook.com                       ║
║  2. Configuración > WhatsApp > Números de teléfono       ║
║  3. Copiá el "Phone Number ID" (son números)             ║
║  4. Editá el .env y agregá:                              ║
║     WA_PHONE_NUMBER_ID=tu_id_aqui                        ║
║                                                          ║
║  Una vez configurado podés:                              ║
║  - Enviar mensajes automáticos a leads                   ║
║  - Recordatorios de consultas                            ║
║  - Seguimiento post-consulta                             ║
║  - Plantillas aprobadas para campañas masivas            ║
╚══════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "info"

    if cmd == "info":
        print_setup_instructions()
    elif cmd == "leads":
        list_leads()
    elif cmd == "test":
        phone = input("Número de teléfono (ej: 5491112345678): ")
        result = send_whatsapp_message(phone, "Test desde Jarvis Marketing Agent ✅")
        print(f"Resultado: {result}")
    elif cmd == "agregar":
        name = input("Nombre del lead: ")
        phone = input("Teléfono (5491112345678): ")
        procedure = input("Procedimiento: ")
        add_lead(name, phone, procedure)
