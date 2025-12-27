"""
Usage Tracking System
- Trackt API-Calls, Analysen, Copilot-Anfragen
- Monatliche Limits pro Plan
- Verbrauchsstatistiken
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Optional
import json

DB_PATH = "/var/www/contract-app/data/contracts.db"

# Plan-Limits
PLAN_LIMITS = {
    "free": {
        "analyses_per_month": 5,
        "copilot_queries_per_month": 20,
        "contracts_stored": 10,
        "team_members": 1,
        "name": "Free",
        "price": 0
    },
    "starter": {
        "analyses_per_month": 50,
        "copilot_queries_per_month": 200,
        "contracts_stored": 100,
        "team_members": 3,
        "name": "Starter",
        "price": 69
    },
    "professional": {
        "analyses_per_month": 200,
        "copilot_queries_per_month": 1000,
        "contracts_stored": 500,
        "team_members": 10,
        "name": "Professional",
        "price": 179
    },
    "enterprise": {
        "analyses_per_month": -1,  # unlimited
        "copilot_queries_per_month": -1,
        "contracts_stored": -1,
        "team_members": -1,
        "name": "Enterprise",
        "price": 449
    }
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_usage_tables():
    """Erstellt Usage-Tabellen"""
    conn = get_db()
    
    # Usage Events (jede einzelne Aktion)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            event_type TEXT NOT NULL,
            resource_id TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Monthly Usage Summary (aggregiert)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage_monthly (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            month TEXT NOT NULL,
            analyses_count INTEGER DEFAULT 0,
            copilot_queries INTEGER DEFAULT 0,
            exports_count INTEGER DEFAULT 0,
            api_calls INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_email, month)
        )
    """)
    
    # User Plans
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_plans (
            user_email TEXT PRIMARY KEY,
            plan_id TEXT DEFAULT 'free',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            stripe_customer_id TEXT,
            stripe_subscription_id TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Usage-Tabellen initialisiert")

def track_event(user_email: str, event_type: str, resource_id: str = None, metadata: dict = None):
    """Trackt ein Usage-Event"""
    conn = get_db()
    
    # Event speichern
    conn.execute("""
        INSERT INTO usage_events (user_email, event_type, resource_id, metadata)
        VALUES (?, ?, ?, ?)
    """, (user_email, event_type, resource_id, json.dumps(metadata) if metadata else None))
    
    # Monthly Summary updaten
    month = datetime.now().strftime("%Y-%m")
    
    # Prüfen ob Eintrag existiert
    existing = conn.execute(
        "SELECT id FROM usage_monthly WHERE user_email = ? AND month = ?",
        (user_email, month)
    ).fetchone()
    
    if existing:
        # Update basierend auf Event-Typ
        if event_type == "analysis":
            conn.execute("UPDATE usage_monthly SET analyses_count = analyses_count + 1, updated_at = CURRENT_TIMESTAMP WHERE user_email = ? AND month = ?", (user_email, month))
        elif event_type == "copilot_query":
            conn.execute("UPDATE usage_monthly SET copilot_queries = copilot_queries + 1, updated_at = CURRENT_TIMESTAMP WHERE user_email = ? AND month = ?", (user_email, month))
        elif event_type == "export":
            conn.execute("UPDATE usage_monthly SET exports_count = exports_count + 1, updated_at = CURRENT_TIMESTAMP WHERE user_email = ? AND month = ?", (user_email, month))
        elif event_type == "api_call":
            conn.execute("UPDATE usage_monthly SET api_calls = api_calls + 1, updated_at = CURRENT_TIMESTAMP WHERE user_email = ? AND month = ?", (user_email, month))
    else:
        # Neuen Eintrag erstellen
        analyses = 1 if event_type == "analysis" else 0
        copilot = 1 if event_type == "copilot_query" else 0
        exports = 1 if event_type == "export" else 0
        api = 1 if event_type == "api_call" else 0
        
        conn.execute("""
            INSERT INTO usage_monthly (user_email, month, analyses_count, copilot_queries, exports_count, api_calls)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_email, month, analyses, copilot, exports, api))
    
    conn.commit()
    conn.close()

def get_user_plan(user_email: str) -> Dict:
    """Holt den Plan eines Users"""
    conn = get_db()
    
    row = conn.execute(
        "SELECT * FROM user_plans WHERE user_email = ?",
        (user_email,)
    ).fetchone()
    
    conn.close()
    
    if row:
        plan_id = row['plan_id']
        return {
            "plan_id": plan_id,
            "started_at": row['started_at'],
            "expires_at": row['expires_at'],
            **PLAN_LIMITS.get(plan_id, PLAN_LIMITS['free'])
        }
    else:
        return {"plan_id": "free", **PLAN_LIMITS['free']}

def set_user_plan(user_email: str, plan_id: str, stripe_customer_id: str = None, stripe_subscription_id: str = None):
    """Setzt den Plan eines Users"""
    conn = get_db()
    
    conn.execute("""
        INSERT INTO user_plans (user_email, plan_id, stripe_customer_id, stripe_subscription_id, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_email) DO UPDATE SET
            plan_id = excluded.plan_id,
            stripe_customer_id = excluded.stripe_customer_id,
            stripe_subscription_id = excluded.stripe_subscription_id,
            updated_at = CURRENT_TIMESTAMP
    """, (user_email, plan_id, stripe_customer_id, stripe_subscription_id))
    
    conn.commit()
    conn.close()

def get_monthly_usage(user_email: str, month: str = None) -> Dict:
    """Holt den monatlichen Verbrauch"""
    if not month:
        month = datetime.now().strftime("%Y-%m")
    
    conn = get_db()
    
    row = conn.execute(
        "SELECT * FROM usage_monthly WHERE user_email = ? AND month = ?",
        (user_email, month)
    ).fetchone()
    
    conn.close()
    
    if row:
        return {
            "month": month,
            "analyses_count": row['analyses_count'],
            "copilot_queries": row['copilot_queries'],
            "exports_count": row['exports_count'],
            "api_calls": row['api_calls']
        }
    else:
        return {
            "month": month,
            "analyses_count": 0,
            "copilot_queries": 0,
            "exports_count": 0,
            "api_calls": 0
        }

def get_usage_with_limits(user_email: str) -> Dict:
    """Holt Verbrauch mit Limits und Prozentsätzen"""
    plan = get_user_plan(user_email)
    usage = get_monthly_usage(user_email)
    
    def calc_percentage(used, limit):
        if limit == -1:  # unlimited
            return 0
        if limit == 0:
            return 100
        return min(100, round((used / limit) * 100))
    
    return {
        "plan": plan,
        "usage": usage,
        "limits": {
            "analyses": {
                "used": usage['analyses_count'],
                "limit": plan['analyses_per_month'],
                "percentage": calc_percentage(usage['analyses_count'], plan['analyses_per_month']),
                "unlimited": plan['analyses_per_month'] == -1
            },
            "copilot": {
                "used": usage['copilot_queries'],
                "limit": plan['copilot_queries_per_month'],
                "percentage": calc_percentage(usage['copilot_queries'], plan['copilot_queries_per_month']),
                "unlimited": plan['copilot_queries_per_month'] == -1
            },
            "exports": {
                "used": usage['exports_count'],
                "limit": 100,  # Default
                "percentage": calc_percentage(usage['exports_count'], 100),
                "unlimited": False
            }
        }
    }

def check_limit(user_email: str, event_type: str) -> Dict:
    """Prüft ob User sein Limit erreicht hat"""
    data = get_usage_with_limits(user_email)
    
    if event_type == "analysis":
        limit_info = data['limits']['analyses']
    elif event_type == "copilot_query":
        limit_info = data['limits']['copilot']
    else:
        return {"allowed": True, "limit_info": None}
    
    if limit_info['unlimited']:
        return {"allowed": True, "limit_info": limit_info}
    
    if limit_info['used'] >= limit_info['limit']:
        return {
            "allowed": False,
            "limit_info": limit_info,
            "message": f"Monatliches Limit erreicht ({limit_info['used']}/{limit_info['limit']}). Upgrade für mehr.",
            "upgrade_url": "/billing"
        }
    
    # Warnung bei 80%
    warning = None
    if limit_info['percentage'] >= 80:
        remaining = limit_info['limit'] - limit_info['used']
        warning = f"Noch {remaining} von {limit_info['limit']} übrig diesen Monat."
    
    return {"allowed": True, "limit_info": limit_info, "warning": warning}

def get_usage_history(user_email: str, months: int = 6) -> list:
    """Holt Usage-Historie der letzten X Monate"""
    conn = get_db()
    
    rows = conn.execute("""
        SELECT * FROM usage_monthly 
        WHERE user_email = ? 
        ORDER BY month DESC 
        LIMIT ?
    """, (user_email, months)).fetchall()
    
    conn.close()
    
    return [dict(row) for row in rows]

# Initialisierung
init_usage_tables()
