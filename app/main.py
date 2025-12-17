# app/main.py
"""
Contract Analyzer API v0.3.0 - Production Ready
Mit API-Key-Auth, Export-Funktionen, Feedback-System und CFO-Dashboard
"""

import os
import csv
import io
import time
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from uuid import uuid4
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.frontend import get_upload_page, get_landing_page, get_history_page, get_analytics_page, get_help_page

from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field

# Lokale Module
from .pdf_utils import extract_text_from_pdf
from .llm_client import call_employment_contract_model, call_saas_contract_model, LLMError
from .prompts import get_employment_contract_prompt, get_saas_contract_prompt
from .logging_service import setup_logging, log_analysis_event
from dashboard import get_dashboard

# SSO Auth für Cross-Domain Login
import sys
sys.path.insert(0, '/var/www/contract-app')
from shared_auth import verify_sso_token, get_current_user, COOKIE_NAME
import sys
sys.path.insert(0, '/var/www/contract-app')
from multi_product_subscriptions import has_product_access, increment_usage, get_user_products

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
# ============================================================================
# SSO AUTH DEPENDENCY
# ============================================================================

from fastapi import Request, Cookie

def get_optional_user(request: Request):
    """Holt User aus SSO Cookie (optional)"""
    token = request.cookies.get(COOKIE_NAME)
    if token:
        user = verify_sso_token(token)
        if user:
            return user
    return None

def require_auth(request: Request):
    """Erzwingt SSO Auth - Redirect zu Login wenn nicht eingeloggt"""
    user = get_optional_user(request)
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(
            url=f"https://app.sbsdeutschland.com/login?next={request.url}",
            status_code=303
        )
    return user



app = FastAPI(
    title="Contract Analyzer API",
    version="0.3.0",
    description="Production-Ready Backend für KI-gestützte Vertragsanalyse mit Auth, Export & Dashboard",
    docs_url="/docs",
    openapi_url="/openapi.json",
)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def landing():
    return get_landing_page()

@app.get("/upload", response_class=HTMLResponse)
async def upload():
    return get_upload_page()

# ============================================================================
# ROOT ROUTE
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Startseite mit Weiterleitung zu Dashboard oder Docs"""
    return """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SBS Vertragsanalyse API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
        }
        .container {
            text-align: center;
            padding: 48px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 24px;
            max-width: 500px;
        }
        h1 { font-size: 2rem; margin-bottom: 8px; }
        .version { color: rgba(255,255,255,0.5); margin-bottom: 24px; }
        .status { 
            display: inline-flex; 
            align-items: center; 
            gap: 8px;
            padding: 8px 16px;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 999px;
            color: #10b981;
            font-size: 0.85rem;
            margin-bottom: 32px;
        }
        .status::before {
            content: '';
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .links { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }
        a {
            padding: 12px 24px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            text-decoration: none;
            border-radius: 999px;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        a:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4);
        }
        a.secondary {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 SBS Vertragsanalyse</h1>
        <p class="version">API v0.3.0</p>
        <div class="status">System Online</div>
        <div class="links">
            <a href="/upload">Vertrag hochladen</a>
            <a href="/docs" class="secondary">API Docs</a>
        </div>
    </div>
</body>
</html>
    """

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def check_contract_usage(user_id: int) -> dict:
    """Prüft ob User Verträge analysieren darf"""
    access = has_product_access(user_id, "contract")
    
    if access.get("is_admin"):
        return {"allowed": True, "is_admin": True, "plan": "enterprise"}
    
    limit = access.get("usage_limit", 3)
    used = access.get("usage_current", 0)
    
    # -1 = unlimited
    if limit == -1:
        return {"allowed": True, "plan": access.get("plan"), "used": used, "limit": "∞"}
    
    if used >= limit:
        return {
            "allowed": False, 
            "reason": "limit_reached",
            "plan": access.get("plan"),
            "used": used,
            "limit": limit
        }
    
    return {
        "allowed": True,
        "plan": access.get("plan"),
        "used": used,
        "limit": limit,
        "remaining": limit - used
    }


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# API-Keys (in Production aus Env oder DB laden)
API_KEYS = {
    "demo-key-123": "demo-tenant-1",
    "pilot-key-456": "kanzlei-mueller",
}

# ============================================================================
# AUTHENTICATION
# ============================================================================

async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verifiziert API-Key und gibt Tenant-ID zurück."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")
    
    tenant_id = API_KEYS.get(x_api_key)
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return tenant_id

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class RiskFlag(BaseModel):
    severity: str = Field(..., description="low, medium, oder high")
    title: str = Field(..., description="Kurze deutsche Risiko-Bezeichnung")
    description: str = Field(..., description="Erklärung des Risikos")
    clause_snippet: Optional[str] = Field(None, description="Direkter Zitat aus Vertrag")
    policy_reference: Optional[str] = Field(None, description="z.B. BGB §623, Policy-Name")

class EmploymentExtractedFields(BaseModel):
    parties: List[dict] = Field(default=[], description="[{name, role}]")
    start_date: Optional[str] = None
    fixed_term: bool = False
    end_date: Optional[str] = None
    probation_period_months: Optional[float] = None
    weekly_hours: Optional[float] = None
    base_salary_eur: Optional[float] = None
    vacation_days_per_year: Optional[int] = None
    notice_period_employee: Optional[str] = None
    notice_period_employer: Optional[str] = None
    non_compete_during_term: bool = False
    post_contract_non_compete: bool = False

class SaaSExtractedFields(BaseModel):
    customer_name: Optional[str] = None
    vendor_name: Optional[str] = None
    contract_start_date: Optional[str] = None
    contract_end_date: Optional[str] = None
    auto_renew: Optional[bool] = None
    renewal_notice_days: Optional[float] = None
    annual_contract_value_eur: Optional[float] = None
    billing_interval: Optional[str] = None
    min_term_months: Optional[float] = None
    termination_for_convenience: Optional[bool] = None
    data_location: Optional[str] = None
    dp_addendum_included: Optional[bool] = None
    liability_cap_multiple_acv: Optional[float] = None
    uptime_sla_percent: Optional[float] = None

class ContractAnalysisResult(BaseModel):
    contract_id: str
    contract_type: str = Field(..., description="employment oder saas")
    language: str = "de"
    summary: str = Field(..., description="2-4 Sätze Zusammenfassung")
    extracted_fields: dict = Field(..., description="Strukturierte Daten")
    risk_flags: List[RiskFlag] = Field(default=[], description="Identifizierte Risiken")

class ContractUploadResponse(BaseModel):
    contract_id: str
    filename: str
    message: str = "File uploaded successfully. Use /contracts/{contract_id}/analyze to analyze."

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

class FeedbackRequest(BaseModel):
    is_correct: bool = Field(..., description="War die Analyse korrekt?")
    comment: Optional[str] = Field(None, description="Optional: Kommentar")

# ============================================================================
# ENDPOINTS: Health & Metadata
# ============================================================================

@app.get("/health", response_model=HealthResponse)
def health():
    """Health-Check Endpoint."""
    return {
        "status": "ok",
        "version": "0.3.0",
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/contracts")
def list_contracts(tenant_id: str = Depends(verify_api_key)):
    """Listet alle Verträge für einen Tenant."""
    files = list(UPLOAD_DIR.glob("*"))
    contracts = []
    for f in files:
        contract_id = f.name.split("_")[0]
        contracts.append({
            "contract_id": contract_id,
            "filename": f.name,
            "uploaded_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })
    return {"tenant_id": tenant_id, "contracts": contracts, "count": len(contracts)}

# ============================================================================
# ENDPOINTS: Upload & Analyse
# ============================================================================

@app.post("/contracts/upload", response_model=ContractUploadResponse)
async def upload_contract(file: UploadFile = File(...), tenant_id: str = Depends(verify_api_key)):
    """Lädt einen Vertrag hoch. Requires: X-API-Key Header"""
    allowed_types = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
    
    if file.size and file.size > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 20MB)")
    
    contract_id = str(uuid4())
    dest = UPLOAD_DIR / f"{contract_id}_{file.filename}"
    
    try:
        with dest.open("wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
        
        logger.info(f"Contract uploaded: {contract_id} by {tenant_id}, filename: {file.filename}")
        return ContractUploadResponse(contract_id=contract_id, filename=file.filename)
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

@app.post("/contracts/{contract_id}/analyze", response_model=ContractAnalysisResult)
def analyze_contract(
    contract_id: str,
    contract_type: str = Body("employment", embed=True),
    language: str = Body("de", embed=True),
    tenant_id: str = Depends(verify_api_key)
):
    """Analysiert einen Vertrag. Requires: X-API-Key Header"""
    
    files = list(UPLOAD_DIR.glob(f"{contract_id}_*"))
    if not files:
        log_analysis_event(contract_id=contract_id, tenant_id=tenant_id, contract_type=contract_type, language=language, status="error", duration_ms=0, llm_model="gpt-4o-mini", error_message="Contract not found")
        raise HTTPException(status_code=404, detail="Contract not found")
    
    file_path = files[0]
    
    if file_path.suffix.lower() not in [".pdf", ".docx", ".doc"]:
        raise HTTPException(status_code=400, detail="Only PDF/DOCX supported")
    
    if contract_type not in ["employment", "saas"]:
        raise HTTPException(status_code=400, detail="contract_type must be 'employment' or 'saas'")
    
    try:
        if file_path.suffix.lower() == ".pdf":
            contract_text = extract_text_from_pdf(file_path)
        else:
            raise HTTPException(status_code=501, detail="DOCX support coming soon")
        
        if not contract_text or len(contract_text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Contract text too short or empty")
        
        logger.info(f"Text extracted for {contract_id}, {len(contract_text)} chars")
    
    except Exception as e:
        logger.error(f"Text extraction failed for {contract_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {e}")
    
    start_time_ms = int(time.time() * 1000)
    
    try:
        if contract_type == "employment":
            user_prompt = get_employment_contract_prompt(contract_text)
            raw_result = call_employment_contract_model(user_prompt)
        else:
            user_prompt = get_saas_contract_prompt(contract_text)
            raw_result = call_saas_contract_model(user_prompt)
        
        raw_result["contract_id"] = contract_id
        raw_result["contract_type"] = contract_type
        raw_result["language"] = language
        
        result = ContractAnalysisResult(**raw_result)
        duration_ms = int(time.time() * 1000) - start_time_ms
        
        if ENTERPRISE_SAAS_STANDARDS:
            enterprise_risks = [r for r in result.risk_flags if r.severity == 'high']
            if enterprise_risks:
                logger.warning(f"⚠️  {len(enterprise_risks)} Enterprise-Risiken gefunden für {contract_id}")
        
        log_analysis_event(contract_id=contract_id, tenant_id=tenant_id, contract_type=contract_type, language=language, status="success", duration_ms=duration_ms, llm_model="gpt-4o-mini", num_risk_flags=len(result.risk_flags), error_message=None)
        
        logger.info(f"Analysis completed: {contract_id} ({contract_type}) by {tenant_id}, {duration_ms}ms, {len(result.risk_flags)} risk flags")
        
        return result
    
    except LLMError as e:
        duration_ms = int(time.time() * 1000) - start_time_ms
        log_analysis_event(contract_id=contract_id, tenant_id=tenant_id, contract_type=contract_type, language=language, status="error", duration_ms=duration_ms, llm_model="gpt-4o-mini", error_message=f"LLM error: {e}")
        logger.error(f"LLM error for {contract_id}: {e}")
        raise HTTPException(status_code=502, detail=f"LLM analysis failed: {e}")
    
    except Exception as e:
        duration_ms = int(time.time() * 1000) - start_time_ms
        log_analysis_event(contract_id=contract_id, tenant_id=tenant_id, contract_type=contract_type, language=language, status="error", duration_ms=duration_ms, llm_model="gpt-4o-mini", error_message=str(e))
        logger.error(f"Unexpected error for {contract_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

# ============================================================================
# ENDPOINTS: Export
# ============================================================================

@app.get("/contracts/{contract_id}/export/json")
def export_analysis_json(contract_id: str, tenant_id: str = Depends(verify_api_key)):
    """Exportiert Analyse als JSON. Requires: X-API-Key"""
    import sqlite3
    
    try:
        conn = sqlite3.connect("analysis.sqlite")
        conn.row_factory = sqlite3.Row
        
        row = conn.execute("SELECT * FROM analysis_log WHERE contract_id = ? AND status = 'success' ORDER BY created_at DESC LIMIT 1", (contract_id,)).fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="No successful analysis found")
        
        data = dict(row)
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        return StreamingResponse(io.BytesIO(json_str.encode("utf-8")), media_type="application/json", headers={"Content-Disposition": f"attachment; filename=contract_{contract_id}_analysis.json"})
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export failed for {contract_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")

@app.get("/contracts/{contract_id}/export/csv")
def export_analysis_csv(contract_id: str, tenant_id: str = Depends(verify_api_key)):
    """Exportiert Analyse als CSV. Requires: X-API-Key"""
    import sqlite3
    
    try:
        conn = sqlite3.connect("analysis.sqlite")
        conn.row_factory = sqlite3.Row
        
        row = conn.execute("SELECT * FROM analysis_log WHERE contract_id = ? AND status = 'success' ORDER BY created_at DESC LIMIT 1", (contract_id,)).fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="No successful analysis found")
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(row.keys())
        writer.writerow([str(v) for v in row])
        
        csv_content = output.getvalue()
        
        return StreamingResponse(io.BytesIO(csv_content.encode("utf-8")), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=contract_{contract_id}_analysis.csv"})
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export failed for {contract_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")

# ============================================================================
# ENDPOINTS: Feedback
# ============================================================================

@app.post("/contracts/{contract_id}/feedback")
def submit_feedback(contract_id: str, feedback: FeedbackRequest, tenant_id: str = Depends(verify_api_key)):
    """Gibt Feedback zu einer Analyse. Requires: X-API-Key"""
    import sqlite3
    
    try:
        conn = sqlite3.connect("analysis.sqlite")
        
        conn.execute("""CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            contract_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            comment TEXT
        )""")
        
        conn.execute("INSERT INTO feedback (contract_id, tenant_id, is_correct, comment) VALUES (?, ?, ?, ?)", (contract_id, tenant_id, feedback.is_correct, feedback.comment))
        conn.commit()
        conn.close()
        
        logger.info(f"Feedback received for {contract_id} by {tenant_id}: {'✓' if feedback.is_correct else '✗'}")
        
        return {"message": "Feedback received. Thank you!", "contract_id": contract_id}
    
    except Exception as e:
        logger.error(f"Feedback submission failed: {e}")
        raise HTTPException(status_code=500, detail=f"Feedback submission failed: {e}")

# ============================================================================
# ENDPOINTS: Raw Text & Dashboard
# ============================================================================

@app.get("/contracts/{contract_id}/raw-text")
def get_contract_text(contract_id: str, tenant_id: str = Depends(verify_api_key)):
    """Gibt Rohtext zurück. Requires: X-API-Key"""
    files = list(UPLOAD_DIR.glob(f"{contract_id}_*"))
    if not files:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    file_path = files[0]
    
    if file_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF supported")
    
    try:
        text = extract_text_from_pdf(file_path)
        return {"contract_id": contract_id, "text": text[:5000], "total_length": len(text)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {e}")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """CFO Dashboard (öffentlich)."""
    return get_dashboard()

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail, "status_code": exc.status_code, "timestamp": datetime.utcnow().isoformat()})

# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    logger.info(f"Contract Analyzer API startup (v0.3.0)")
    logger.info(f"Upload directory: {UPLOAD_DIR.absolute()}")
    
    dummy_mode = os.getenv("CONTRACT_ANALYZER_DUMMY", "true").lower() == "true"
    if dummy_mode:
        logger.warning("⚠️  DUMMY MODE ENABLED")
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("❌ OPENAI_API_KEY not set")
        else:
            logger.info("✓ OPENAI_API_KEY configured")
    
    logger.info(f"✓ {len(API_KEYS)} API keys configured")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Contract Analyzer API shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")


# ============================================================================
# UPLOAD FRONTEND
# ============================================================================



@app.post("/web/analyze/{contract_id}")
async def web_analyze_contract(
    contract_id: str,
    request: Request,
    contract_type: str = Body("employment", embed=True),
    language: str = Body("de", embed=True),
):
    """Web-basierte Vertragsanalyse mit SSO und Usage Tracking"""
    
    # SSO Check
    user = get_optional_user(request)
    user_id = None
    
    if user:
        user_id = user.get("user_id")
        
        # Usage Check
        usage = check_contract_usage(user_id)
        if not usage.get("allowed"):
            raise HTTPException(
                status_code=429, 
                detail=f"Monatliches Limit erreicht ({usage.get('used')}/{usage.get('limit')}). Bitte upgraden Sie Ihren Plan."
            )
    
    # Datei finden
    files = list(UPLOAD_DIR.glob(f"{contract_id}_*"))
    if not files:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    file_path = files[0]
    
    if file_path.suffix.lower() not in [".pdf", ".docx", ".doc"]:
        raise HTTPException(status_code=400, detail="Only PDF/DOCX supported")
    
    if contract_type not in ["employment", "saas"]:
        raise HTTPException(status_code=400, detail="contract_type must be 'employment' or 'saas'")
    
    try:
        if file_path.suffix.lower() == ".pdf":
            contract_text = extract_text_from_pdf(file_path)
        else:
            raise HTTPException(status_code=501, detail="DOCX support coming soon")
        
        if not contract_text or len(contract_text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Contract text too short or empty")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {e}")
    
    start_time_ms = int(time.time() * 1000)
    
    try:
        if contract_type == "employment":
            user_prompt = get_employment_contract_prompt(contract_text)
            raw_result = call_employment_contract_model(user_prompt)
        else:
            user_prompt = get_saas_contract_prompt(contract_text)
            raw_result = call_saas_contract_model(user_prompt)
        
        raw_result["contract_id"] = contract_id
        raw_result["contract_type"] = contract_type
        
        duration_ms = int(time.time() * 1000) - start_time_ms
        
        # Usage incrementieren wenn User eingeloggt
        if user_id:
            increment_usage(user_id, "contract")
            logger.info(f"✅ Usage incremented for user {user_id}")
        
        logger.info(f"Web analysis completed: {contract_id}, duration: {duration_ms}ms")
        
        return raw_result
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Upload-Frontend für Vertragsanalyse (mit optionalem SSO-User)"""
    user = get_optional_user(request)
    
    # User-Info für Template
    user_name = user.get("name", "Account") if user else None
    user_email = user.get("email", "") if user else None
    is_logged_in = user is not None
    
    return f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vertrag analysieren | SBS Deutschland</title>
    <link rel="icon" href="https://sbsdeutschland.com/static/favicon.ico">
    <link rel="stylesheet" href="https://sbsdeutschland.com/static/css/design-tokens.css">
    <link rel="stylesheet" href="https://sbsdeutschland.com/static/css/components.css">
    <link rel="stylesheet" href="https://sbsdeutschland.com/static/css/main.css">
    <link rel="stylesheet" href="https://sbsdeutschland.com/static/css/flyout-menu.css">
    <style>
        .upload-hero {{
            background: linear-gradient(135deg, #003856 0%, #00507a 100%);
            padding: 120px 24px 60px;
            text-align: center;
            position: relative;
        }}
        .upload-hero::before {{
            content: '';
            position: absolute;
            inset: 0;
            background-image: radial-gradient(rgba(255,255,255,0.08) 1px, transparent 1px);
            background-size: 30px 30px;
            pointer-events: none;
        }}
        .upload-hero h1 {{
            font-size: 2.2rem;
            color: #fff;
            margin-bottom: 12px;
        }}
        .upload-hero p {{
            color: rgba(255,255,255,0.8);
            max-width: 500px;
            margin: 0 auto;
        }}
        .upload-container {{
            max-width: 700px;
            margin: -40px auto 60px;
            padding: 0 24px;
            position: relative;
            z-index: 10;
        }}
        .upload-card {{
            background: #fff;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            padding: 40px;
        }}
        .upload-zone {{
            border: 2px dashed #cbd5e1;
            border-radius: 16px;
            padding: 48px 32px;
            text-align: center;
            background: #f8fafc;
            transition: all 0.3s;
            cursor: pointer;
        }}
        .upload-zone:hover, .upload-zone.dragover {{
            border-color: #22d3ee;
            background: rgba(34, 211, 238, 0.05);
        }}
        .upload-zone.has-file {{
            border-color: #10b981;
            background: rgba(16, 185, 129, 0.05);
        }}
        .upload-icon {{ font-size: 3rem; margin-bottom: 16px; }}
        .upload-text {{ font-size: 1.1rem; color: #003856; margin-bottom: 8px; font-weight: 600; }}
        .upload-hint {{ font-size: 0.9rem; color: #64748b; }}
        .file-input {{ display: none; }}
        .file-name {{
            margin-top: 16px;
            padding: 12px 20px;
            background: rgba(16, 185, 129, 0.1);
            border-radius: 8px;
            color: #059669;
            font-weight: 500;
            display: none;
        }}
        .file-name.show {{ display: inline-block; }}
        .contract-type {{
            margin-top: 24px;
            display: flex;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        .type-btn {{
            padding: 12px 24px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            background: #fff;
            color: #64748b;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
        }}
        .type-btn:hover {{ border-color: #003856; color: #003856; }}
        .type-btn.active {{
            border-color: #003856;
            background: #003856;
            color: #fff;
        }}
        .analyze-btn {{
            margin-top: 32px;
            width: 100%;
            padding: 16px 32px;
            background: linear-gradient(135deg, #003856, #00507a);
            color: #fff;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .analyze-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 56, 86, 0.3);
        }}
        .analyze-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }}
        .result-section {{
            margin-top: 32px;
            padding: 24px;
            background: #f8fafc;
            border-radius: 12px;
            display: none;
        }}
        .result-section.show {{ display: block; }}
        .result-section h3 {{
            color: #003856;
            margin-bottom: 16px;
            font-size: 1.2rem;
        }}
        .result-item {{
            padding: 12px 0;
            border-bottom: 1px solid #e2e8f0;
        }}
        .result-item:last-child {{ border-bottom: none; }}
        .result-label {{
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 4px;
        }}
        .result-value {{
            color: #003856;
            font-weight: 500;
        }}
        .error-message {{
            margin-top: 16px;
            padding: 16px;
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            color: #dc2626;
            display: none;
        }}
        .error-message.show {{ display: block; }}
        .trust-bar {{
            background: #f8fafc;
            padding: 24px;
            text-align: center;
        }}
        .trust-items {{
            display: flex;
            justify-content: center;
            gap: 32px;
            flex-wrap: wrap;
        }}
        .trust-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: #64748b;
            font-size: 0.9rem;
        }}
        .trust-item strong {{ color: #003856; }}
    </style>
</head>
<body>
<header class="header">
    <div class="header-inner">
        <a href="https://sbsdeutschland.com/sbshomepage/" class="logo-wrap">
            <img src="https://sbsdeutschland.com/static/sbs-logo-new.png" alt="SBS Deutschland" class="logo-img">
            <div class="logo-text">
                <strong>SBS Deutschland</strong>
                <span>Smart Business Service · Weinheim</span>
            </div>
        </a>
        <nav class="nav" id="nav">
            <div class="dropdown">
                <span class="dropdown-toggle">Lösungen</span>
                <div class="dropdown-menu">
                    <a href="https://sbsdeutschland.com/static/landing/">🧾 KI-Rechnungsverarbeitung</a>
                    <a href="https://sbsdeutschland.com/loesungen/vertragsanalyse/">📋 KI-Vertragsanalyse</a>
                </div>
            </div>
            <div class="dropdown">
                <span class="dropdown-toggle">Preise</span>
                <div class="dropdown-menu">
                    <a href="https://sbsdeutschland.com/static/preise/">🧾 Rechnungsverarbeitung</a>
                    <a href="https://sbsdeutschland.com/loesungen/vertragsanalyse/preise.html">📋 Vertragsanalyse</a>
                </div>
            </div>
            <div class="auth-section">
                {"<div class='auth-user'><a href='https://app.sbsdeutschland.com/dashboard' style='color:#003856;font-weight:600;text-decoration:none;'>👤 " + user_name + "</a></div>" if is_logged_in else "<a href='https://app.sbsdeutschland.com/login' class='nav-link-login'>Login</a>"}
            </div>
        </nav>
    </div>
</header>

<section class="upload-hero">
    <h1>📋 Vertrag analysieren</h1>
    <p>Laden Sie Ihren Vertrag hoch und erhalten Sie eine KI-gestützte Analyse in Sekunden.</p>
</section>

<div class="upload-container">
    <div class="upload-card">
        <div class="upload-zone" id="uploadZone">
            <div class="upload-icon">📄</div>
            <div class="upload-text">PDF-Datei hierher ziehen</div>
            <div class="upload-hint">oder klicken zum Auswählen (max. 10 MB)</div>
            <input type="file" class="file-input" id="fileInput" accept=".pdf,.docx,.doc">
        </div>
        <div class="file-name" id="fileName"></div>
        
        <div class="contract-type">
            <button class="type-btn active" data-type="employment">👔 Arbeitsvertrag</button>
            <button class="type-btn" data-type="saas">☁️ SaaS-Vertrag</button>
        </div>
        
        <button class="analyze-btn" id="analyzeBtn" disabled>Vertrag analysieren</button>
        
        <div class="error-message" id="errorMessage"></div>
        
        <div class="result-section" id="resultSection">
            <h3>✅ Analyse-Ergebnis</h3>
            <div id="resultContent"></div>
        </div>
    </div>
</div>

<div class="trust-bar">
    <div class="trust-items">
        <div class="trust-item">🇩🇪 Made in Germany</div>
        <div class="trust-item"><strong>DSGVO</strong> konform</div>
        <div class="trust-item"><strong>GPT-4o</strong> powered</div>
        <div class="trust-item">🔒 Sichere Verarbeitung</div>
    </div>
</div>

<footer class="footer" style="background:#003856;color:#fff;padding:40px 24px;margin-top:0;">
    <div style="max-width:1100px;margin:0 auto;text-align:center;">
        <p style="margin-bottom:16px;">© 2025 SBS Deutschland · <a href="https://sbsdeutschland.com/sbshomepage/impressum.html" style="color:rgba(255,255,255,0.7);">Impressum</a> · <a href="https://sbsdeutschland.com/sbshomepage/datenschutz.html" style="color:rgba(255,255,255,0.7);">Datenschutz</a></p>
        <p style="color:rgba(255,255,255,0.6);font-size:0.9rem;">Made with ❤️ in Weinheim</p>
    </div>
</footer>

<script>
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const analyzeBtn = document.getElementById('analyzeBtn');
const errorMessage = document.getElementById('errorMessage');
const resultSection = document.getElementById('resultSection');
const resultContent = document.getElementById('resultContent');
const typeBtns = document.querySelectorAll('.type-btn');

let selectedFile = null;
let contractType = 'employment';
let currentContractId = null;

// Drag & Drop
uploadZone.addEventListener('dragover', (e) => {{
    e.preventDefault();
    uploadZone.classList.add('dragover');
}});

uploadZone.addEventListener('dragleave', () => {{
    uploadZone.classList.remove('dragover');
}});

uploadZone.addEventListener('drop', (e) => {{
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) handleFile(files[0]);
}});

uploadZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => {{
    if (e.target.files.length > 0) handleFile(e.target.files[0]);
}});

function handleFile(file) {{
    if (!file.name.match(/\.(pdf|docx|doc)$/i)) {{
        showError('Bitte nur PDF oder DOCX-Dateien hochladen.');
        return;
    }}
    if (file.size > 10 * 1024 * 1024) {{
        showError('Datei zu groß (max. 10 MB).');
        return;
    }}
    selectedFile = file;
    fileName.textContent = '📄 ' + file.name;
    fileName.classList.add('show');
    uploadZone.classList.add('has-file');
    analyzeBtn.disabled = false;
    hideError();
}}

typeBtns.forEach(btn => {{
    btn.addEventListener('click', () => {{
        typeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        contractType = btn.dataset.type;
    }});
}});

analyzeBtn.addEventListener('click', async () => {{
    if (!selectedFile) return;
    
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Wird hochgeladen...';
    hideError();
    resultSection.classList.remove('show');
    
    try {{
        // Upload
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        const uploadRes = await fetch('/contracts/upload', {{
            method: 'POST',
            body: formData,
            headers: {{ 'X-API-Key': 'web-upload-key' }}
        }});
        
        const uploadData = await uploadRes.json();
        if (!uploadRes.ok) throw new Error(uploadData.detail || 'Upload fehlgeschlagen');
        
        currentContractId = uploadData.contract_id;
        analyzeBtn.textContent = 'Wird analysiert...';
        
        // Analyze
        const analyzeRes = await fetch('/web/analyze/' + currentContractId, {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{contract_type: contractType, language: 'de'}}),
            credentials: 'include'
        }});
        
        const analyzeData = await analyzeRes.json();
        if (!analyzeRes.ok) throw new Error(analyzeData.detail || 'Analyse fehlgeschlagen');
        
        displayResult(analyzeData);
        
    }} catch (err) {{
        showError(err.message);
    }}
    
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = 'Vertrag analysieren';
}});

function displayResult(data) {{
    let html = '';
    
    if (data.summary) {{
        html += '<div class="result-item"><div class="result-label">Zusammenfassung</div><div class="result-value">' + data.summary + '</div></div>';
    }}
    
    if (data.termination_notice) {{
        html += '<div class="result-item"><div class="result-label">Kündigungsfrist</div><div class="result-value">' + data.termination_notice + '</div></div>';
    }}
    
    if (data.contract_duration) {{
        html += '<div class="result-item"><div class="result-label">Vertragslaufzeit</div><div class="result-value">' + data.contract_duration + '</div></div>';
    }}
    
    if (data.salary) {{
        html += '<div class="result-item"><div class="result-label">Vergütung</div><div class="result-value">' + data.salary + '</div></div>';
    }}
    
    if (data.risks && data.risks.length > 0) {{
        html += '<div class="result-item"><div class="result-label">⚠️ Risiken</div><div class="result-value">' + data.risks.join('<br>') + '</div></div>';
    }}
    
    if (data.key_clauses && data.key_clauses.length > 0) {{
        html += '<div class="result-item"><div class="result-label">📋 Wichtige Klauseln</div><div class="result-value">' + data.key_clauses.join('<br>') + '</div></div>';
    }}
    
    // Fallback: Zeige alle Keys
    if (!html) {{
        for (const [key, value] of Object.entries(data)) {{
            if (value && key !== 'contract_id' && key !== 'contract_type') {{
                html += '<div class="result-item"><div class="result-label">' + key + '</div><div class="result-value">' + JSON.stringify(value) + '</div></div>';
            }}
        }}
    }}
    
    resultContent.innerHTML = html;
    resultSection.classList.add('show');
}}

function showError(msg) {{
    errorMessage.textContent = '❌ ' + msg;
    errorMessage.classList.add('show');
}}

function hideError() {{
    errorMessage.classList.remove('show');
}}
</script>
</body>
</html>
"""



# === ADDITIONAL ROUTES ===
@app.get("/history", response_class=HTMLResponse)
async def history():
    return get_history_page()

@app.get("/analytics", response_class=HTMLResponse)
async def analytics():
    return get_analytics_page()

@app.get("/help", response_class=HTMLResponse)
async def help_page():
    return get_help_page()

@app.get("/compare", response_class=HTMLResponse)
async def compare():
    return "<html><body><h1>Vertragsvergleich - Coming Soon</h1></body></html>"

@app.get("/library", response_class=HTMLResponse)
async def library():
    return "<html><body><h1>Klausel-Bibliothek - Coming Soon</h1></body></html>"

@app.get("/exports", response_class=HTMLResponse)
async def exports():
    return "<html><body><h1>Export-Historie - Coming Soon</h1></body></html>"

@app.get("/settings", response_class=HTMLResponse)
async def settings():
    return "<html><body><h1>Einstellungen - Coming Soon</h1></body></html>"

@app.get("/billing", response_class=HTMLResponse)
async def billing():
    return "<html><body><h1>Abrechnung - Coming Soon</h1></body></html>"

@app.get("/team", response_class=HTMLResponse)
async def team():
    return "<html><body><h1>Team - Coming Soon</h1></body></html>"

@app.get("/audit", response_class=HTMLResponse)
async def audit():
    return "<html><body><h1>Audit-Log - Coming Soon</h1></body></html>"
