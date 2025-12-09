#!/usr/bin/env python3
"""
Backend-Fix-Skript
- Korrigiert den HTTP-Exception-Handler
- Löscht die alte SQLite-DB (falls vorhanden)
- Startet den Server im Dummy-Modus
"""

import os
import sys
from pathlib import Path

def fix_http_exception_handler():
    """Ersetzt den alten HTTPException-Handler durch JSONResponse."""
    main_py = Path("app/main.py")
    
    if not main_py.exists():
        print("❌ app/main.py nicht gefunden")
        sys.exit(1)
    
    content = main_py.read_text()
    
    # Import hinzufügen (falls nicht vorhanden)
    if "from fastapi.responses import JSONResponse" not in content:
        content = content.replace(
            "from pydantic import BaseModel, Field",
            "from pydantic import BaseModel, Field\nfrom fastapi.responses import JSONResponse"
        )
        print("✓ JSONResponse-Import hinzugefügt")
    
    # Alten Handler durch neuen ersetzen
    old_handler = '''@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Strukturierte Error-Response."""
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.utcnow().isoformat(),
    }'''
    
    new_handler = '''@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Strukturierte Error-Response als gültiges FastAPI-Response-Objekt."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )'''
    
    if old_handler in content:
        content = content.replace(old_handler, new_handler)
        print("✓ HTTP-Exception-Handler korrigiert")
    else:
        print("⚠️  Alter Handler nicht gefunden – vielleicht bereits korrigiert")
    
    main_py.write_text(content)
    print("✓ app/main.py gespeichert")

def reset_database():
    """Löscht die alte SQLite-DB, damit Schema neu angelegt wird."""
    db_path = Path("analysis.sqlite")
    
    if db_path.exists():
        db_path.unlink()
        print("✓ Alte analysis.sqlite gelöscht")
    else:
        print("✓ Keine alte DB gefunden – ist okay")

def start_server():
    """Startet Uvicorn im Dummy-Modus."""
    print("\n🚀 Starte Server im Dummy-Modus...")
    os.system("export CONTRACT_ANALYZER_DUMMY=true && uvicorn app.main:app --reload")

if __name__ == "__main__":
    print("=== Contract Analyzer Backend Fix ===\n")
    
    fix_http_exception_handler()
    reset_database()
    
    print("\n=== Setup abgeschlossen ===\n")
    
    # Server starten
    start_server()
