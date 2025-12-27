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
async def history_page(request: Request):
    """Verlauf Page mit echten Daten aus DB"""
    user = get_user_info(request)
    
    # Verträge aus DB laden
    conn = _init_db()
    try:
        rows = conn.execute(
            "SELECT contract_id, filename, contract_type, created_at, status, risk_level, risk_score "
            "FROM contracts ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
    finally:
        conn.close()
    
    # Vertragstyp-Labels
    type_labels = {
        "employment": "Arbeitsvertrag",
        "saas": "SaaS-Vertrag",
        "nda": "NDA",
        "vendor": "Lieferant",
        "service": "Dienstleistung",
        "rental": "Mietvertrag",
        "purchase": "Kaufvertrag",
        "general": "Allgemein",
    }
    
    # Tabellen-Rows generieren
    table_rows = ""
    for r in rows:
        contract_id, filename, ctype, created_at, status, risk_level, risk_score = r
        
        # Datum formatieren
        try:
            dt = datetime.fromisoformat(created_at)
            date_str = dt.strftime("%d.%m.%Y %H:%M")
        except:
            date_str = created_at[:16] if created_at else "-"
        
        type_label = type_labels.get(ctype, ctype or "Allgemein")
        risk_level = risk_level or "low"
        risk_score = risk_score or 0
        
        # Status Badge
        if status == "analyzed":
            status_badge = '<span class="badge badge-success">Analysiert</span>'
        elif status == "uploaded":
            status_badge = '<span class="badge badge-warning">Hochgeladen</span>'
        else:
            status_badge = f'<span class="badge badge-info">{status}</span>'
        
        table_rows += f'''
        <tr onclick="window.location='/contracts/{contract_id}'" style="cursor:pointer;">
          <td><strong>{filename}</strong></td>
          <td><span class="badge badge-info">{type_label}</span></td>
          <td>{date_str}</td>
          <td>{status_badge}</td>
          <td>
            <span class="risk-dot {risk_level}"></span>
            {risk_level.capitalize()} ({risk_score}/100)
          </td>
          <td>
            <a href="/api/v3/contracts/{contract_id}/export/pdf" class="btn btn-secondary" style="padding:6px 12px;font-size:0.8rem;" onclick="event.stopPropagation();">PDF</a>
            <a href="/api/v3/contracts/{contract_id}/export/json" class="btn btn-secondary" style="padding:6px 12px;font-size:0.8rem;" onclick="event.stopPropagation();">JSON</a>
          </td>
        </tr>
        '''
    
    # Leerer Zustand
    if not rows:
        table_rows = '''
        <tr>
          <td colspan="6" style="text-align:center;padding:60px;">
            <div style="font-size:3rem;margin-bottom:16px;">📄</div>
            <p style="font-weight:600;margin-bottom:8px;">Keine Verträge vorhanden</p>
            <p style="color:var(--sbs-muted);">Laden Sie Ihren ersten Vertrag hoch.</p>
            <a href="/upload" class="btn btn-primary" style="margin-top:16px;">Vertrag hochladen</a>
          </td>
        </tr>
        '''
    
    return get_history_page_dynamic(user["name"], table_rows, len(rows))


def get_history_page_dynamic(user_name: str, table_rows: str, total_count: int):
    """Generiert History-Seite mit dynamischen Daten."""
    from .pages_enterprise import PAGE_CSS, get_header, get_footer
    
    user_initial = user_name[0].upper() if user_name else "U"
    
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verlauf | SBS Contract Intelligence</title>
  <link rel="icon" href="/static/favicon.ico">
  {PAGE_CSS}
  <style>
    .history-table {{ width: 100%; border-collapse: collapse; }}
    .history-table th, .history-table td {{ padding: 16px 20px; text-align: left; border-bottom: 1px solid var(--sbs-border); }}
    .history-table th {{ background: #f8fafc; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--sbs-muted); }}
    .history-table tr:hover {{ background: rgba(0,56,86,0.02); cursor: pointer; }}
    .risk-dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }}
    .risk-dot.critical {{ background: #dc2626; }}
    .risk-dot.high {{ background: #ea580c; }}
    .risk-dot.medium {{ background: #d97706; }}
    .risk-dot.low {{ background: #16a34a; }}
    .badge {{ display: inline-flex; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }}
    .badge-success {{ background: rgba(16,185,129,0.1); color: #059669; }}
    .badge-warning {{ background: rgba(245,158,11,0.1); color: #d97706; }}
    .badge-info {{ background: rgba(0,56,86,0.1); color: #003856; }}
  </style>
</head>
<body>
{get_header(user_name, "verlauf")}
<main>
<div class="hero">
  <div class="container">
    <div class="hero-badge"><span class="dot"></span> VERLAUF</div>
    <h1>📊 Analysierte Verträge</h1>
    <p>Übersicht aller analysierten Verträge mit Risikobewertung.</p>
  </div>
</div>
<div class="page-container">
  <div class="stats-grid" style="grid-template-columns: repeat(3, 1fr); margin-bottom: 32px;">
    <div class="stat-card"><div class="stat-value">{total_count}</div><div class="stat-label">Verträge gesamt</div></div>
    <div class="stat-card"><div class="stat-value">{total_count}</div><div class="stat-label">Analysiert</div></div>
    <div class="stat-card"><div class="stat-value">0</div><div class="stat-label">Ausstehend</div></div>
  </div>
  <div class="content-card">
    <div class="content-card-header">
      <h3 class="content-card-title">Alle Verträge</h3>
      <a href="/upload" class="btn btn-primary">+ Neuer Vertrag</a>
    </div>
    <div class="content-card-body" style="padding:0;">
      <table class="history-table">
        <thead>
          <tr>
            <th>Dateiname</th>
            <th>Typ</th>
            <th>Datum</th>
            <th>Status</th>
            <th>Risiko</th>
            <th>Export</th>
          </tr>
        </thead>
        <tbody>
          {table_rows}
        </tbody>
      </table>
    </div>
  </div>
</div>
</main>
{get_footer()}
</body>
</html>'''

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics Dashboard mit echten Daten"""
    user = get_user_info(request)
    
    # KPIs aus DB laden
    conn = _init_db()
    try:
        total = conn.execute("SELECT COUNT(*) FROM contracts").fetchone()[0] or 0
        analyzed = conn.execute("SELECT COUNT(*) FROM contracts WHERE status = 'analyzed'").fetchone()[0] or 0
        
        # Risiko-Verteilung
        critical = conn.execute("SELECT COUNT(*) FROM contracts WHERE risk_level = 'critical'").fetchone()[0] or 0
        high = conn.execute("SELECT COUNT(*) FROM contracts WHERE risk_level = 'high'").fetchone()[0] or 0
        medium = conn.execute("SELECT COUNT(*) FROM contracts WHERE risk_level = 'medium'").fetchone()[0] or 0
        low = conn.execute("SELECT COUNT(*) FROM contracts WHERE risk_level = 'low'").fetchone()[0] or 0
        
        # Durchschnittlicher Risiko-Score
        avg_score = conn.execute("SELECT AVG(risk_score) FROM contracts WHERE risk_score IS NOT NULL").fetchone()[0] or 0
        
        # Vertragstypen-Verteilung
        type_counts = conn.execute(
            "SELECT contract_type, COUNT(*) as cnt FROM contracts GROUP BY contract_type ORDER BY cnt DESC"
        ).fetchall()
        
        # Letzte 7 Tage
        recent = conn.execute(
            "SELECT COUNT(*) FROM contracts WHERE created_at > datetime('now', '-7 days')"
        ).fetchone()[0] or 0
    finally:
        conn.close()
    
    # Vertragstyp-Labels
    type_labels = {
        "employment": "Arbeitsvertrag", "saas": "SaaS-Vertrag", "nda": "NDA",
        "vendor": "Lieferant", "service": "Dienstleistung", "rental": "Mietvertrag",
        "purchase": "Kaufvertrag", "general": "Allgemein",
    }
    
    # Typ-Bars generieren
    type_bars = ""
    max_count = max([c[1] for c in type_counts], default=1)
    for ctype, count in type_counts:
        label = type_labels.get(ctype, ctype or "Unbekannt")
        width = int((count / max_count) * 100)
        type_bars += f'''
        <div style="margin-bottom:12px;">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span>{label}</span><span style="font-weight:600;">{count}</span>
          </div>
          <div style="background:var(--sbs-border);border-radius:4px;height:8px;">
            <div style="background:var(--sbs-blue);border-radius:4px;height:100%;width:{width}%;"></div>
          </div>
        </div>
        '''
    
    return get_analytics_page_dynamic(user["name"], total, analyzed, recent, avg_score, critical, high, medium, low, type_bars)


def get_analytics_page_dynamic(user_name: str, total: int, analyzed: int, recent: int, avg_score: float, critical: int, high: int, medium: int, low: int, type_bars: str):
    """Generiert Analytics-Seite mit dynamischen Daten."""
    from .pages_enterprise import PAGE_CSS, get_header, get_footer
    
    # Risiko-Farbe basierend auf Durchschnitt
    if avg_score >= 70:
        score_color = "#dc2626"
    elif avg_score >= 50:
        score_color = "#d97706"
    else:
        score_color = "#16a34a"
    
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Analytics | SBS Contract Intelligence</title>
  <link rel="icon" href="/static/favicon.ico">
  {PAGE_CSS}
</head>
<body>
{get_header(user_name, "analytics")}
<main>
<div class="hero">
  <div class="container">
    <div class="hero-badge"><span class="dot"></span> ANALYTICS</div>
    <h1>📈 Analytics Dashboard</h1>
    <p>Überblick über alle Vertragsanalysen und Risikobewertungen.</p>
  </div>
</div>
<div class="page-container">
  <!-- KPI Cards -->
  <div class="stats-grid" style="margin-bottom:32px;">
    <div class="stat-card">
      <div class="stat-value">{total}</div>
      <div class="stat-label">Verträge gesamt</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{analyzed}</div>
      <div class="stat-label">Analysiert</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{recent}</div>
      <div class="stat-label">Letzte 7 Tage</div>
    </div>
    <div class="stat-card">
      <div class="stat-value" style="color:{score_color};">{avg_score:.0f}</div>
      <div class="stat-label">Ø Risiko-Score</div>
    </div>
  </div>
  
  <div class="grid-2">
    <!-- Risiko-Verteilung -->
    <div class="content-card">
      <div class="content-card-header">
        <h3 class="content-card-title">⚠️ Risiko-Verteilung</h3>
      </div>
      <div class="content-card-body">
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;text-align:center;">
          <div style="padding:20px;background:rgba(220,38,38,0.1);border-radius:12px;">
            <div style="font-size:2rem;font-weight:700;color:#dc2626;">{critical}</div>
            <div style="font-size:0.85rem;color:var(--sbs-muted);">Kritisch</div>
          </div>
          <div style="padding:20px;background:rgba(234,88,12,0.1);border-radius:12px;">
            <div style="font-size:2rem;font-weight:700;color:#ea580c;">{high}</div>
            <div style="font-size:0.85rem;color:var(--sbs-muted);">Hoch</div>
          </div>
          <div style="padding:20px;background:rgba(217,119,6,0.1);border-radius:12px;">
            <div style="font-size:2rem;font-weight:700;color:#d97706;">{medium}</div>
            <div style="font-size:0.85rem;color:var(--sbs-muted);">Mittel</div>
          </div>
          <div style="padding:20px;background:rgba(22,163,74,0.1);border-radius:12px;">
            <div style="font-size:2rem;font-weight:700;color:#16a34a;">{low}</div>
            <div style="font-size:0.85rem;color:var(--sbs-muted);">Niedrig</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Vertragstypen -->
    <div class="content-card">
      <div class="content-card-header">
        <h3 class="content-card-title">📊 Vertragstypen</h3>
      </div>
      <div class="content-card-body">
        {type_bars if type_bars else '<p style="color:var(--sbs-muted);text-align:center;">Keine Daten</p>'}
      </div>
    </div>
  </div>
</div>
</main>
{get_footer()}
</body>
</html>'''

@app.get("/help", response_class=HTMLResponse)
async def help_page():
    """Hilfe & FAQ"""
    return get_help_page()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """CFO Dashboard mit Onboarding-Check"""
    user = get_user_info(request)
    email = user.get("email")
    
    # Check Onboarding - nur fuer neue User
    if email:
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT onboarding_completed FROM user_settings WHERE user_email = ?", (email,)).fetchone()
            conn.close()
            # Redirect nur wenn User noch kein Onboarding gemacht hat
            if not row:
                from fastapi.responses import RedirectResponse
                return RedirectResponse("/onboarding")
        except:
            pass
    
    return get_dashboard()

# Enterprise Pages mit User-Auth
from .pages_enterprise import (
    get_compare_page, get_library_page, get_exports_page,
    get_settings_page, get_billing_page, get_team_page, get_audit_page
)

# Admin Users
ADMIN_USERNAMES = {"luis220195", "admin"}
ADMIN_EMAILS = {"info@sbsdeutschland.com", "luis@sbsdeutschland.com", "luis220195@gmail.com"}

def get_user_info(request: Request):
    """Holt User-Info aus SSO oder gibt Defaults zurück."""
    user = get_optional_user(request)
    if user:
        return {
            "name": user.get("name", user.get("username", "User")),
            "email": user.get("email", ""),
            "is_admin": user.get("username") in ADMIN_USERNAMES or user.get("email") in ADMIN_EMAILS
        }
    return {"name": "Gast", "email": "", "is_admin": False}

@app.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request):
    user = get_user_info(request)
    return get_compare_page(user["name"])

@app.get("/library", response_class=HTMLResponse)
async def library_page(request: Request):
    user = get_user_info(request)
    return get_library_page(user["name"])

@app.get("/exports", response_class=HTMLResponse)
async def exports_page(request: Request):
    user = get_user_info(request)
    return get_exports_page(user["name"])

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    user = get_user_info(request)
    return get_settings_page(user["name"], user["email"])

@app.get("/billing", response_class=HTMLResponse)
async def billing_page(request: Request):
    user = get_user_info(request)
    return get_billing_page(user["name"], user.get("is_admin", False), user.get("email"))

@app.get("/team", response_class=HTMLResponse)
async def team_page(request: Request):
    user = get_user_info(request)
    return get_team_page(user["name"])

@app.get("/audit", response_class=HTMLResponse)
async def audit_page(request: Request):
    user = get_user_info(request)
    return get_audit_page(user["name"])

# ============================================================================
# API V3 ROUTES (Frontend Compatible)
# ============================================================================

@app.get("/contracts/{contract_id}", response_class=HTMLResponse)
async def contract_detail_page(contract_id: str, request: Request):
    """Einzelne Vertragsdetailseite"""
    user = get_user_info(request)
    
    # Vertrag aus DB laden
    conn = _init_db()
    try:
        meta = conn.execute(
            "SELECT contract_id, filename, contract_type, created_at, status, risk_level, risk_score "
            "FROM contracts WHERE contract_id = ?", (contract_id,)
        ).fetchone()
        
        analysis = conn.execute(
            "SELECT analysis_json FROM analysis_results WHERE contract_id = ?", (contract_id,)
        ).fetchone()
    finally:
        conn.close()
    
    if not meta:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")
    
    contract_id, filename, ctype, created_at, status, risk_level, risk_score = meta
    
    # Analyse-Daten parsen
    analysis_data = {}
    if analysis and analysis[0]:
        analysis_data = json.loads(analysis[0])
    
    # Vertragstyp-Labels
    type_labels = {
        "employment": "Arbeitsvertrag", "saas": "SaaS-Vertrag", "nda": "NDA",
        "vendor": "Lieferantenvertrag", "service": "Dienstleistungsvertrag",
        "rental": "Mietvertrag", "purchase": "Kaufvertrag", "general": "Allgemein",
    }
    type_label = type_labels.get(ctype, ctype or "Allgemein")
    
    # Datum formatieren
    try:
        dt = datetime.fromisoformat(created_at)
        date_str = dt.strftime("%d.%m.%Y um %H:%M Uhr")
    except:
        date_str = created_at[:16] if created_at else "-"
    
    # Risiko-Farbe
    risk_colors = {"critical": "#dc2626", "high": "#ea580c", "medium": "#d97706", "low": "#16a34a"}
    risk_color = risk_colors.get(risk_level, "#6b7280")
    risk_label = {"critical": "Kritisch", "high": "Hoch", "medium": "Mittel", "low": "Niedrig"}.get(risk_level, risk_level)
    
    # Extrahierte Daten
    extracted_data = analysis_data.get("extracted_data", {})
    risk_assessment = analysis_data.get("risk_assessment", {})
    summary = risk_assessment.get("executive_summary", "Keine Zusammenfassung verfügbar.")
    
    # Felder als HTML
    fields_html = ""
    field_labels = {
        "vendor_name": "Anbieter", "customer_name": "Kunde", "product_name": "Produkt",
        "auto_renew": "Auto-Renewal", "renewal_notice_days": "Kündigungsfrist (Tage)",
        "min_term_months": "Mindestlaufzeit (Monate)", "data_location": "Datenlokation",
        "uptime_sla_percent": "SLA Uptime (%)", "liability_cap_multiple_acv": "Haftungsgrenze (x ACV)",
        "annual_contract_value_eur": "Jährlicher Wert (EUR)", "billing_interval": "Abrechnungsintervall",
        "parties": "Parteien", "start_date": "Startdatum", "end_date": "Enddatum",
        "base_salary_eur": "Grundgehalt (EUR)", "vacation_days_per_year": "Urlaubstage",
        "weekly_hours": "Wochenstunden", "probation_period_months": "Probezeit (Monate)",
        "disclosing_party": "Offenlegende Partei", "receiving_party": "Empfangende Partei",
        "term_years": "Laufzeit (Jahre)", "penalty_amount_eur": "Vertragsstrafe (EUR)",
    }
    
    for key, value in extracted_data.items():
        if value is not None and value != "" and value != []:
            label = field_labels.get(key, key.replace("_", " ").title())
            if isinstance(value, bool):
                value = "Ja" if value else "Nein"
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    value = ", ".join([f"{p.get('name', 'N/A')}" for p in value])
                else:
                    value = ", ".join(str(v) for v in value)
            fields_html += f'<tr><td style="font-weight:500;color:var(--sbs-blue);">{label}</td><td>{value}</td></tr>'
    
    # Risiken als HTML
    risks_html = ""
    all_risks = []
    for level in ["critical_risks", "high_risks", "medium_risks", "low_risks"]:
        for risk in risk_assessment.get(level, []):
            risk["level"] = level.replace("_risks", "")
            all_risks.append(risk)
    
    for risk in all_risks:
        level = risk.get("level", "medium")
        title = risk.get("title", risk.get("issue_title", "Risiko"))
        desc = risk.get("description", risk.get("issue_description", ""))
        clause = risk.get("clause_snippet", risk.get("clause_text", ""))
        r_color = risk_colors.get(level, "#6b7280")
        r_label = {"critical": "Kritisch", "high": "Hoch", "medium": "Mittel", "low": "Niedrig"}.get(level, level)
        
        risks_html += f'''
        <div style="background:#fff;border-radius:12px;padding:20px;margin-bottom:16px;border-left:4px solid {r_color};">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <strong style="color:var(--sbs-blue);">{title}</strong>
            <span class="badge" style="background:{r_color}20;color:{r_color};">{r_label}</span>
          </div>
          <p style="color:var(--sbs-muted);margin-bottom:8px;">{desc}</p>
          {f'<p style="font-style:italic;color:#666;font-size:0.9rem;background:#f8fafc;padding:12px;border-radius:8px;">„{clause}"</p>' if clause else ''}
        </div>
        '''
    
    if not risks_html:
        risks_html = '<p style="color:var(--sbs-muted);text-align:center;padding:40px;">✅ Keine Risiken identifiziert</p>'
    
    return get_contract_detail_page(user["name"], contract_id, filename, type_label, date_str, 
                                     risk_level, risk_label, risk_score or 0, risk_color, 
                                     summary, fields_html, risks_html)


def get_contract_detail_page(user_name, contract_id, filename, type_label, date_str, 
                              risk_level, risk_label, risk_score, risk_color, summary, fields_html, risks_html):
    """Generiert Vertrags-Detailseite."""
    from .pages_enterprise import PAGE_CSS, get_header, get_footer
    
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{filename} | SBS Contract Intelligence</title>
  <link rel="icon" href="/static/favicon.ico">
  {PAGE_CSS}
</head>
<body>
{get_header(user_name, "verlauf")}
<main>
<div class="hero">
  <div class="container">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
      <a href="/history" style="color:#fff;opacity:0.7;text-decoration:none;">← Zurück zum Verlauf</a>
    </div>
    <div class="hero-badge"><span class="dot"></span> {type_label.upper()}</div>
    <h1>📄 {filename}</h1>
    <p>Analysiert am {date_str}</p>
  </div>
</div>
<div class="page-container">
  <!-- Risiko-Overview -->
  <div class="content-card" style="border-left:4px solid {risk_color};margin-bottom:24px;">
    <div class="content-card-body">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:24px;">
        <div>
          <div style="font-size:0.85rem;color:var(--sbs-muted);margin-bottom:4px;">RISIKO-BEWERTUNG</div>
          <div style="font-size:2rem;font-weight:700;color:{risk_color};">{risk_label}</div>
        </div>
        <div style="text-align:center;">
          <div style="font-size:3rem;font-weight:700;color:{risk_color};">{risk_score}</div>
          <div style="font-size:0.85rem;color:var(--sbs-muted);">von 100</div>
        </div>
        <div style="display:flex;gap:12px;">
          <a href="/api/v3/contracts/{contract_id}/export/pdf" class="btn btn-primary">📄 PDF Export</a>
          <a href="/api/v3/contracts/{contract_id}/export/json" class="btn btn-secondary">📋 JSON Export</a>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Zusammenfassung -->
  <div class="content-card" style="margin-bottom:24px;">
    <div class="content-card-header"><h3 class="content-card-title">📝 Zusammenfassung</h3></div>
    <div class="content-card-body">
      <p style="line-height:1.8;color:var(--sbs-text);">{summary}</p>
    </div>
  </div>
  
  <div class="grid-2">
    <!-- Extrahierte Daten -->
    <div class="content-card">
      <div class="content-card-header"><h3 class="content-card-title">📊 Extrahierte Daten</h3></div>
      <div class="content-card-body" style="padding:0;">
        <table class="data-table">
          <tbody>{fields_html if fields_html else '<tr><td colspan="2" style="text-align:center;padding:40px;color:var(--sbs-muted);">Keine Daten extrahiert</td></tr>'}</tbody>
        </table>
      </div>
    </div>
    
    <!-- Risiken -->
    <div class="content-card">
      <div class="content-card-header"><h3 class="content-card-title">⚠️ Identifizierte Risiken</h3></div>
      <div class="content-card-body" style="background:#f8fafc;">
        {risks_html}
      </div>
    </div>
  </div>
</div>
</main>
{get_footer()}
</body>
</html>'''


@app.get("/library/clause/{clause_id}", response_class=HTMLResponse)
async def clause_detail_page(clause_id: int, request: Request):
    """Klausel-Detailseite."""
    user = get_user_info(request)
    
    # Klausel-Daten (später aus DB)
    clauses = {
        1: {"name": "Kündigungsklausel Standard", "type": "Allgemein", "risk": "low", "usage": 47,
            "text": "Der Vertrag kann von beiden Parteien mit einer Frist von 30 Tagen zum Monatsende gekündigt werden. Die Kündigung bedarf der Schriftform.",
            "explanation": "Diese Standard-Kündigungsklausel entspricht den üblichen Gepflogenheiten im deutschen Vertragsrecht. Die 30-Tage-Frist ist ausgewogen und gibt beiden Parteien ausreichend Zeit für die Neuorganisation.",
            "laws": ["BGB § 621", "BGB § 622"]},
        2: {"name": "Haftungsbegrenzung 1x ACV", "type": "SaaS", "risk": "medium", "usage": 32,
            "text": "Die Haftung des Anbieters ist auf den jährlichen Vertragswert (Annual Contract Value) begrenzt. Dies gilt nicht für Vorsatz und grobe Fahrlässigkeit.",
            "explanation": "Eine Haftungsbegrenzung auf 1x ACV ist marktüblich für SaaS-Verträge. Bei kritischen Anwendungen sollte eine höhere Grenze (2-3x ACV) verhandelt werden.",
            "laws": ["BGB § 276", "BGB § 307"]},
        3: {"name": "Geheimhaltung 5 Jahre", "type": "NDA", "risk": "low", "usage": 28,
            "text": "Die empfangende Partei verpflichtet sich, alle vertraulichen Informationen für einen Zeitraum von 5 Jahren nach Beendigung des Vertrags geheim zu halten.",
            "explanation": "Eine 5-jährige Geheimhaltungsfrist ist Standard für die meisten Geschäftsbeziehungen. Bei technischen Informationen kann eine längere Frist angemessen sein.",
            "laws": ["GeschGehG § 2", "BGB § 823"]},
        4: {"name": "Auto-Renewal 30 Tage", "type": "SaaS", "risk": "low", "usage": 25,
            "text": "Der Vertrag verlängert sich automatisch um jeweils 12 Monate, sofern er nicht mit einer Frist von 30 Tagen vor Ablauf gekündigt wird.",
            "explanation": "30 Tage Kündigungsfrist bei Auto-Renewal ist kundenfreundlich. Kritisch sind Klauseln mit weniger als 14 Tagen oder automatischer Verlängerung um mehr als 12 Monate.",
            "laws": ["BGB § 309 Nr. 9"]},
        5: {"name": "Datenlokation EU", "type": "SaaS", "risk": "low", "usage": 21,
            "text": "Sämtliche Kundendaten werden ausschließlich auf Servern innerhalb der Europäischen Union verarbeitet und gespeichert.",
            "explanation": "EU-Datenlokation ist optimal für DSGVO-Compliance. Vermeiden Sie Klauseln, die USA-Server erlauben, ohne explizite Nennung von EU-US Data Privacy Framework.",
            "laws": ["DSGVO Art. 44-49", "BDSG § 80"]},
        6: {"name": "Eigentumsübergang bei Zahlung", "type": "Kaufvertrag", "risk": "low", "usage": 19,
            "text": "Das Eigentum an der Ware geht erst mit vollständiger Bezahlung des Kaufpreises auf den Käufer über (Eigentumsvorbehalt).",
            "explanation": "Ein einfacher Eigentumsvorbehalt ist Standard und schützt den Verkäufer. Bei größeren Geschäften kann ein verlängerter oder erweiterter Eigentumsvorbehalt sinnvoll sein.",
            "laws": ["BGB § 449", "BGB § 929"]},
        7: {"name": "Vertragsstrafe 10%", "type": "Lieferant", "risk": "medium", "usage": 15,
            "text": "Bei Verzug mit der Lieferung ist der Lieferant verpflichtet, eine Vertragsstrafe in Höhe von 10% des Auftragswertes zu zahlen, maximal jedoch 50% des Gesamtauftragswertes.",
            "explanation": "10% Vertragsstrafe ist im oberen Bereich des Üblichen. Die Deckelung auf 50% schützt vor unverhältnismäßigen Forderungen. Achten Sie auf klare Definition des Verzugsbeginns.",
            "laws": ["BGB § 339-345", "BGB § 307"]},
        8: {"name": "Indexmiete jährlich", "type": "Mietvertrag", "risk": "medium", "usage": 12,
            "text": "Die Miete wird jährlich entsprechend der Veränderung des Verbraucherpreisindex angepasst. Eine Anpassung erfolgt nur, wenn der Index um mindestens 3% gestiegen ist.",
            "explanation": "Indexmieten sind bei Gewerbemietverträgen üblich. Die 3%-Schwelle schützt vor häufigen Anpassungen. Achten Sie auf den Basismonat und die Berechnungsmethode.",
            "laws": ["BGB § 557b"]},
    }
    
    clause = clauses.get(clause_id)
    if not clause:
        raise HTTPException(status_code=404, detail="Klausel nicht gefunden")
    
    risk_colors = {"low": "#16a34a", "medium": "#d97706", "high": "#ea580c", "critical": "#dc2626"}
    risk_labels = {"low": "Niedrig", "medium": "Mittel", "high": "Hoch", "critical": "Kritisch"}
    
    laws_html = "".join([f'<span class="badge badge-info" style="margin-right:8px;margin-bottom:8px;">{law}</span>' for law in clause["laws"]])
    
    return get_clause_detail_page(user["name"], clause, risk_colors[clause["risk"]], risk_labels[clause["risk"]], laws_html)


def get_clause_detail_page(user_name, clause, risk_color, risk_label, laws_html):
    """Generiert Klausel-Detailseite."""
    from .pages_enterprise import PAGE_CSS, get_header, get_footer
    
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{clause["name"]} | Klausel-Bibliothek</title>
  <link rel="icon" href="/static/favicon.ico">
  {PAGE_CSS}
</head>
<body>
{get_header(user_name, "tools")}
<main>
<div class="hero">
  <div class="container">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
      <a href="/library" style="color:#fff;opacity:0.7;text-decoration:none;">← Zurück zur Bibliothek</a>
    </div>
    <div class="hero-badge"><span class="dot"></span> {clause["type"].upper()}</div>
    <h1>📜 {clause["name"]}</h1>
    <p>{clause["usage"]}x in Verträgen verwendet</p>
  </div>
</div>
<div class="page-container">
  <!-- Risiko-Badge -->
  <div style="margin-bottom:24px;">
    <span class="badge" style="background:{risk_color}20;color:{risk_color};font-size:1rem;padding:8px 16px;">
      Risiko: {risk_label}
    </span>
  </div>
  
  <!-- Klauseltext -->
  <div class="content-card" style="margin-bottom:24px;">
    <div class="content-card-header"><h3 class="content-card-title">📄 Klauseltext</h3></div>
    <div class="content-card-body">
      <p style="font-size:1.1rem;line-height:1.8;background:#f8fafc;padding:24px;border-radius:12px;border-left:4px solid var(--sbs-blue);">
        „{clause["text"]}"
      </p>
    </div>
  </div>
  
  <!-- Erklärung -->
  <div class="content-card" style="margin-bottom:24px;">
    <div class="content-card-header"><h3 class="content-card-title">💡 Rechtliche Einschätzung</h3></div>
    <div class="content-card-body">
      <p style="line-height:1.8;color:var(--sbs-text);">{clause["explanation"]}</p>
    </div>
  </div>
  
  <!-- Relevante Gesetze -->
  <div class="content-card">
    <div class="content-card-header"><h3 class="content-card-title">⚖️ Relevante Gesetze</h3></div>
    <div class="content-card-body">
      {laws_html}
    </div>
  </div>
  
  <!-- Aktionen -->
  <div style="margin-top:32px;display:flex;gap:16px;">
    <button class="btn btn-primary" onclick="navigator.clipboard.writeText(`{clause["text"]}`)">📋 Klausel kopieren</button>
    <a href="/library" class="btn btn-secondary">← Zurück</a>
  </div>
</div>
</main>
{get_footer()}
</body>
</html>'''
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

@app.get("/api/v3/contracts")
async def api_list_contracts(limit: int = 50):
    """Liste aller Verträge."""
    conn = _init_db()
    try:
        rows = conn.execute(
            "SELECT contract_id, filename, contract_type, created_at, status, risk_level, risk_score "
            "FROM contracts ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    finally:
        conn.close()
    
    contracts = []
    for r in rows:
        contracts.append({
            "contract_id": r[0],
            "filename": r[1],
            "contract_type": r[2],
            "created_at": r[3],
            "status": r[4],
            "risk_level": r[5],
            "risk_score": r[6]
        })
    
    return {"contracts": contracts, "total": len(contracts)}


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
        # Audit-Log
        try:
            user = get_user_info(request)
            from .enterprise_features import log_audit
            log_audit(user.get("email", "anonymous"), "upload", "contract", contract_id, f"Vertrag hochgeladen: {safe_filename}", request.client.host if request.client else None, user.get("name", "Gast"))
        except: pass
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
        # Alle 8 Vertragstypen mit spezifischen Prompts
        from .prompts import get_prompt_for_type
        from .llm_client import call_llm_analysis
        
        system_prompt, user_prompt = get_prompt_for_type(contract_type, contract_text)
        raw_result = call_llm_analysis(system_prompt, user_prompt)
        
        processing_time = time.time() - start_time
        
        # Result aufbereiten
        result = {
            "contract_id": contract_id,
            "source_filename": file_path.name.split("__")[-1] if "__" in file_path.name else file_path.name,
            "contract_type": contract_type,
            "status": "analyzed",
            "processing_time_seconds": round(processing_time, 2),
            "fields_extracted": len([v for v in raw_result.get("extracted_fields", {}).values() if v is not None]),
            "fields_total": len(raw_result.get("extracted_fields", {})) or 14,
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
    """Export als professionelles PDF mit SBS-Branding"""
    from .pdf_report import generate_contract_pdf
    
    conn = _init_db()
    try:
        row = conn.execute("SELECT analysis_json FROM analysis_results WHERE contract_id = ?", (contract_id,)).fetchone()
    finally:
        conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="No analysis found")
    
    analysis = json.loads(row[0])
    
    try:
        pdf_bytes = generate_contract_pdf(analysis)
        
        filename = analysis.get("source_filename", "contract")
        if filename.endswith(".pdf"):
            filename = filename[:-4]
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}_analyse.pdf"}
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

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
    """Erklärt eine Vertragsklausel mit echtem LLM"""
    try:
        body = await request.json()
        clause_text = body.get("clause_text", "")
        contract_type = body.get("contract_type", "general")
    except:
        raise HTTPException(status_code=400, detail="Invalid request body")
    
    if not clause_text:
        raise HTTPException(status_code=400, detail="clause_text required")
    
    # Echte LLM-Analyse
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        type_names = {
            "employment": "Arbeitsvertrag",
            "saas": "SaaS-Vertrag", 
            "vendor": "Lieferantenvertrag",
            "nda": "Geheimhaltungsvereinbarung",
            "service": "Dienstleistungsvertrag",
            "rental": "Mietvertrag",
            "purchase": "Kaufvertrag",
            "general": "Vertrag"
        }
        type_name = type_names.get(contract_type, "Vertrag")
        
        prompt = f"""Analysiere diese Vertragsklausel aus einem {type_name} nach deutschem Recht.

KLAUSEL:
"{clause_text}"

Antworte NUR mit validem JSON ohne Markdown-Formatierung:
{{"risk_level": "low oder medium oder high oder critical", "explanation": "Was bedeutet diese Klausel konkret fuer den Vertragspartner? (2-3 Saetze, verstaendlich)", "legal_assessment": "Rechtliche Einschaetzung nach deutschem Recht - ist die Klausel wirksam? Gibt es Risiken? (2-3 Saetze)", "related_laws": ["Liste der relevanten Paragraphen, z.B. BGB 307, ArbZG 3"], "recommendations": ["Konkrete Handlungsempfehlung 1", "Konkrete Handlungsempfehlung 2"]}}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Du bist ein erfahrener deutscher Rechtsanwalt. Antworte nur mit validem JSON, keine Markdown-Backticks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # JSON extrahieren falls mit Backticks
        if "```" in result_text:
            parts = result_text.split("```")
            for part in parts:
                if "{" in part and "}" in part:
                    result_text = part.strip()
                    if result_text.startswith("json"):
                        result_text = result_text[4:].strip()
                    break
        
        result = json.loads(result_text)
        result["clause_text"] = clause_text
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error in clause explain: {e}")
        return {
            "clause_text": clause_text,
            "risk_level": "medium",
            "explanation": "Die automatische Analyse konnte das Ergebnis nicht verarbeiten.",
            "legal_assessment": "Bitte lassen Sie diese Klausel von einem Rechtsanwalt pruefen.",
            "related_laws": ["BGB"],
            "recommendations": ["Rechtliche Beratung einholen"]
        }
    except Exception as e:
        logger.error(f"Clause explain error: {e}")
        return {
            "clause_text": clause_text,
            "risk_level": "medium",
            "explanation": "Die automatische Analyse ist fehlgeschlagen.",
            "legal_assessment": "Bitte lassen Sie diese Klausel von einem Rechtsanwalt pruefen.",
            "related_laws": ["BGB"],
            "recommendations": ["Rechtliche Beratung einholen"]
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
    logger.info("Contract Intelligence API v0.3.1 starting...")
    logger.info(f"Upload directory: {UPLOAD_DIR.absolute()}")
    
    # DB initialisieren
    _init_db()
    
    dummy_mode = os.getenv("CONTRACT_ANALYZER_DUMMY", "true").lower() == "true"
    if dummy_mode:
        logger.warning("DUMMY MODE ENABLED")
    else:
        if os.getenv("OPENAI_API_KEY"):
            logger.info("OpenAI API key configured")
        else:
            logger.error("OPENAI_API_KEY not set")
    
    logger.info(f"{len(API_KEYS)} API keys configured")
    logger.info("Enterprise Frontend loaded")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Contract Intelligence API shutting down...")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)

# Logout Route
@app.get("/logout")
async def logout():
    """Logout - löscht SSO Cookie und leitet zur Hauptseite"""
    from fastapi.responses import RedirectResponse
    response = RedirectResponse(url="https://app.sbsdeutschland.com/logout", status_code=303)
    response.delete_cookie("sbs_auth_token", domain=".sbsdeutschland.com", path="/")
    response.delete_cookie("sbs_session", domain=".sbsdeutschland.com", path="/")
    return response

# Passwort ändern API
@app.post("/api/change-password")
async def change_password(request: Request):
    """Passwort ändern - nutzt die zentrale User-DB"""
    import hashlib
    user = get_user_info(request)
    if not user.get("email"):
        return {"success": False, "error": "Nicht eingeloggt"}
    
    form = await request.form()
    current_pw = form.get("current_password", "")
    new_pw = form.get("new_password", "")
    
    if len(new_pw) < 8:
        return {"success": False, "error": "Passwort muss mindestens 8 Zeichen haben"}
    
    # Verbinde zur zentralen User-DB (Invoice-App)
    import sqlite3
    conn = sqlite3.connect("/var/www/invoice-app/invoices.db")
    cursor = conn.cursor()
    
    # Prüfe aktuelles Passwort
    current_hash = hashlib.sha256(current_pw.encode()).hexdigest()
    user_row = cursor.execute(
        "SELECT id FROM users WHERE email = ? AND password_hash = ?",
        (user["email"], current_hash)
    ).fetchone()
    
    if not user_row:
        conn.close()
        return {"success": False, "error": "Aktuelles Passwort ist falsch"}
    
    # Neues Passwort setzen
    new_hash = hashlib.sha256(new_pw.encode()).hexdigest()
    cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, user["email"]))
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "Passwort erfolgreich geändert"}

# API-Key generieren
@app.post("/api/settings/generate-key")
async def api_generate_key(request: Request):
    """Generiert einen neuen API-Key für den User"""
    user = get_user_info(request)
    if not user.get("email"):
        return {"success": False, "error": "Nicht eingeloggt"}
    
    from .enterprise_features import generate_api_key
    api_key = generate_api_key(user["email"])
    
    # Audit-Log
    from .enterprise_features import log_audit
    log_audit(user["email"], "api_key_generated", "settings", None, "API-Key generiert", request.client.host if request.client else None, user["name"])
    
    return {"success": True, "api_key": api_key}

# API-Key widerrufen
@app.post("/api/settings/revoke-key")
async def api_revoke_key(request: Request):
    """Widerruft den API-Key des Users"""
    user = get_user_info(request)
    if not user.get("email"):
        return {"success": False, "error": "Nicht eingeloggt"}
    
    from .enterprise_features import revoke_api_key
    result = revoke_api_key(user["email"])
    
    if result.get("success"):
        from .enterprise_features import log_audit
        log_audit(user["email"], "api_key_revoked", "settings", None, "API-Key widerrufen", request.client.host if request.client else None, user["name"])
    
    return result

# Notification Settings speichern
@app.post("/api/settings/notifications")
async def api_save_notifications(request: Request):
    """Speichert Notification-Einstellungen"""
    user = get_user_info(request)
    if not user.get("email"):
        return {"success": False, "error": "Nicht eingeloggt"}
    
    form = await request.form()
    email_notif = form.get("notification_email") == "true"
    slack_notif = form.get("notification_slack") == "true"
    
    from .enterprise_features import update_user_settings
    result = update_user_settings(user["email"], notification_email=email_notif, notification_slack=slack_notif)
    
    return result

# Team-Mitglied einladen
@app.post("/api/team/invite")
async def api_team_invite(request: Request):
    """Lädt ein neues Team-Mitglied ein"""
    user = get_user_info(request)
    if not user.get("email"):
        return {"success": False, "error": "Nicht eingeloggt"}
    
    form = await request.form()
    invite_email = form.get("email", "").strip()
    invite_name = form.get("name", "").strip()
    invite_role = form.get("role", "viewer")
    
    if not invite_email or "@" not in invite_email:
        return {"success": False, "error": "Ungültige E-Mail-Adresse"}
    
    if not invite_name:
        return {"success": False, "error": "Name erforderlich"}
    
    from .enterprise_features import add_team_member, log_audit
    result = add_team_member(invite_email, invite_name, invite_role, user["email"])
    
    if result.get("success"):
        log_audit(user["email"], "team_invite", "team", None, f"Eingeladen: {invite_email} als {invite_role}", request.client.host if request.client else None, user["name"])
    
    return result

# Team-Mitglied entfernen
@app.post("/api/team/remove")
async def api_team_remove(request: Request):
    """Entfernt ein Team-Mitglied"""
    user = get_user_info(request)
    if not user.get("email"):
        return {"success": False, "error": "Nicht eingeloggt"}
    
    form = await request.form()
    remove_email = form.get("email", "").strip()
    
    from .enterprise_features import remove_team_member, log_audit
    result = remove_team_member(remove_email)
    
    if result.get("success"):
        log_audit(user["email"], "team_remove", "team", None, f"Entfernt: {remove_email}", request.client.host if request.client else None, user["name"])
    
    return result

# ============================================================================
# CONTRACT COPILOT
# ============================================================================

@app.get("/copilot", response_class=HTMLResponse)
async def copilot_page(request: Request):
    """Contract Copilot - Chat mit Verträgen"""
    user = get_user_info(request)
    user_name = user.get("name", "Gast")
    from .copilot_page import get_copilot_page
    return get_copilot_page(user_name)

@app.post("/api/copilot/chat")
async def copilot_chat(request: Request):
    """Chat mit Contract Copilot"""
    user = get_user_info(request)
    
    try:
        body = await request.json()
        message = body.get("message", "").strip()
        contract_id = body.get("contract_id")
        history = body.get("history", [])
    except:
        form = await request.form()
        message = form.get("message", "").strip()
        contract_id = form.get("contract_id")
        history = []
    
    if not message:
        return {"success": False, "error": "Keine Nachricht"}
    
    # Kontext laden falls contract_id vorhanden
    context = ""
    contract_info = None
    if contract_id:
        conn = _init_db()
        row = conn.execute("SELECT analysis_json FROM analysis_results WHERE contract_id = ?", (contract_id,)).fetchone()
        contract_row = conn.execute("SELECT filename, contract_type FROM contracts WHERE contract_id = ?", (contract_id,)).fetchone()
        conn.close()
        
        if row:
            import json
            analysis = json.loads(row[0])
            contract_info = {
                "filename": contract_row[0] if contract_row else "Unbekannt",
                "type": contract_row[1] if contract_row else "general",
                "risk_level": analysis.get("risk_assessment", {}).get("overall_risk_level", "unknown"),
                "risk_score": analysis.get("risk_assessment", {}).get("overall_risk_score", 0)
            }
            context = f"""
VERTRAGSKONTEXT:
- Datei: {contract_info['filename']}
- Typ: {contract_info['type']}
- Risikolevel: {contract_info['risk_level']} ({contract_info['risk_score']}/100)
- Zusammenfassung: {analysis.get('risk_assessment', {}).get('executive_summary', 'Keine Zusammenfassung')}

EXTRAHIERTE DATEN:
{json.dumps(analysis.get('extracted_data', {}), indent=2, ensure_ascii=False)}

RISIKEN:
{json.dumps(analysis.get('risk_assessment', {}).get('critical_risks', []) + analysis.get('risk_assessment', {}).get('high_risks', []), indent=2, ensure_ascii=False)}
"""
    
    # Alle Verträge als Übersicht wenn kein spezifischer ausgewählt
    if not contract_id:
        conn = _init_db()
        contracts = conn.execute("SELECT contract_id, filename, contract_type, status, risk_level, risk_score FROM contracts ORDER BY created_at DESC LIMIT 20").fetchall()
        conn.close()
        
        if contracts:
            context = "VERFÜGBARE VERTRÄGE:\n"
            for c in contracts:
                context += f"- {c[1]} (Typ: {c[2]}, Status: {c[3]}, Risiko: {c[4] or 'unbekannt'})\n"
    
    # OpenAI API Call
    import os
    import httpx
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"success": False, "error": "OpenAI API nicht konfiguriert"}
    
    system_prompt = f"""Du bist der SBS Contract Copilot, ein KI-Assistent für Vertragsanalyse.
Du hilfst Nutzern bei Fragen zu ihren Verträgen, Risiken und rechtlichen Themen.

Deine Aufgaben:
- Verträge erklären und zusammenfassen
- Risiken identifizieren und bewerten
- Klauseln erläutern
- Handlungsempfehlungen geben
- Fristen und wichtige Termine hervorheben

Antworte auf Deutsch, professionell aber verständlich.
Wenn du Risiken oder problematische Klauseln findest, weise klar darauf hin.

{context}
"""

    messages = [{"role": "system", "content": system_prompt}]
    for h in history[-10:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": message})
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": "gpt-4o-mini", "messages": messages, "temperature": 0.7, "max_tokens": 1500}
            )
            result = response.json()
            
            if "choices" in result:
                answer = result["choices"][0]["message"]["content"]
                
                # Audit Log
                from .enterprise_features import log_audit
                log_audit(user.get("email", "anonymous"), "copilot_chat", "copilot", contract_id, f"Frage: {message[:50]}...", request.client.host if request.client else None, user.get("name", "Gast"))
                # Usage Tracking
                try:
                    from .usage_tracking import track_event
                    track_event(user.get("email", "anonymous"), "copilot_query", contract_id)
                except: pass
                
                return {"success": True, "answer": answer, "contract_info": contract_info}
            else:
                return {"success": False, "error": result.get("error", {}).get("message", "API Fehler")}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/copilot/contracts")
async def copilot_contracts(request: Request):
    """Liste aller Verträge für Copilot Kontext"""
    conn = _init_db()
    contracts = conn.execute("""
        SELECT c.contract_id, c.filename, c.contract_type, c.status, c.risk_level, c.risk_score, c.created_at
        FROM contracts c
        ORDER BY c.created_at DESC
        LIMIT 50
    """).fetchall()
    conn.close()
    
    return {"contracts": [
        {"id": c[0], "filename": c[1], "type": c[2], "status": c[3], "risk_level": c[4], "risk_score": c[5], "created_at": c[6]}
        for c in contracts
    ]}

# ============================================================================
# FRISTEN-ALERTS
# ============================================================================

@app.get("/api/deadlines")
async def get_deadlines(request: Request):
    """Holt kommende Vertragsfristen"""
    from .deadline_alerts import get_upcoming_deadlines, init_alerts_table
    init_alerts_table()
    deadlines = get_upcoming_deadlines(days_ahead=60)
    return {"deadlines": deadlines, "count": len(deadlines)}

@app.get("/api/alerts/pending")
async def get_pending_alerts(request: Request):
    """Holt ausstehende Alerts"""
    user = get_user_info(request)
    from .deadline_alerts import get_pending_alerts
    alerts = get_pending_alerts(user.get("email"))
    return {"alerts": alerts, "count": len(alerts)}

@app.post("/api/alerts/check")
async def run_alert_check(request: Request):
    """Führt manuellen Fristen-Check aus (Admin only)"""
    user = get_user_info(request)
    if not user.get("is_admin"):
        return {"success": False, "error": "Nur für Admins"}
    
    from .deadline_alerts import run_daily_check
    run_daily_check()
    return {"success": True, "message": "Fristen-Check durchgeführt"}

@app.get("/deadlines", response_class=HTMLResponse)
async def deadlines_page(request: Request):
    """Fristen-Übersicht Seite"""
    user = get_user_info(request)
    user_name = user.get("name", "Gast")
    from .deadline_page import get_deadlines_page
    return get_deadlines_page(user_name)

# ============================================================================
# USAGE TRACKING
# ============================================================================

@app.get("/api/usage")
async def get_usage(request: Request):
    """Holt aktuellen Verbrauch des Users"""
    user = get_user_info(request)
    email = user.get("email", "anonymous")
    
    from .usage_tracking import get_usage_with_limits, init_usage_tables
    init_usage_tables()
    
    data = get_usage_with_limits(email)
    return data

@app.get("/api/usage/history")
async def get_usage_history(request: Request):
    """Holt Usage-Historie"""
    user = get_user_info(request)
    email = user.get("email", "anonymous")
    
    from .usage_tracking import get_usage_history
    history = get_usage_history(email, months=6)
    return {"history": history}

@app.post("/api/usage/check")
async def check_usage_limit(request: Request):
    """Prüft ob Limit erreicht"""
    user = get_user_info(request)
    email = user.get("email", "anonymous")
    
    body = await request.json()
    event_type = body.get("event_type", "analysis")
    
    from .usage_tracking import check_limit
    result = check_limit(email, event_type)
    return result

# ============================================================================
# STRIPE BILLING
# ============================================================================

@app.post("/api/billing/checkout")
async def create_checkout(request: Request):
    """Erstellt Stripe Checkout Session für Plan-Upgrade"""
    user = get_user_info(request)
    email = user.get("email")
    
    if not email:
        return {"success": False, "error": "Nicht eingeloggt"}
    
    try:
        body = await request.json()
        plan_id = body.get("plan_id", "starter")
        interval = body.get("interval", "monthly")
    except:
        form = await request.form()
        plan_id = form.get("plan_id", "starter")
        interval = form.get("interval", "monthly")
    
    from .stripe_billing import create_checkout_session
    result = create_checkout_session(email, plan_id, interval)
    return result

@app.get("/api/billing/portal")
async def billing_portal(request: Request):
    """Redirect zum Stripe Customer Portal"""
    user = get_user_info(request)
    email = user.get("email")
    
    if not email:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/login")
    
    from .stripe_billing import create_portal_session
    result = create_portal_session(email)
    
    if result.get("success"):
        from fastapi.responses import RedirectResponse
        return RedirectResponse(result["portal_url"])
    else:
        return {"success": False, "error": result.get("error")}

@app.post("/api/billing/webhook")
async def stripe_webhook(request: Request):
    """Stripe Webhook Endpoint"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    
    from .stripe_billing import handle_webhook
    result = handle_webhook(payload, sig_header)
    
    if result.get("success"):
        return {"received": True}
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=result.get("error"))

@app.get("/api/billing/status")
async def billing_status(request: Request):
    """Holt aktuellen Billing-Status"""
    user = get_user_info(request)
    email = user.get("email")
    
    if not email:
        return {"success": False, "error": "Nicht eingeloggt"}
    
    from .stripe_billing import get_subscription_status
    from .usage_tracking import get_user_plan, get_monthly_usage
    
    stripe_status = get_subscription_status(email)
    plan = get_user_plan(email)
    usage = get_monthly_usage(email)
    
    return {
        "stripe": stripe_status,
        "plan": plan,
        "usage": usage
    }

@app.get("/pricing")
async def pricing_page(request: Request):
    """Redirect zur Hauptseite Preisseite"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse("https://sbsdeutschland.com/loesungen/vertragsanalyse/preise.html")

# ============================================================================
# 2FA / TOTP AUTHENTICATION
# ============================================================================

@app.get("/api/2fa/status")
async def get_2fa_status(request: Request):
    """Holt 2FA Status des Users"""
    user = get_user_info(request)
    email = user.get("email")
    if not email:
        return {"error": "Nicht eingeloggt"}
    
    from .two_factor_auth import get_2fa_status
    return get_2fa_status(email)

@app.post("/api/2fa/setup")
async def setup_2fa(request: Request):
    """Startet 2FA Setup - generiert Secret und QR Code"""
    user = get_user_info(request)
    email = user.get("email")
    if not email:
        return {"error": "Nicht eingeloggt"}
    
    from .two_factor_auth import generate_totp_secret
    return generate_totp_secret(email)

@app.post("/api/2fa/enable")
async def enable_2fa(request: Request):
    """Aktiviert 2FA nach Code-Verifikation"""
    user = get_user_info(request)
    email = user.get("email")
    if not email:
        return {"error": "Nicht eingeloggt"}
    
    body = await request.json()
    code = body.get("code", "")
    
    from .two_factor_auth import enable_2fa as do_enable
    result = do_enable(email, code)
    
    if result.get("success"):
        from .enterprise_features import log_audit
        log_audit(email, "2fa_enabled", "security", None, "2FA aktiviert", None, request.client.host)
    
    return result

@app.post("/api/2fa/verify")
async def verify_2fa(request: Request):
    """Verifiziert 2FA Code"""
    user = get_user_info(request)
    email = user.get("email")
    if not email:
        return {"error": "Nicht eingeloggt"}
    
    body = await request.json()
    code = body.get("code", "")
    
    from .two_factor_auth import verify_totp
    return verify_totp(email, code, request.client.host)

@app.post("/api/2fa/disable")
async def disable_2fa(request: Request):
    """Deaktiviert 2FA"""
    user = get_user_info(request)
    email = user.get("email")
    if not email:
        return {"error": "Nicht eingeloggt"}
    
    body = await request.json()
    code = body.get("code", "")
    
    from .two_factor_auth import disable_2fa as do_disable
    result = do_disable(email, code)
    
    if result.get("success"):
        from .enterprise_features import log_audit
        log_audit(email, "2fa_disabled", "security", None, "2FA deaktiviert", None, request.client.host)
    
    return result

@app.post("/api/2fa/backup-codes")
async def regenerate_backup_codes(request: Request):
    """Generiert neue Backup Codes"""
    user = get_user_info(request)
    email = user.get("email")
    if not email:
        return {"error": "Nicht eingeloggt"}
    
    body = await request.json()
    code = body.get("code", "")
    
    from .two_factor_auth import regenerate_backup_codes
    return regenerate_backup_codes(email, code)

@app.get("/security", response_class=HTMLResponse)
async def security_page(request: Request):
    """Security Settings Seite mit 2FA"""
    user = get_user_info(request)
    from .security_page import get_security_page
    return get_security_page(user.get("name", "User"), user.get("email"))

# ============================================================================
# ONBOARDING
# ============================================================================

@app.get("/onboarding", response_class=HTMLResponse)
async def onboarding_page(request: Request):
    """Onboarding Wizard fuer neue User"""
    user = get_user_info(request)
    from .onboarding import get_onboarding_page
    return get_onboarding_page(user.get("name", "User"), user.get("email"))

@app.post("/api/onboarding/complete")
async def complete_onboarding(request: Request):
    """Markiert Onboarding als abgeschlossen"""
    user = get_user_info(request)
    email = user.get("email")
    if not email:
        return {"success": False}
    
    # Speichere in DB
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO user_settings (user_email, onboarding_completed, onboarding_completed_at)
        VALUES (?, 1, CURRENT_TIMESTAMP)
        ON CONFLICT(user_email) DO UPDATE SET
            onboarding_completed = 1,
            onboarding_completed_at = CURRENT_TIMESTAMP
    """, (email,))
    conn.commit()
    conn.close()
    
    from .enterprise_features import log_audit
    log_audit(email, "onboarding_completed", "user", None, "Onboarding abgeschlossen", None, request.client.host)
    
    return {"success": True}

@app.get("/api/onboarding/status")
async def onboarding_status(request: Request):
    """Prueft ob User Onboarding abgeschlossen hat"""
    user = get_user_info(request)
    email = user.get("email")
    if not email:
        return {"completed": False}
    
    conn = get_db_connection()
    row = conn.execute(
        "SELECT onboarding_completed FROM user_settings WHERE user_email = ?",
        (email,)
    ).fetchone()
    conn.close()
    
    return {"completed": bool(row and row[0])}
