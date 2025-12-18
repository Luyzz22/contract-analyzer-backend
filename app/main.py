# app/main.py
"""
Contract Analyzer API v0.3.1 - Production Ready
Mit Enterprise Frontend, API-Key-Auth, Export-Funktionen und CFO-Dashboard
"""

import os
import csv
import io
import time
import logging
import json
import glob
import shutil
import uuid
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Header, Depends, Request, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Frontend Module
from app.frontend import (
    get_upload_page, 
    get_landing_page, 
    get_history_page, 
    get_analytics_page, 
    get_help_page
)

# Lokale Module
from .pdf_utils import extract_text_from_pdf
from .llm_client import call_employment_contract_model, call_saas_contract_model, LLMError
from .prompts import get_employment_contract_prompt, get_saas_contract_prompt
from .logging_service import setup_logging, log_analysis_event

# Dashboard
try:
    from dashboard import get_dashboard
except ImportError:
    def get_dashboard():
        return "<html><body><h1>Dashboard</h1></body></html>"

# SSO Auth
import sys
sys.path.insert(0, '/var/www/contract-app')
try:
    from shared_auth import verify_sso_token, get_current_user, COOKIE_NAME
    from multi_product_subscriptions import has_product_access, increment_usage, get_user_products
except ImportError:
    COOKIE_NAME = "sbs_session"
    def verify_sso_token(token): return None
    def has_product_access(user_id, product): return {"allowed": True}
    def increment_usage(user_id, product): pass

# Enterprise-Standards
try:
    from enterprise_saas_config import ENTERPRISE_SAAS_STANDARDS, VENDOR_COMPLIANCE_MATRIX
except ImportError:
    ENTERPRISE_SAAS_STANDARDS = None
    VENDOR_COMPLIANCE_MATRIX = None

# ============================================================================
# SETUP
# ============================================================================

logger = logging.getLogger(__name__)
setup_logging()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# API-Keys
API_KEYS = {
    "demo-key-123": "demo-tenant-1",
    "pilot-key-456": "kanzlei-mueller",
    "web-upload-key": "web-frontend",
}

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="SBS Contract Intelligence API",
    version="0.3.1",
    description="Enterprise KI-Vertragsanalyse mit SSO, Export & Dashboard",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# AUTH HELPERS
# ============================================================================

def get_optional_user(request: Request):
    """Holt User aus SSO Cookie (optional)"""
    token = request.cookies.get(COOKIE_NAME)
    if token:
        user = verify_sso_token(token)
        if user:
            return user
    return None

async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verifiziert API-Key und gibt Tenant-ID zurück."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")
    tenant_id = API_KEYS.get(x_api_key)
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return tenant_id

def check_contract_usage(user_id: int) -> dict:
    """Prüft ob User Verträge analysieren darf"""
    access = has_product_access(user_id, "contract")
    if access.get("is_admin"):
        return {"allowed": True, "is_admin": True, "plan": "enterprise"}
    limit = access.get("usage_limit", 3)
    used = access.get("usage_current", 0)
    if limit == -1:
        return {"allowed": True, "plan": access.get("plan"), "used": used, "limit": "∞"}
    if used >= limit:
        return {"allowed": False, "reason": "limit_reached", "plan": access.get("plan"), "used": used, "limit": limit}
    return {"allowed": True, "plan": access.get("plan"), "used": used, "limit": limit, "remaining": limit - used}

# ============================================================================
# DATABASE HELPERS
# ============================================================================

def _get_db_path() -> str:
    return os.getenv("CONTRACTS_DB_PATH", "/var/www/contract-app/data/contracts.db")

def _get_upload_dir() -> str:
    return os.getenv("UPLOAD_DIR", "/var/www/contract-app/uploads")

def _init_db():
    db_path = _get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            contract_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            contract_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL,
            risk_level TEXT,
            risk_score INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            contract_id TEXT PRIMARY KEY,
            analysis_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class RiskFlag(BaseModel):
    severity: str = Field(..., description="low, medium, high, critical")
    title: str
    description: str
    clause_snippet: Optional[str] = None
    policy_reference: Optional[str] = None

class ContractUploadResponse(BaseModel):
    contract_id: str
    filename: str
    message: str = "Upload successful"

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

# ============================================================================
# FRONTEND ROUTES (Enterprise Design)
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Landing Page mit Enterprise Design"""
    return get_landing_page()

@app.get("/upload", response_class=HTMLResponse)
async def upload_page():
    """Upload Page mit 8 Vertragstypen"""
    return get_upload_page()

@app.get("/history", response_class=HTMLResponse)
async def history_page():
    """Verlauf Page"""
    return get_history_page()

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page():
    """Analytics Dashboard"""
    return get_analytics_page()

@app.get("/help", response_class=HTMLResponse)
async def help_page():
    """Hilfe & FAQ"""
    return get_help_page()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """CFO Dashboard"""
    return get_dashboard()

# Placeholder Pages
@app.get("/compare", response_class=HTMLResponse)
async def compare_page():
    return "<html><head><title>Vertragsvergleich</title></head><body><h1>Vertragsvergleich - Coming Soon</h1><a href='/upload'>← Zurück</a></body></html>"

@app.get("/library", response_class=HTMLResponse)
async def library_page():
    return "<html><head><title>Klausel-Bibliothek</title></head><body><h1>Klausel-Bibliothek - Coming Soon</h1><a href='/upload'>← Zurück</a></body></html>"

@app.get("/exports", response_class=HTMLResponse)
async def exports_page():
    return "<html><head><title>Export-Historie</title></head><body><h1>Export-Historie - Coming Soon</h1><a href='/upload'>← Zurück</a></body></html>"

@app.get("/settings", response_class=HTMLResponse)
async def settings_page():
    return "<html><head><title>Einstellungen</title></head><body><h1>Einstellungen - Coming Soon</h1><a href='/upload'>← Zurück</a></body></html>"

@app.get("/billing", response_class=HTMLResponse)
async def billing_page():
    return "<html><head><title>Abrechnung</title></head><body><h1>Abrechnung - Coming Soon</h1><a href='/upload'>← Zurück</a></body></html>"

@app.get("/team", response_class=HTMLResponse)
async def team_page():
    return "<html><head><title>Team</title></head><body><h1>Team - Coming Soon</h1><a href='/upload'>← Zurück</a></body></html>"

@app.get("/audit", response_class=HTMLResponse)
async def audit_page():
    return "<html><head><title>Audit-Log</title></head><body><h1>Audit-Log - Coming Soon</h1><a href='/upload'>← Zurück</a></body></html>"

# ============================================================================
# API V3 ROUTES (Frontend Compatible)
# ============================================================================

@app.get("/api/v3/contracts")
async def api_list_contracts(limit: int = 50):
    """Liste aller Verträge für Frontend"""
    conn = _init_db()
    try:
        rows = conn.execute(
            "SELECT contract_id, filename, contract_type, created_at, status, risk_level, risk_score "
            "FROM contracts ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
    finally:
        conn.close()
    
    items = [{
        "id": r[0],
        "contract_id": r[0],
        "filename": r[1],
        "contract_type": r[2],
        "created_at": r[3],
        "status": r[4],
        "risk_level": r[5] or "low",
        "risk_score": r[6] or 0,
    } for r in rows]
    
    return {"items": items, "contracts": items, "count": len(items)}

@app.post("/api/v3/contracts/upload")
async def api_upload_contract(request: Request):
    """Upload Vertrag - Frontend Compatible"""
    form = await request.form()
    
    # Contract Type extrahieren
    contract_type = form.get("contract_type") or form.get("type") or "general"
    
    # File finden
    uploaded_file = None
    for key, value in form.multi_items():
        if hasattr(value, "filename") and hasattr(value, "file"):
            uploaded_file = value
            break
    
    if not uploaded_file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Speichern
    upload_dir = _get_upload_dir()
    os.makedirs(upload_dir, exist_ok=True)
    
    contract_id = uuid.uuid4().hex
    safe_filename = os.path.basename(uploaded_file.filename or "upload.pdf").replace(" ", "_")
    file_path = os.path.join(upload_dir, f"{contract_id}__{safe_filename}")
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(uploaded_file.file, f)
    
    # In DB speichern
    conn = _init_db()
    try:
        conn.execute(
            "INSERT INTO contracts (contract_id, filename, contract_type, created_at, status) VALUES (?, ?, ?, ?, ?)",
            (contract_id, safe_filename, str(contract_type), datetime.utcnow().isoformat(), "uploaded")
        )
        conn.commit()
    finally:
        conn.close()
    
    logger.info(f"Contract uploaded: {contract_id} - {safe_filename}")
    
    return {
        "contract_id": contract_id,
        "id": contract_id,
        "filename": safe_filename,
        "contract_type": str(contract_type),
        "status": "uploaded",
        "message": "Upload successful"
    }

@app.post("/api/v3/contracts/{contract_id}/analyze")
async def api_analyze_contract(contract_id: str, request: Request):
    """Analysiert Vertrag - mit echter LLM-Analyse"""
    
    # File finden
    upload_dir = _get_upload_dir()
    files = glob.glob(os.path.join(upload_dir, f"{contract_id}__*"))
    
    if not files:
        # Auch altes Format prüfen
        files = glob.glob(os.path.join(upload_dir, f"{contract_id}_*"))
    
    if not files:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    file_path = Path(files[0])
    
    # Contract Type aus DB oder Request
    conn = _init_db()
    row = conn.execute("SELECT contract_type FROM contracts WHERE contract_id = ?", (contract_id,)).fetchone()
    contract_type = row[0] if row else "general"
    
    # Body parsen falls vorhanden
    try:
        body = await request.json()
        if body.get("contract_type"):
            contract_type = body.get("contract_type")
    except:
        pass
    
    # Text extrahieren
    try:
        if file_path.suffix.lower() == ".pdf":
            contract_text = extract_text_from_pdf(file_path)
        else:
            raise HTTPException(status_code=400, detail="Only PDF supported currently")
        
        if not contract_text or len(contract_text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Contract text too short or empty")
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {e}")
    
    # LLM Analyse
    start_time = time.time()
    
    try:
        if contract_type == "employment":
            user_prompt = get_employment_contract_prompt(contract_text)
            raw_result = call_employment_contract_model(user_prompt)
        elif contract_type == "saas":
            user_prompt = get_saas_contract_prompt(contract_text)
            raw_result = call_saas_contract_model(user_prompt)
        else:
            # Allgemeine Analyse
            user_prompt = get_employment_contract_prompt(contract_text)  # Fallback
            raw_result = call_employment_contract_model(user_prompt)
        
        processing_time = time.time() - start_time
        
        # Result aufbereiten
        result = {
            "contract_id": contract_id,
            "source_filename": file_path.name.split("__")[-1] if "__" in file_path.name else file_path.name,
            "contract_type": contract_type,
            "status": "analyzed",
            "processing_time_seconds": round(processing_time, 2),
            "fields_extracted": len(raw_result.get("extracted_fields", {})),
            "fields_total": 42,
            "extracted_data": raw_result.get("extracted_fields", {}),
            "risk_assessment": {
                "overall_risk_level": raw_result.get("overall_risk_level", "medium"),
                "overall_risk_score": raw_result.get("overall_risk_score", 50),
                "executive_summary": raw_result.get("summary", "Vertrag wurde analysiert."),
                "critical_risks": [r for r in raw_result.get("risk_flags", []) if r.get("severity") == "critical"],
                "high_risks": [r for r in raw_result.get("risk_flags", []) if r.get("severity") == "high"],
                "medium_risks": [r for r in raw_result.get("risk_flags", []) if r.get("severity") == "medium"],
                "low_risks": [r for r in raw_result.get("risk_flags", []) if r.get("severity") == "low"],
            }
        }
        
        # Transform risk_flags to expected format
        for risk_list in ["critical_risks", "high_risks", "medium_risks", "low_risks"]:
            for risk in result["risk_assessment"].get(risk_list, []):
                risk["issue_title"] = risk.get("title", "Risiko")
                risk["issue_description"] = risk.get("description", "")
                risk["risk_level"] = risk.get("severity", "medium")
                risk["legal_basis"] = risk.get("policy_reference", "BGB")
                risk["clause_text"] = risk.get("clause_snippet", "")
                risk["recommendation"] = "Bitte prüfen Sie diese Klausel."
        
        # In DB speichern
        try:
            conn.execute(
                "UPDATE contracts SET status = ?, risk_level = ?, risk_score = ? WHERE contract_id = ?",
                ("analyzed", result["risk_assessment"]["overall_risk_level"], result["risk_assessment"]["overall_risk_score"], contract_id)
            )
            conn.execute(
                "INSERT OR REPLACE INTO analysis_results (contract_id, analysis_json, created_at) VALUES (?, ?, ?)",
                (contract_id, json.dumps(result, ensure_ascii=False), datetime.utcnow().isoformat())
            )
            conn.commit()
        finally:
            conn.close()
        
        logger.info(f"Analysis completed: {contract_id} in {processing_time:.2f}s")
        
        return result
        
    except LLMError as e:
        logger.error(f"LLM error: {e}")
        raise HTTPException(status_code=502, detail=f"Analysis failed: {e}")
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

@app.get("/api/v3/contracts/{contract_id}")
async def api_get_contract(contract_id: str):
    """Einzelnen Vertrag abrufen"""
    conn = _init_db()
    try:
        meta = conn.execute(
            "SELECT contract_id, filename, contract_type, created_at, status, risk_level, risk_score FROM contracts WHERE contract_id = ?",
            (contract_id,)
        ).fetchone()
        
        analysis = conn.execute(
            "SELECT analysis_json FROM analysis_results WHERE contract_id = ?",
            (contract_id,)
        ).fetchone()
    finally:
        conn.close()
    
    if not meta:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    result = {
        "contract_id": meta[0],
        "id": meta[0],
        "filename": meta[1],
        "contract_type": meta[2],
        "created_at": meta[3],
        "status": meta[4],
        "risk_level": meta[5],
        "risk_score": meta[6],
    }
    
    if analysis and analysis[0]:
        result["analysis"] = json.loads(analysis[0])
    
    return result

@app.get("/api/v3/contracts/{contract_id}/export/json")
async def api_export_json(contract_id: str):
    """Export als JSON"""
    conn = _init_db()
    try:
        row = conn.execute("SELECT analysis_json FROM analysis_results WHERE contract_id = ?", (contract_id,)).fetchone()
    finally:
        conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="No analysis found")
    
    return StreamingResponse(
        io.BytesIO(row[0].encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=contract_{contract_id}.json"}
    )

@app.get("/api/v3/contracts/{contract_id}/export/pdf")
async def api_export_pdf(contract_id: str):
    """Export als PDF (Placeholder)"""
    # TODO: PDF Generation implementieren
    raise HTTPException(status_code=501, detail="PDF export coming soon")

@app.get("/api/v3/dashboard/summary")
async def api_dashboard_summary():
    """Dashboard KPIs"""
    conn = _init_db()
    try:
        total = conn.execute("SELECT COUNT(*) FROM contracts").fetchone()[0]
        analyzed = conn.execute("SELECT COUNT(*) FROM contracts WHERE status = 'analyzed'").fetchone()[0]
        critical = conn.execute("SELECT COUNT(*) FROM contracts WHERE risk_level = 'critical'").fetchone()[0]
        avg_score = conn.execute("SELECT AVG(risk_score) FROM contracts WHERE risk_score IS NOT NULL").fetchone()[0]
    finally:
        conn.close()
    
    return {
        "total_contracts": total or 0,
        "active_contracts": analyzed or 0,
        "critical_risk_count": critical or 0,
        "avg_risk_score": round(avg_score or 0),
    }

@app.post("/api/v3/clause/explain")
async def api_explain_clause(request: Request):
    """Erklärt eine Vertragsklausel"""
    try:
        body = await request.json()
        clause_text = body.get("clause_text", "")
        contract_type = body.get("contract_type", "general")
    except:
        raise HTTPException(status_code=400, detail="Invalid request body")
    
    if not clause_text:
        raise HTTPException(status_code=400, detail="clause_text required")
    
    # Einfache Analyse (TODO: LLM-basiert)
    return {
        "clause_text": clause_text,
        "risk_level": "medium",
        "explanation": f"Diese Klausel regelt wichtige vertragliche Aspekte. Bei einem {contract_type}-Vertrag sollten Sie besonders auf die rechtlichen Implikationen achten.",
        "legal_assessment": "Die Klausel erscheint grundsätzlich rechtlich zulässig, sollte aber im Kontext des Gesamtvertrags geprüft werden.",
        "related_laws": ["BGB §305", "BGB §307", "AGB-Recht"],
        "recommendations": [
            "Prüfen Sie die Klausel im Gesamtkontext des Vertrags",
            "Bei Unsicherheit rechtliche Beratung einholen",
            "Vergleichen Sie mit Marktstandards"
        ]
    }

# ============================================================================
# HEALTH & MISC
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health Check"""
    return {
        "status": "ok",
        "version": "0.3.1",
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup():
    logger.info("🚀 Contract Intelligence API v0.3.1 starting...")
    logger.info(f"📁 Upload directory: {UPLOAD_DIR.absolute()}")
    
    # DB initialisieren
    _init_db()
    
    dummy_mode = os.getenv("CONTRACT_ANALYZER_DUMMY", "true").lower() == "true"
    if dummy_mode:
        logger.warning("⚠️  DUMMY MODE ENABLED")
    else:
        if os.getenv("OPENAI_API_KEY"):
            logger.info("✅ OpenAI API key configured")
        else:
            logger.error("❌ OPENAI_API_KEY not set")
    
    logger.info(f"✅ {len(API_KEYS)} API keys configured")
    logger.info("✅ Enterprise Frontend loaded")

@app.on_event("shutdown")
async def shutdown():
    logger.info("👋 Contract Intelligence API shutting down...")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
