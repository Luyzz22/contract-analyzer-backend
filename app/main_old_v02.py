# app/main.py
"""
Contract Analyzer API – MVP Backend für KI-gestützte Vertragsanalyse.
Unterstützt Arbeitsverträge & SaaS-Dienstleistungsverträge.

Stack:
- FastAPI für REST API
- LLM (OpenAI GPT-4 mini) für Analyse
- SQLite für Audit-Logging
- Pydantic für Schema-Validierung
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse

# Lokale Module
from .pdf_utils import extract_text_from_pdf
from .llm_client import call_employment_contract_model, call_saas_contract_model, LLMError
from .prompts import get_employment_contract_prompt, get_saas_contract_prompt
from .logging_service import setup_logging, log_analysis_event

# Enterprise-Standards (nur einmal importieren)
try:
    from enterprise_saas_config import ENTERPRISE_SAAS_STANDARDS, VENDOR_COMPLIANCE_MATRIX
except ImportError:
    # Fallback falls Datei noch nicht existiert
    ENTERPRISE_SAAS_STANDARDS = None
    VENDOR_COMPLIANCE_MATRIX = None

# ============================================================================
# SETUP
# ============================================================================

# Logging konfigurieren
logger = logging.getLogger(__name__)
setup_logging()

# FastAPI-App
app = FastAPI(
    title="Contract Analyzer API",
    version="0.2.0",
    description="MVP-Backend für KI-gestützte Vertragsanalyse (Arbeits- & SaaS-Verträge)",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# CORS für Frontend (localhost:5173 in Dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload-Verzeichnis
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class RiskFlag(BaseModel):
    """Ein identifiziertes Risiko in einem Vertrag."""
    severity: str = Field(..., description="low, medium, oder high")
    title: str = Field(..., description="Kurze deutsche Risiko-Bezeichnung")
    description: str = Field(..., description="Erklärung des Risikos")
    clause_snippet: Optional[str] = Field(None, description="Direkter Zitat aus Vertrag")
    policy_reference: Optional[str] = Field(None, description="z.B. BGB §623, Policy-Name")


class EmploymentExtractedFields(BaseModel):
    """Strukturierte Felder aus einem Arbeitsvertrag."""
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
    """Strukturierte Felder aus einem SaaS-Vertrag."""
    customer_name: Optional[str] = None
    vendor_name: Optional[str] = None
    contract_start_date: Optional[str] = None
    contract_end_date: Optional[str] = None
    auto_renew: Optional[bool] = None
    renewal_notice_days: Optional[float] = None
    annual_contract_value_eur: Optional[float] = None
    billing_interval: Optional[str] = None  # monthly, quarterly, annual
    min_term_months: Optional[float] = None
    termination_for_convenience: Optional[bool] = None
    data_location: Optional[str] = None
    dp_addendum_included: Optional[bool] = None
    liability_cap_multiple_acv: Optional[float] = None
    uptime_sla_percent: Optional[float] = None


class ContractAnalysisResult(BaseModel):
    """Analyse-Ergebnis nach LLM-Verarbeitung."""
    contract_id: str
    contract_type: str = Field(..., description="employment oder saas")
    language: str = "de"
    summary: str = Field(..., description="2-4 Sätze Zusammenfassung")
    extracted_fields: dict = Field(..., description="Strukturierte Daten")
    risk_flags: List[RiskFlag] = Field(default=[], description="Identifizierte Risiken")


class ContractUploadResponse(BaseModel):
    """Response beim Hochladen eines Vertrags."""
    contract_id: str
    filename: str
    message: str = "File uploaded successfully. Use /contracts/{contract_id}/analyze to analyze."


class HealthResponse(BaseModel):
    """Health-Check Response."""
    status: str
    version: str
    timestamp: str


# ============================================================================
# ENDPOINTS: Health & Metadata
# ============================================================================

@app.get("/health", response_model=HealthResponse)
def health():
    """Health-Check Endpoint für Monitoring."""
    return {
        "status": "ok",
        "version": "0.2.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/contracts")
def list_contracts():
    """Listet alle hochgeladenen Verträge (ohne Inhalte)."""
    files = list(UPLOAD_DIR.glob("*"))
    contracts = []
    for f in files:
        contract_id = f.name.split("_")[0]
        contracts.append({
            "contract_id": contract_id,
            "filename": f.name,
            "uploaded_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })
    return {"contracts": contracts}


# ============================================================================
# ENDPOINTS: Upload & Analyse
# ============================================================================

@app.post("/contracts/upload", response_model=ContractUploadResponse)
async def upload_contract(file: UploadFile = File(...)):
    """
    Lädt einen Vertragsvertrag (PDF/DOCX) hoch.
    
    Validiert Dateityp, speichert lokal, gibt contract_id zurück.
    """
    allowed_types = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Supported: PDF, DOCX, DOC"
        )
    
    if file.size and file.size > 20 * 1024 * 1024:  # 20MB max
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
        
        logger.info(f"Contract uploaded: {contract_id}, filename: {file.filename}")
        
        return ContractUploadResponse(
            contract_id=contract_id,
            filename=file.filename,
        )
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@app.post("/contracts/{contract_id}/analyze", response_model=ContractAnalysisResult)
def analyze_contract(
    contract_id: str,
    contract_type: str = Body("employment", description="employment oder saas"),
    language: str = Body("de", description="Sprache des Vertrags"),
):
    """
    Analysiert einen hochgeladenen Vertrag mit KI.
    
    1. Sucht Vertrag nach contract_id
    2. Extrahiert Text (PDF → Text)
    3. Ruft LLM mit Prompt-Template auf
    4. Validiert Ergebnis gegen Schema
    5. Logged Analyse-Metadaten
    
    Unterstützte Vertragstypen:
    - employment: Arbeitsverträge (Arbeitsrecht-fokussiert)
    - saas: B2B-SaaS & Cloud-Dienste (CFO-fokussiert)
    """
    
    # ─────────────────────────────────────────────────────────────────
    # 1. Datei finden & validieren
    # ─────────────────────────────────────────────────────────────────
    
    files = list(UPLOAD_DIR.glob(f"{contract_id}_*"))
    if not files:
        log_analysis_event(
            contract_id=contract_id,
            tenant_id="demo-tenant-1",
            contract_type=contract_type,
            language=language,
            status="error",
            duration_ms=0,
            llm_model="gpt-4.1-mini",
            error_message="Contract not found",
        )
        raise HTTPException(status_code=404, detail="Contract not found")
    
    file_path = files[0]
    
    if file_path.suffix.lower() not in [".pdf", ".docx", ".doc"]:
        raise HTTPException(status_code=400, detail="Only PDF/DOCX supported")
    
    if contract_type not in ["employment", "saas"]:
        raise HTTPException(status_code=400, detail="contract_type muss 'employment' oder 'saas' sein")
    
    # ─────────────────────────────────────────────────────────────────
    # 2. Text extrahieren
    # ─────────────────────────────────────────────────────────────────
    
    try:
        if file_path.suffix.lower() == ".pdf":
            contract_text = extract_text_from_pdf(file_path)
        else:
            # TODO: DOCX-Unterstützung mit python-docx
            raise HTTPException(status_code=501, detail="DOCX support coming soon, use PDF for now")
        
        if not contract_text or len(contract_text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Contract text too short or empty")
        
        logger.info(f"Text extracted for {contract_id}, {len(contract_text)} chars")
    
    except Exception as e:
        logger.error(f"Text extraction failed for {contract_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {e}")
    
    # ─────────────────────────────────────────────────────────────────
    # 3. Prompt zusammenstellen & LLM aufrufen
    # ─────────────────────────────────────────────────────────────────
    
    start_time_ms = int(time.time() * 1000)
    tenant_id = "demo-tenant-1"  # Später aus Auth/Header
    
    try:
        if contract_type == "employment":
            user_prompt = get_employment_contract_prompt(contract_text)
            raw_result = call_employment_contract_model(user_prompt)
        else:  # saas
            user_prompt = get_saas_contract_prompt(contract_text)
            raw_result = call_saas_contract_model(user_prompt)
        
        # Sicherstellen, dass contract_id gesetzt ist
        raw_result["contract_id"] = contract_id
        raw_result["contract_type"] = contract_type
        raw_result["language"] = language
        
        # Pydantic-Validierung
        result = ContractAnalysisResult(**raw_result)
        
        duration_ms = int(time.time() * 1000) - start_time_ms
        
        # ─────────────────────────────────────────────────────────────
        # 4. Enterprise-Risiko-Check (KORREKT PLATZIERT)
        # ─────────────────────────────────────────────────────────────
        
        if ENTERPRISE_SAAS_STANDARDS:
            enterprise_risks = []
            for risk in result.risk_flags:
                if risk.severity == 'high':
                    enterprise_risks.append(risk)

            if len(enterprise_risks) > 0:
                logger.warning(f"⚠️  {len(enterprise_risks)} Enterprise-Risiken gefunden für {contract_id}")
        
        # Logging
        log_analysis_event(
            contract_id=contract_id,
            tenant_id=tenant_id,
            contract_type=contract_type,
            language=language,
            status="success",
            duration_ms=duration_ms,
            llm_model="gpt-4.1-mini",
            num_risk_flags=len(result.risk_flags),
            error_message=None,
        )
        
        logger.info(
            f"Analysis completed: {contract_id} ({contract_type}), "
            f"{duration_ms}ms, {len(result.risk_flags)} risk flags"
        )
        
        return result
    
    except LLMError as e:
        duration_ms = int(time.time() * 1000) - start_time_ms
        log_analysis_event(
            contract_id=contract_id,
            tenant_id=tenant_id,
            contract_type=contract_type,
            language=language,
            status="error",
            duration_ms=duration_ms,
            llm_model="gpt-4.1-mini",
            error_message=f"LLM error: {e}",
        )
        logger.error(f"LLM error for {contract_id}: {e}")
        raise HTTPException(status_code=502, detail=f"LLM analysis failed: {e}")
    
    except ValueError as e:
        duration_ms = int(time.time() * 1000) - start_time_ms
        log_analysis_event(
            contract_id=contract_id,
            tenant_id=tenant_id,
            contract_type=contract_type,
            language=language,
            status="error",
            duration_ms=duration_ms,
            llm_model="gpt-4.1-mini",
            error_message=f"Validation error: {e}",
        )
        logger.error(f"Validation error for {contract_id}: {e}")
        raise HTTPException(status_code=422, detail=f"Invalid response schema: {e}")
    
    except Exception as e:
        duration_ms = int(time.time() * 1000) - start_time_ms
        log_analysis_event(
            contract_id=contract_id,
            tenant_id=tenant_id,
            contract_type=contract_type,
            language=language,
            status="error",
            duration_ms=duration_ms,
            llm_model="gpt-4.1-mini",
            error_message=str(e),
        )
        logger.error(f"Unexpected error for {contract_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@app.get("/contracts/{contract_id}/raw-text")
def get_contract_text(contract_id: str):
    """
    Gibt den extrahierten Rohtext eines Vertrags zurück.
    Nützlich für Debugging & Validierung.
    """
    files = list(UPLOAD_DIR.glob(f"{contract_id}_*"))
    if not files:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    file_path = files[0]
    
    if file_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF supported for text extraction")
    
    try:
        text = extract_text_from_pdf(file_path)
        return {
            "contract_id": contract_id,
            "text": text[:5000],  # Nur erste 5000 Zeichen zurück
            "total_length": len(text),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {e}")


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Strukturierte Error-Response als gültiges FastAPI-Response-Objekt."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Bei App-Start: Logging initialisieren, Directories prüfen."""
    logger.info("Contract Analyzer API startup (v0.2.0)")
    logger.info(f"Upload directory: {UPLOAD_DIR.absolute()}")
    
    # Prüfe Umgebungsvariablen
    dummy_mode = os.getenv("CONTRACT_ANALYZER_DUMMY", "true").lower() == "true"
    if dummy_mode:
        logger.warning("⚠️  DUMMY MODE ENABLED – Nutzt Mock-Responses statt echter API")
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("❌ OPENAI_API_KEY not set – LLM-Calls werden fehlschlagen")
        else:
            logger.info("✓ OPENAI_API_KEY configured")


@app.on_event("shutdown")
async def shutdown_event():
    """Bei App-Shutdown."""
    logger.info("Contract Analyzer API shutdown")


# ============================================================================
# CLI / LOCAL TESTING
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )

