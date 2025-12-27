"""
2FA/TOTP Authentication Module
- QR Code Generation
- TOTP Verification
- Backup Codes
"""

import pyotp
import qrcode
import io
import base64
import secrets
import sqlite3
import hashlib
from typing import Dict, Optional, List
from datetime import datetime

DB_PATH = "/var/www/contract-app/data/contracts.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_2fa_tables():
    """Erstellt 2FA-Tabellen"""
    conn = get_db()
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_2fa (
            user_email TEXT PRIMARY KEY,
            totp_secret TEXT,
            is_enabled INTEGER DEFAULT 0,
            enabled_at TIMESTAMP,
            backup_codes TEXT,
            last_used_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS totp_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            success INTEGER,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def generate_totp_secret(user_email: str) -> Dict:
    """Generiert neuen TOTP Secret und QR Code"""
    conn = get_db()
    
    # Generiere Secret
    secret = pyotp.random_base32()
    
    # Speichere (noch nicht aktiviert)
    conn.execute("""
        INSERT INTO user_2fa (user_email, totp_secret, is_enabled)
        VALUES (?, ?, 0)
        ON CONFLICT(user_email) DO UPDATE SET
            totp_secret = excluded.totp_secret,
            is_enabled = 0
    """, (user_email, secret))
    conn.commit()
    conn.close()
    
    # Generiere QR Code
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user_email,
        issuer_name="SBS Vertragsanalyse"
    )
    
    # QR Code als Base64
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "secret": secret,
        "qr_code": f"data:image/png;base64,{qr_base64}",
        "provisioning_uri": provisioning_uri
    }

def verify_totp(user_email: str, code: str, ip_address: str = None) -> Dict:
    """Verifiziert TOTP Code"""
    conn = get_db()
    
    row = conn.execute(
        "SELECT totp_secret, is_enabled, backup_codes FROM user_2fa WHERE user_email = ?",
        (user_email,)
    ).fetchone()
    
    if not row:
        log_attempt(user_email, False, ip_address)
        return {"success": False, "error": "2FA nicht eingerichtet"}
    
    secret = row['totp_secret']
    totp = pyotp.TOTP(secret)
    
    # Pruefe TOTP Code (mit 30 Sekunden Toleranz)
    if totp.verify(code, valid_window=1):
        log_attempt(user_email, True, ip_address)
        conn.execute(
            "UPDATE user_2fa SET last_used_at = CURRENT_TIMESTAMP WHERE user_email = ?",
            (user_email,)
        )
        conn.commit()
        conn.close()
        return {"success": True}
    
    # Pruefe Backup Codes
    backup_codes = row['backup_codes']
    if backup_codes:
        codes = backup_codes.split(',')
        code_hash = hashlib.sha256(code.encode()).hexdigest()[:16]
        if code_hash in codes:
            # Entferne verwendeten Backup Code
            codes.remove(code_hash)
            conn.execute(
                "UPDATE user_2fa SET backup_codes = ?, last_used_at = CURRENT_TIMESTAMP WHERE user_email = ?",
                (','.join(codes), user_email)
            )
            conn.commit()
            conn.close()
            log_attempt(user_email, True, ip_address)
            return {"success": True, "backup_code_used": True, "remaining_codes": len(codes)}
    
    conn.close()
    log_attempt(user_email, False, ip_address)
    return {"success": False, "error": "Ungültiger Code"}

def enable_2fa(user_email: str, code: str) -> Dict:
    """Aktiviert 2FA nach Verifikation"""
    conn = get_db()
    
    row = conn.execute(
        "SELECT totp_secret FROM user_2fa WHERE user_email = ?",
        (user_email,)
    ).fetchone()
    
    if not row:
        return {"success": False, "error": "2FA Setup nicht gestartet"}
    
    secret = row['totp_secret']
    totp = pyotp.TOTP(secret)
    
    if not totp.verify(code, valid_window=1):
        return {"success": False, "error": "Ungültiger Code"}
    
    # Generiere Backup Codes
    backup_codes = generate_backup_codes()
    backup_hashes = [hashlib.sha256(c.encode()).hexdigest()[:16] for c in backup_codes]
    
    conn.execute("""
        UPDATE user_2fa 
        SET is_enabled = 1, enabled_at = CURRENT_TIMESTAMP, backup_codes = ?
        WHERE user_email = ?
    """, (','.join(backup_hashes), user_email))
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "backup_codes": backup_codes,
        "message": "2FA erfolgreich aktiviert"
    }

def disable_2fa(user_email: str, code: str) -> Dict:
    """Deaktiviert 2FA"""
    verify = verify_totp(user_email, code)
    if not verify["success"]:
        return verify
    
    conn = get_db()
    conn.execute("""
        UPDATE user_2fa 
        SET is_enabled = 0, totp_secret = NULL, backup_codes = NULL
        WHERE user_email = ?
    """, (user_email,))
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "2FA deaktiviert"}

def is_2fa_enabled(user_email: str) -> bool:
    """Prueft ob 2FA aktiviert ist"""
    conn = get_db()
    row = conn.execute(
        "SELECT is_enabled FROM user_2fa WHERE user_email = ?",
        (user_email,)
    ).fetchone()
    conn.close()
    return bool(row and row['is_enabled'])

def get_2fa_status(user_email: str) -> Dict:
    """Holt 2FA Status"""
    conn = get_db()
    row = conn.execute(
        "SELECT is_enabled, enabled_at, last_used_at, backup_codes FROM user_2fa WHERE user_email = ?",
        (user_email,)
    ).fetchone()
    conn.close()
    
    if not row:
        return {"enabled": False, "setup_started": False}
    
    backup_count = len(row['backup_codes'].split(',')) if row['backup_codes'] else 0
    
    return {
        "enabled": bool(row['is_enabled']),
        "setup_started": True,
        "enabled_at": row['enabled_at'],
        "last_used_at": row['last_used_at'],
        "backup_codes_remaining": backup_count
    }

def generate_backup_codes(count: int = 8) -> List[str]:
    """Generiert Backup Codes"""
    codes = []
    for _ in range(count):
        code = secrets.token_hex(4).upper()
        codes.append(f"{code[:4]}-{code[4:]}")
    return codes

def regenerate_backup_codes(user_email: str, code: str) -> Dict:
    """Generiert neü Backup Codes"""
    verify = verify_totp(user_email, code)
    if not verify["success"]:
        return verify
    
    backup_codes = generate_backup_codes()
    backup_hashes = [hashlib.sha256(c.encode()).hexdigest()[:16] for c in backup_codes]
    
    conn = get_db()
    conn.execute(
        "UPDATE user_2fa SET backup_codes = ? WHERE user_email = ?",
        (','.join(backup_hashes), user_email)
    )
    conn.commit()
    conn.close()
    
    return {"success": True, "backup_codes": backup_codes}

def log_attempt(user_email: str, success: bool, ip_address: str = None):
    """Loggt 2FA Versuch"""
    conn = get_db()
    conn.execute("""
        INSERT INTO totp_attempts (user_email, success, ip_address)
        VALUES (?, ?, ?)
    """, (user_email, 1 if success else 0, ip_address))
    conn.commit()
    conn.close()

def get_recent_attempts(user_email: str, limit: int = 10) -> List[Dict]:
    """Holt letzte Login-Versuche"""
    conn = get_db()
    rows = conn.execute("""
        SELECT success, ip_address, created_at 
        FROM totp_attempts 
        WHERE user_email = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_email, limit)).fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

# Init tables
init_2fa_tables()
print("2FA Module geladen")
