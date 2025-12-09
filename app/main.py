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

app = FastAPI(
    title="Contract Analyzer API",
    version="0.3.0",
    description="Production-Ready Backend für KI-gestützte Vertragsanalyse mit Auth, Export & Dashboard",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
