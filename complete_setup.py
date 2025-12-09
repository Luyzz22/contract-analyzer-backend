#!/usr/bin/env python3
"""
Contract Analyzer – Complete Setup
1. Installiert kompatible Libraries für echten LLM-Betrieb
2. Konfiguriert Frontend
3. Testet alle Modi (Employment & SaaS)
4. Startet beide Services
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Führt Shell-Befehl aus und gibt Output zurück."""
    print(f"▶️  {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Fehler: {result.stderr}")
        sys.exit(1)
    return result.stdout

def setup_backend():
    """Backend-Libraries kompatibel machen."""
    print("\n=== 1. Backend Setup ===")
    
    # httpx auf kompatible Version setzen
    run_command("pip install 'httpx==0.27.2'")
    
    # openai aktuell halten
    run_command("pip install 'openai>=1.30.0'")
    
    # requirements speichern
    run_command("pip freeze > requirements.txt")
    
    print("✓ Backend Libraries installiert")

def configure_frontend():
    """Frontend so konfigurieren, dass es das Backend nutzt."""
    print("\n=== 2. Frontend Setup ===")
    
    frontend_dir = Path("../contract-analyzer-frontend")
    
    if not frontend_dir.exists():
        print("❌ Frontend-Verzeichnis nicht gefunden")
        print("   Erwartet: ~/contract-analyzer-frontend")
        return False
    
    # API-Base-URL in .env setzen
    env_file = frontend_dir / ".env"
    env_content = "VITE_API_BASE_URL=http://127.0.0.1:8000\n"
    
    env_file.write_text(env_content)
    print("✓ Frontend .env konfiguriert")
    
    # Installiere Node-Dependencies falls nötig
    package_json = frontend_dir / "package.json"
    if package_json.exists():
        print("📦 Installiere Frontend Dependencies...")
        run_command("npm install", cwd=str(frontend_dir))
    
    return True

def test_all_modes():
    """Testet Employment und SaaS Modus."""
    print("\n=== 3. API Tests ===")
    
    # Backend bereits laufen? Wenn nicht, starten
    try:
        run_command("curl -s http://127.0.0.1:8000/health")
        print("✓ Backend läuft bereits")
    except:
        print("▶️  Starte Backend im Hintergrund...")
        subprocess.Popen(
            ["uvicorn", "app.main:app", "--reload"],
            cwd=".",
            env={**os.environ, "CONTRACT_ANALYZER_DUMMY": "true"}
        )
        # Warte kurz
        import time
        time.sleep(3)
    
    # Test-PDF verwenden (muss im Projekt liegen)
    test_pdf = Path("testvertrag.pdf")
    if not test_pdf.exists():
        raise SystemExit("❌ testvertrag.pdf nicht gefunden – bitte ins Projektverzeichnis legen.")
    
    # 1. Upload
    print("\n▶️  Teste Upload...")
    upload_result = run_command(
        "curl -s -F 'file=@testvertrag.pdf' http://127.0.0.1:8000/contracts/upload"
    )
    
    # contract_id extrahieren
    import json
    upload_data = json.loads(upload_result)
    contract_id = upload_data["contract_id"]
    print(f"✓ Upload erfolgreich: {contract_id}")
    
    # 2. Employment-Analyse
    print("\n▶️  Teste Employment-Analyse...")
    analyze_result = run_command(
        f"curl -s -X POST http://127.0.0.1:8000/contracts/{contract_id}/analyze "
        "-H 'Content-Type: application/json' "
        "-d '{\"contract_type\": \"employment\", \"language\": \"de\"}'"
    )
    try:
        analyze_data = json.loads(analyze_result)
    except Exception:
        print("❌ Employment-Analyse: Keine gültige JSON-Antwort:")
        print(analyze_result)
        raise SystemExit(1)

    if "summary" not in analyze_data:
        print("❌ Employment-Analyse fehlgeschlagen, Antwort ohne 'summary':")
        print(analyze_data)
        raise SystemExit(1)

    print("✓ Employment-Analyse erfolgreich")
    print(f"   Summary: {analyze_data['summary'][:80]}...")
    print(f"   Risiken: {len(analyze_data.get('risk_flags', []))} gefunden")
    
    # 3. SaaS-Analyse (mit gleichem PDF, simuliert)
    print("\n▶️  Teste SaaS-Analyse...")
    analyze_result_saas = run_command(
        f"curl -s -X POST http://127.0.0.1:8000/contracts/{contract_id}/analyze "
        "-H 'Content-Type: application/json' "
        "-d '{\"contract_type\": \"saas\", \"language\": \"de\"}'"
    )
    analyze_data_saas = json.loads(analyze_result_saas)
    print(f"✓ SaaS-Analyse erfolgreich")
    print(f"   Summary: {analyze_data_saas['summary'][:80]}...")
    
    return True

def start_services():
    """Startet Backend und Frontend."""
    print("\n=== 4. Services starten ===")
    
    # Backend starten (im Hintergrund)
    print("▶️  Starte Backend...")
    backend_process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--reload", "--port", "8000"],
        cwd=".",
        env={**os.environ, "CONTRACT_ANALYZER_DUMMY": "true"}
    )
    
    # Frontend starten (im Hintergrund)
    frontend_dir = Path("../contract-analyzer-frontend")
    if frontend_dir.exists():
        print("▶️  Starte Frontend...")
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(frontend_dir)
        )
        
        print("\n✅ Services laufen:")
        print("   Backend:  http://127.0.0.1:8000")
        print("   Frontend: http://localhost:5173")
        print("   Swagger:  http://127.0.0.1:8000/docs")
    else:
        print("⚠️  Frontend nicht gefunden, nur Backend gestartet")
    
    print("\nPress Ctrl+C zum Beenden")

if __name__ == "__main__":
    print("🚀 Contract Analyzer – Complete Setup")
    print("=" * 50)
    
    setup_backend()
    
    if configure_frontend():
        test_all_modes()
    
    start_services()
