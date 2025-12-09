# app/logging_service.py
"""
Audit- & Monitoring-Logging für Contract Analyzer.
CFO-fähig mit Kennzahlen-Tracking und Multi-Tenant-Support.

Speichert in SQLite:
- Jeden Analyse-Event mit Metadaten
- Fehlerquoten, Durchsnittszeiten, Token-Nutzung
- Pro Tenant: Monatliche Limits, Nutzung, Kosten
"""

import sqlite3
import logging
import os
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

# ============================================================================
# SETUP
# ============================================================================

LOG_DB = Path("analysis.sqlite")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Logging zu Datei & Console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "app.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


# ============================================================================
# DATABASE SCHEMA & INIT
# ============================================================================

def setup_logging():
    """Initialisiert die SQLite-DB für Logging."""
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS analysis_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            contract_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            contract_type TEXT NOT NULL,
            language TEXT DEFAULT 'de',
            status TEXT NOT NULL,
            duration_ms INTEGER,
            llm_model TEXT,
            llm_input_tokens INTEGER,
            llm_output_tokens INTEGER,
            num_risk_flags INTEGER DEFAULT 0,
            error_message TEXT,
            risk_flags TEXT
        )
        """)
        
        conn.execute("""
        CREATE TABLE IF NOT EXISTS tenant_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT NOT NULL UNIQUE,
            tenant_name TEXT,
            api_key TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            analyses_monthly_limit INTEGER DEFAULT 1000,
            analyses_this_month INTEGER DEFAULT 0,
            tokens_this_month INTEGER DEFAULT 0,
            last_analysis_at TEXT
        )
        """)
        
        conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            contract_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            feedback_text TEXT,
            rating INTEGER
        )
        """)
        
        conn.commit()
        logger.info("✓ Database initialized")


# ============================================================================
# CONTEXT MANAGER FÜR DB
# ============================================================================

@contextmanager
def get_db():
    """Context manager für sichere DB-Connections."""
    conn = sqlite3.connect(LOG_DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ============================================================================
# LOGGING FUNKTIONEN
# ============================================================================

def log_analysis_event(
    contract_id: str,
    tenant_id: str,
    contract_type: str,
    language: str = "de",
    status: str = "success",
    duration_ms: int = 0,
    llm_model: str = "gpt-4.1-mini",
    llm_input_tokens: int = None,
    llm_output_tokens: int = None,
    num_risk_flags: int = 0,
    error_message: str = None,
):
    """
    Logged einen einzelnen Analyse-Event.
    
    Args:
        contract_id: UUID des Vertrags
        tenant_id: Tenant/Kanzlei-ID
        contract_type: "employment" oder "saas"
        language: "de" oder "en"
        status: "success" oder "error"
        duration_ms: Dauer in Millisekunden
        llm_model: z.B. "gpt-4.1-mini"
        llm_input_tokens: Eingabe-Tokens (optional)
        llm_output_tokens: Output-Tokens (optional)
        num_risk_flags: Anzahl erkannter Risiken
        error_message: Falls Status=error
    """
    try:
        with get_db() as conn:
            conn.execute("""
            INSERT INTO analysis_log (
                contract_id, tenant_id, contract_type, language,
                status, duration_ms, llm_model, llm_input_tokens,
                llm_output_tokens, num_risk_flags, error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contract_id, tenant_id, contract_type, language,
                status, duration_ms, llm_model, llm_input_tokens,
                llm_output_tokens, num_risk_flags, error_message,
            ))
            
            # Update tenant_usage
            total_tokens = (llm_input_tokens or 0) + (llm_output_tokens or 0)
            conn.execute("""
            UPDATE tenant_usage
            SET analyses_this_month = analyses_this_month + 1,
                tokens_this_month = tokens_this_month + ?,
                last_analysis_at = CURRENT_TIMESTAMP
            WHERE tenant_id = ?
            """, (total_tokens, tenant_id))
            
            conn.commit()
            
            status_icon = "✓" if status == "success" else "✗"
            logger.info(
                f"{status_icon} {contract_type} | {tenant_id} | {duration_ms}ms | "
                f"{num_risk_flags} risks | {llm_input_tokens or '?'} in / {llm_output_tokens or '?'} out tokens"
            )
    
    except Exception as e:
        logger.error(f"Failed to log analysis event: {e}")


def log_feedback(contract_id: str, tenant_id: str, feedback_text: str, rating: int = None):
    """Logged Nutzerfeedback zu einer Analyse."""
    try:
        with get_db() as conn:
            conn.execute("""
            INSERT INTO feedback (contract_id, tenant_id, feedback_text, rating)
            VALUES (?, ?, ?, ?)
            """, (contract_id, tenant_id, feedback_text, rating))
            conn.commit()
            logger.info(f"✓ Feedback logged for {contract_id}")
    except Exception as e:
        logger.error(f"Failed to log feedback: {e}")


# ============================================================================
# CFO-ABFRAGEN (für Dashboards & Reports)
# ============================================================================

def get_analysis_metrics(days: int = 30) -> dict:
    """
    Gibt Analyse-Metriken für die letzten N Tage zurück.
    
    Returns:
        {
            'total_analyses': int,
            'successful': int,
            'failed': int,
            'error_rate': float,
            'avg_duration_ms': float,
            'total_tokens': int,
        }
    """
    with get_db() as conn:
        rows = conn.execute(f"""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as successful,
            SUM(CASE WHEN status='error' THEN 1 ELSE 0 END) as failed,
            AVG(duration_ms) as avg_duration_ms,
            SUM(COALESCE(llm_input_tokens, 0) + COALESCE(llm_output_tokens, 0)) as total_tokens
        FROM analysis_log
        WHERE datetime(created_at) > datetime('now', '-{days} days')
        """).fetchall()
        
        row = rows[0] if rows else None
        if not row:
            return {
                'total_analyses': 0,
                'successful': 0,
                'failed': 0,
                'error_rate': 0.0,
                'avg_duration_ms': 0,
                'total_tokens': 0,
            }
        
        total = row[0] or 0
        successful = row[1] or 0
        failed = row[2] or 0
        error_rate = (failed / total * 100) if total > 0 else 0.0
        avg_duration = row[3] or 0
        total_tokens = row[4] or 0
        
        return {
            'total_analyses': total,
            'successful': successful,
            'failed': failed,
            'error_rate': round(error_rate, 2),
            'avg_duration_ms': round(avg_duration, 1),
            'total_tokens': total_tokens,
        }


def get_tenant_metrics(tenant_id: str) -> dict:
    """Gibt Metriken für einen spezifischen Tenant zurück."""
    with get_db() as conn:
        # Tenant-Info
        tenant_row = conn.execute("""
        SELECT tenant_name, analyses_monthly_limit, analyses_this_month, tokens_this_month
        FROM tenant_usage
        WHERE tenant_id = ?
        """, (tenant_id,)).fetchone()
        
        if not tenant_row:
            return {'error': 'Tenant not found'}
        
        # Analyse-Stats
        stats_row = conn.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as successful,
            AVG(duration_ms) as avg_duration_ms,
            AVG(num_risk_flags) as avg_risk_flags
        FROM analysis_log
        WHERE tenant_id = ?
        """, (tenant_id,)).fetchone()
        
        return {
            'tenant_id': tenant_id,
            'tenant_name': tenant_row[1],
            'monthly_limit': tenant_row[2],
            'analyses_this_month': tenant_row[3],
            'tokens_this_month': tenant_row[4],
            'total_all_time': stats_row[0] or 0,
            'success_rate': round((stats_row[1] / stats_row[0] * 100), 2) if stats_row[0] else 0.0,
            'avg_duration_ms': round(stats_row[2], 1) if stats_row[2] else 0,
            'avg_risk_flags_per_contract': round(stats_row[3], 1) if stats_row[3] else 0,
        }


def get_daily_analysis_count(days: int = 30) -> list:
    """Gibt Anzahl Analysen pro Tag für Chart zurück."""
    with get_db() as conn:
        rows = conn.execute(f"""
        SELECT DATE(created_at) as day, COUNT(*) as count, 
               SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as successful
        FROM analysis_log
        WHERE datetime(created_at) > datetime('now', '-{days} days')
        GROUP BY DATE(created_at)
        ORDER BY day ASC
        """).fetchall()
        
        return [
            {'day': row[0], 'total': row[1], 'successful': row[2]}
            for row in rows
        ]


def get_contract_type_distribution() -> dict:
    """Verteilung nach Vertragstyp."""
    with get_db() as conn:
        rows = conn.execute("""
        SELECT contract_type, COUNT(*) as count,
               SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as successful
        FROM analysis_log
        GROUP BY contract_type
        """).fetchall()
        
        return {
            row[0]: {'total': row[1], 'successful': row[2]}
            for row in rows
        }


def get_risk_distribution(contract_type: str = None) -> dict:
    """Durchschnittliche Risiko-Flags pro Analyse (optional nach Typ gefiltert)."""
    with get_db() as conn:
        if contract_type:
            row = conn.execute("""
            SELECT AVG(num_risk_flags) as avg_risks, MAX(num_risk_flags) as max_risks
            FROM analysis_log
            WHERE status='success' AND contract_type = ?
            """, (contract_type,)).fetchone()
        else:
            row = conn.execute("""
            SELECT AVG(num_risk_flags) as avg_risks, MAX(num_risk_flags) as max_risks
            FROM analysis_log
            WHERE status='success'
            """).fetchone()
        
        return {
            'avg_risk_flags': round(row[0], 1) if row[0] else 0,
            'max_risk_flags': row[1] or 0,
        }


def get_error_distribution() -> dict:
    """Fehler nach Art kategorisiert."""
    with get_db() as conn:
        rows = conn.execute("""
        SELECT SUBSTR(error_message, 1, 50) as error_type, COUNT(*) as count
        FROM analysis_log
        WHERE status='error' AND error_message IS NOT NULL
        GROUP BY SUBSTR(error_message, 1, 50)
        ORDER BY count DESC
        LIMIT 10
        """).fetchall()
        
        return {
            row[0]: row[1]
            for row in rows
        }


# ============================================================================
# TENANT MANAGEMENT
# ============================================================================

def register_tenant(tenant_id: str, tenant_name: str, api_key: str, monthly_limit: int = 1000):
    """Registriert einen neuen Tenant."""
    try:
        with get_db() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO tenant_usage
            (tenant_id, tenant_name, api_key, analyses_monthly_limit)
            VALUES (?, ?, ?, ?)
            """, (tenant_id, tenant_name, api_key, monthly_limit))
            conn.commit()
            logger.info(f"✓ Tenant registered: {tenant_id} ({tenant_name})")
    except Exception as e:
        logger.error(f"Failed to register tenant: {e}")


def verify_tenant_limit(tenant_id: str) -> bool:
    """Prüft, ob Tenant monatliches Limit überschritten hat."""
    with get_db() as conn:
        row = conn.execute("""
        SELECT analyses_monthly_limit, analyses_this_month
        FROM tenant_usage
        WHERE tenant_id = ?
        """, (tenant_id,)).fetchone()
        
        if not row:
            return False
        
        return row[1] < row[0]


# ============================================================================
# CRON / MAINTENANCE
# ============================================================================

def reset_monthly_counters():
    """Reset monthly counters (aufgerufen am 1. des Monats)."""
    try:
        with get_db() as conn:
            conn.execute("""
            UPDATE tenant_usage
            SET analyses_this_month = 0, tokens_this_month = 0
            """)
            conn.commit()
            logger.info("✓ Monthly counters reset")
    except Exception as e:
        logger.error(f"Failed to reset monthly counters: {e}")


def cleanup_old_logs(days: int = 90):
    """Löscht Analyse-Logs älter als N Tage."""
    try:
        with get_db() as conn:
            conn.execute(f"""
            DELETE FROM analysis_log
            WHERE datetime(created_at) < datetime('now', '-{days} days')
            """)
            deleted = conn.total_changes
            conn.commit()
            logger.info(f"✓ Cleaned up {deleted} old log entries (>{days} days)")
    except Exception as e:
        logger.error(f"Failed to cleanup logs: {e}")


# ============================================================================
# CFO DASHBOARD QUERIES
# ============================================================================

def get_cfo_dashboard_summary() -> dict:
    """
    Gibt CFO-relevante KPIs für das Dashboard zurück.
    """
    metrics = get_analysis_metrics(days=30)
    
    with get_db() as conn:
        # Top-Risiken
        risk_rows = conn.execute("""
        SELECT title, severity, COUNT(*) as count
        FROM analysis_log, json_each(risk_flags)
        WHERE datetime(created_at) > datetime('now', '-30 days')
        GROUP BY title, severity
        ORDER BY count DESC
        LIMIT 10
        """).fetchall()
        
        # Kosten-Schätzung (bei $0.0015 pro 1K Tokens)
        estimated_cost_usd = (metrics['total_tokens'] / 1000) * 0.0015
        
        return {
            'kpi': metrics,
            'estimated_monthly_cost_usd': round(estimated_cost_usd, 2),
            'top_risks': [
                {'title': row[0], 'severity': row[1], 'count': row[2]}
                for row in risk_rows
            ]
        }


if __name__ == "__main__":
    # CLI für Testing & Reporting
    setup_logging()
    
    print("\n=== CONTRACT ANALYZER – METRICS DASHBOARD ===\n")
    
    metrics = get_analysis_metrics(days=30)
    print(f"Last 30 Days:")
    print(f"  • Total Analyses: {metrics['total_analyses']}")
    print(f"  • Successful: {metrics['successful']}")
    print(f"  • Failed: {metrics['failed']}")
    print(f"  • Error Rate: {metrics['error_rate']}%")
    print(f"  • Avg Duration: {metrics['avg_duration_ms']}ms")
    print(f"  • Total Tokens: {metrics['total_tokens']}")
    
    print(f"\nContract Types:")
    types = get_contract_type_distribution()
    for ctype, counts in types.items():
        print(f"  • {ctype}: {counts['total']} total, {counts['successful']} successful")
    
    print(f"\nRisk Distribution:")
    risks = get_risk_distribution()
    print(f"  • Avg Risks: {risks['avg_risk_flags']}")
    print(f"  • Max Risks: {risks['max_risk_flags']}")
    
    # CFO-Summary
    cfo = get_cfo_dashboard_summary()
    print(f"\nEstimated Monthly Cost: ${cfo['estimated_monthly_cost_usd']}")
    
    print("\n" + "="*40 + "\n")

