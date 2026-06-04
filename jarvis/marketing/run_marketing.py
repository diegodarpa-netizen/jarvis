"""
Punto de entrada principal del Agente de Marketing.
Ejecutar: python run_marketing.py [comando]

Comandos:
  (sin argumento)   → Agente interactivo
  daily             → Briefing diario de mercado
  competidores      → Análisis de competidores
  viral             → Playbook de contenido viral
  meta              → Blueprint de Meta Ads
  todos             → Ejecutar todos los análisis
"""
import sys
import os
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

# Load .env from Jarvis root (handles both Mac path formats)
def _load_dotenv():
    possible_env_paths = [
        Path(__file__).parents[3] / "Jarvis\\.env",
        Path(__file__).parents[3] / ".env",
        Path.home() / "Desktop" / "Jarvis" / "Jarvis\\.env",
    ]
    for env_path in possible_env_paths:
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip()
            return True
    return False

_load_dotenv()


def check_env():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY no está configurada.")
        print("   Agregá al .env: ANTHROPIC_API_KEY=sk-ant-...")
        print("   Obtenela en: console.anthropic.com/settings/keys")
        sys.exit(1)


def main():
    check_env()

    command = sys.argv[1].lower() if len(sys.argv) > 1 else "interactive"

    if command == "daily":
        from market_daily import generate_daily_briefing
        generate_daily_briefing()

    elif command == "competidores":
        from ad_library_scraper import generate_competitor_report
        generate_competitor_report()

    elif command == "competidores-basico":
        from competitor_analyzer import analyze_competitors
        analyze_competitors()

    elif command == "viral":
        from viral_tracker import track_viral_content
        track_viral_content()

    elif command == "meta":
        from meta_optimizer import generate_meta_strategy
        generate_meta_strategy()

    elif command == "whatsapp":
        from whatsapp_leads import print_setup_instructions, list_leads
        cmd2 = sys.argv[2] if len(sys.argv) > 2 else "info"
        if cmd2 == "leads":
            list_leads()
        else:
            print_setup_instructions()

    elif command == "todos":
        print("🚀 Ejecutando análisis completo de marketing...\n")
        from market_daily import generate_daily_briefing
        from competitor_analyzer import analyze_competitors
        from viral_tracker import track_viral_content
        from meta_optimizer import generate_meta_strategy

        print("\n" + "="*60)
        print("1/4 BRIEFING DIARIO")
        print("="*60)
        generate_daily_briefing()

        print("\n" + "="*60)
        print("2/4 ANÁLISIS DE COMPETIDORES")
        print("="*60)
        analyze_competitors()

        print("\n" + "="*60)
        print("3/4 CONTENIDO VIRAL")
        print("="*60)
        track_viral_content()

        print("\n" + "="*60)
        print("4/4 META ADS BLUEPRINT")
        print("="*60)
        generate_meta_strategy()

        print("\n✅ Análisis completo terminado. Revisá los reportes en:")
        print(f"   {Path(__file__).parent / 'reports'}")

    else:
        # Interactive agent
        from marketing_agent import run_interactive_agent
        run_interactive_agent()


if __name__ == "__main__":
    main()
