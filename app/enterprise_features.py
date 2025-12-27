"""
Enterprise SaaS Features für Contract Analyzer
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict
import secrets

DB_PATH = "/var/www/contract-app/data/contracts.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_enterprise_tables():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_email TEXT NOT NULL,
            user_name TEXT,
            action TEXT NOT NULL,
            resource_type TEXT,
            resource_id TEXT,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            success INTEGER DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'viewer',
            status TEXT DEFAULT 'active',
            invited_by TEXT,
            invited_at TEXT,
            joined_at TEXT,
            last_active TEXT,
            avatar_color TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_email TEXT PRIMARY KEY,
            notification_email INTEGER DEFAULT 1,
            notification_slack INTEGER DEFAULT 0,
            slack_webhook TEXT,
            language TEXT DEFAULT 'de',
            timezone TEXT DEFAULT 'Europe/Berlin',
            theme TEXT DEFAULT 'light',
            two_factor_enabled INTEGER DEFAULT 0,
            api_key TEXT,
            api_key_created TEXT,
            updated_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            org_id TEXT DEFAULT 'default',
            plan TEXT DEFAULT 'professional',
            status TEXT DEFAULT 'active',
            billing_cycle TEXT DEFAULT 'monthly',
            price_cents INTEGER DEFAULT 17900,
            max_users INTEGER DEFAULT 5,
            max_contracts_month INTEGER DEFAULT 100,
            current_period_start TEXT,
            current_period_end TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL,
            contracts_analyzed INTEGER DEFAULT 0,
            pages_processed INTEGER DEFAULT 0,
            exports_generated INTEGER DEFAULT 0,
            api_calls INTEGER DEFAULT 0,
            storage_mb REAL DEFAULT 0
        )
    ''')
    
    conn.commit()
    _insert_default_data(conn)
    conn.close()
    print("✅ Enterprise-Tabellen initialisiert")

def _insert_default_data(conn):
    cursor = conn.cursor()
    
    existing = cursor.execute("SELECT COUNT(*) FROM team_members").fetchone()[0]
    if existing == 0:
        cursor.execute('''
            INSERT INTO team_members (email, name, role, status, joined_at, last_active, avatar_color)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('luis@sbsdeutschland.com', 'Luis Schenk', 'admin', 'active', 
              datetime.now().isoformat(), datetime.now().isoformat(), '#003856'))
    
    existing_sub = cursor.execute("SELECT COUNT(*) FROM subscriptions").fetchone()[0]
    if existing_sub == 0:
        now = datetime.now()
        period_end = now + timedelta(days=30)
        cursor.execute('''
            INSERT INTO subscriptions (plan, status, billing_cycle, price_cents, max_users, 
                                       max_contracts_month, current_period_start, current_period_end, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('professional', 'active', 'monthly', 17900, 5, 100, 
              now.isoformat(), period_end.isoformat(), now.isoformat()))
    
    current_month = datetime.now().strftime('%Y-%m')
    existing_usage = cursor.execute("SELECT COUNT(*) FROM usage_stats WHERE month = ?", (current_month,)).fetchone()[0]
    if existing_usage == 0:
        cursor.execute('INSERT INTO usage_stats (month) VALUES (?)', (current_month,))
    
    conn.commit()

# AUDIT LOGGING
def log_audit(user_email: str, action: str, resource_type: str = None, 
              resource_id: str = None, details: str = None, 
              ip_address: str = None, user_name: str = None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO audit_logs (timestamp, user_email, user_name, action, resource_type, 
                               resource_id, details, ip_address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now().isoformat(), user_email, user_name, action, 
          resource_type, resource_id, details, ip_address))
    conn.commit()
    conn.close()

def get_audit_logs(limit: int = 50) -> List[Dict]:
    conn = get_db()
    rows = conn.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_audit_stats() -> Dict:
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    today_count = cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE timestamp LIKE ?", (f"{today}%",)).fetchone()[0]
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    week_count = cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE timestamp > ?", (week_ago,)).fetchone()[0]
    total_count = cursor.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]
    unique_users = cursor.execute("SELECT COUNT(DISTINCT user_email) FROM audit_logs WHERE timestamp LIKE ?", (f"{today}%",)).fetchone()[0]
    conn.close()
    return {"today": today_count, "this_week": week_count, "total": total_count, "unique_users_today": unique_users}

# TEAM MANAGEMENT
def get_team_members() -> List[Dict]:
    conn = get_db()
    rows = conn.execute('SELECT * FROM team_members ORDER BY role, name').fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_team_stats() -> Dict:
    conn = get_db()
    cursor = conn.cursor()
    total = cursor.execute("SELECT COUNT(*) FROM team_members").fetchone()[0]
    admins = cursor.execute("SELECT COUNT(*) FROM team_members WHERE role = 'admin'").fetchone()[0]
    sub = cursor.execute("SELECT max_users FROM subscriptions LIMIT 1").fetchone()
    max_users = sub['max_users'] if sub else 5
    conn.close()
    return {"total": total, "admins": admins, "max_users": max_users, "available": max_users - total}

def add_team_member(email: str, name: str, role: str = 'viewer', invited_by: str = None) -> Dict:
    conn = get_db()
    cursor = conn.cursor()
    existing = cursor.execute("SELECT id FROM team_members WHERE email = ?", (email,)).fetchone()
    if existing:
        conn.close()
        return {"success": False, "error": "Benutzer existiert bereits"}
    colors = ['#003856', '#FFB900', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899']
    avatar_color = colors[hash(email) % len(colors)]
    cursor.execute('''
        INSERT INTO team_members (email, name, role, status, invited_by, invited_at, avatar_color)
        VALUES (?, ?, ?, 'pending', ?, ?, ?)
    ''', (email, name, role, invited_by, datetime.now().isoformat(), avatar_color))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"{name} wurde eingeladen"}

# BILLING
def get_subscription() -> Dict:
    conn = get_db()
    sub = conn.execute("SELECT * FROM subscriptions LIMIT 1").fetchone()
    conn.close()
    return dict(sub) if sub else None

def get_current_usage() -> Dict:
    conn = get_db()
    cursor = conn.cursor()
    current_month = datetime.now().strftime('%Y-%m')
    usage = cursor.execute("SELECT * FROM usage_stats WHERE month = ?", (current_month,)).fetchone()
    sub = cursor.execute("SELECT max_contracts_month FROM subscriptions LIMIT 1").fetchone()
    max_contracts = sub['max_contracts_month'] if sub else 100
    conn.close()
    if not usage:
        return {"contracts_analyzed": 0, "pages_processed": 0, "exports_generated": 0, "api_calls": 0, "max_contracts": max_contracts, "usage_percent": 0}
    usage_dict = dict(usage)
    usage_dict['max_contracts'] = max_contracts
    usage_dict['usage_percent'] = round((usage_dict['contracts_analyzed'] / max_contracts) * 100, 1)
    return usage_dict

def increment_usage(field: str, amount: int = 1):
    conn = get_db()
    cursor = conn.cursor()
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute(f'UPDATE usage_stats SET {field} = {field} + ? WHERE month = ?', (amount, current_month))
    conn.commit()
    conn.close()

def get_billing_history() -> List[Dict]:
    return [
        {"id": "INV-2025-0012", "date": "01.12.2025", "amount": "179,00 €", "status": "paid"},
        {"id": "INV-2025-0011", "date": "01.11.2025", "amount": "179,00 €", "status": "paid"},
        {"id": "INV-2025-0010", "date": "01.10.2025", "amount": "179,00 €", "status": "paid"}
    ]

# SETTINGS
def get_user_settings(email: str) -> Dict:
    conn = get_db()
    settings = conn.execute("SELECT * FROM user_settings WHERE user_email = ?", (email,)).fetchone()
    conn.close()
    if not settings:
        return {"user_email": email, "notification_email": True, "notification_slack": False, "api_key": None}
    return dict(settings)

def update_user_settings(email: str, **kwargs) -> Dict:
    conn = get_db()
    cursor = conn.cursor()
    existing = cursor.execute("SELECT user_email FROM user_settings WHERE user_email = ?", (email,)).fetchone()
    if not existing:
        cursor.execute("INSERT INTO user_settings (user_email, updated_at) VALUES (?, ?)", (email, datetime.now().isoformat()))
    for key, value in kwargs.items():
        if key in ['notification_email', 'notification_slack', 'language', 'timezone', 'theme', 'two_factor_enabled']:
            cursor.execute(f'UPDATE user_settings SET {key} = ?, updated_at = ? WHERE user_email = ?', (value, datetime.now().isoformat(), email))
    conn.commit()
    conn.close()
    return {"success": True}

def generate_api_key(email: str) -> str:
    conn = get_db()
    cursor = conn.cursor()
    api_key = f"sbs_contract_{secrets.token_hex(24)}"
    existing = cursor.execute("SELECT user_email FROM user_settings WHERE user_email = ?", (email,)).fetchone()
    if not existing:
        cursor.execute('INSERT INTO user_settings (user_email, api_key, api_key_created, updated_at) VALUES (?, ?, ?, ?)',
                       (email, api_key, datetime.now().isoformat(), datetime.now().isoformat()))
    else:
        cursor.execute('UPDATE user_settings SET api_key = ?, api_key_created = ?, updated_at = ? WHERE user_email = ?',
                       (api_key, datetime.now().isoformat(), datetime.now().isoformat(), email))
    conn.commit()
    conn.close()
    return api_key

init_enterprise_tables()

def revoke_api_key(email: str) -> dict:
    """Widerruft den API-Key eines Users."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE user_settings SET api_key = NULL, api_key_created = NULL, updated_at = ? WHERE user_email = ?',
                   (datetime.now().isoformat(), email))
    conn.commit()
    conn.close()
    return {"success": True}

def remove_team_member(email: str) -> Dict:
    """Entfernt ein Team-Mitglied."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM team_members WHERE email = ?', (email,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    if affected > 0:
        return {"success": True}
    return {"success": False, "error": "Mitglied nicht gefunden"}
