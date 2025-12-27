"""
Fristen-Alerts System
- Prüft täglich ablaufende Verträge
- Sendet E-Mail-Benachrichtigungen
- Zeigt Alerts im Dashboard
"""

import sqlite3
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict
import os

DB_PATH = "/var/www/contract-app/data/contracts.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_alerts_table():
    """Erstellt die Alerts-Tabelle"""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS deadline_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            alert_date DATE NOT NULL,
            deadline_date DATE NOT NULL,
            days_until INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            sent_at TIMESTAMP,
            user_email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(contract_id, alert_type, alert_date)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alert_settings (
            user_email TEXT PRIMARY KEY,
            alert_30_days BOOLEAN DEFAULT 1,
            alert_14_days BOOLEAN DEFAULT 1,
            alert_7_days BOOLEAN DEFAULT 1,
            alert_1_day BOOLEAN DEFAULT 1,
            email_enabled BOOLEAN DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Alerts-Tabellen initialisiert")

def get_upcoming_deadlines(days_ahead: int = 30) -> List[Dict]:
    """Findet alle Verträge mit Fristen in den nächsten X Tagen"""
    conn = get_db()
    
    contracts = conn.execute("""
        SELECT c.contract_id, c.filename, c.contract_type, ar.analysis_json
        FROM contracts c
        JOIN analysis_results ar ON c.contract_id = ar.contract_id
        WHERE c.status = 'analyzed'
    """).fetchall()
    
    conn.close()
    
    upcoming = []
    today = datetime.now().date()
    cutoff = today + timedelta(days=days_ahead)
    
    for contract in contracts:
        try:
            analysis = json.loads(contract['analysis_json'])
            extracted = analysis.get('extracted_data', {})
            
            # Vertragsenddatum
            end_date_str = extracted.get('contract_end_date')
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                days_until = (end_date - today).days
                
                if 0 <= days_until <= days_ahead:
                    # Kündigungsfrist berechnen
                    notice_days = int(extracted.get('renewal_notice_days', 30) or 30)
                    notice_deadline = end_date - timedelta(days=notice_days)
                    notice_days_until = (notice_deadline - today).days
                    
                    upcoming.append({
                        'contract_id': contract['contract_id'],
                        'filename': contract['filename'],
                        'contract_type': contract['contract_type'],
                        'end_date': end_date_str,
                        'days_until_end': days_until,
                        'notice_deadline': notice_deadline.isoformat(),
                        'days_until_notice': notice_days_until,
                        'auto_renew': extracted.get('auto_renew', False),
                        'vendor': extracted.get('vendor_name', 'Unbekannt'),
                        'value': extracted.get('annual_contract_value_eur', 0)
                    })
        except Exception as e:
            print(f"Error processing {contract['contract_id']}: {e}")
    
    # Sortiere nach Dringlichkeit
    upcoming.sort(key=lambda x: x['days_until_end'])
    return upcoming

def create_alerts_for_contract(contract: Dict) -> List[Dict]:
    """Erstellt Alert-Einträge für einen Vertrag"""
    alerts = []
    today = datetime.now().date()
    
    # Alert-Schwellen in Tagen
    thresholds = [30, 14, 7, 1]
    
    for days in thresholds:
        if contract['days_until_end'] <= days:
            alerts.append({
                'contract_id': contract['contract_id'],
                'alert_type': f'{days}_days',
                'alert_date': today.isoformat(),
                'deadline_date': contract['end_date'],
                'days_until': contract['days_until_end']
            })
    
    # Kündigungsfrist-Alert
    if contract['days_until_notice'] <= 7 and contract['days_until_notice'] >= 0:
        alerts.append({
            'contract_id': contract['contract_id'],
            'alert_type': 'notice_deadline',
            'alert_date': today.isoformat(),
            'deadline_date': contract['notice_deadline'],
            'days_until': contract['days_until_notice']
        })
    
    return alerts

def save_alert(alert: Dict, user_email: str = None):
    """Speichert einen Alert in der DB"""
    conn = get_db()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO deadline_alerts 
            (contract_id, alert_type, alert_date, deadline_date, days_until, user_email)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            alert['contract_id'],
            alert['alert_type'],
            alert['alert_date'],
            alert['deadline_date'],
            alert['days_until'],
            user_email
        ))
        conn.commit()
    except Exception as e:
        print(f"Error saving alert: {e}")
    finally:
        conn.close()

def get_pending_alerts(user_email: str = None) -> List[Dict]:
    """Holt alle ausstehenden Alerts"""
    conn = get_db()
    
    query = """
        SELECT da.*, c.filename, c.contract_type
        FROM deadline_alerts da
        JOIN contracts c ON da.contract_id = c.contract_id
        WHERE da.status = 'pending'
    """
    if user_email:
        query += " AND da.user_email = ?"
        alerts = conn.execute(query, (user_email,)).fetchall()
    else:
        alerts = conn.execute(query).fetchall()
    
    conn.close()
    return [dict(a) for a in alerts]

def send_alert_email(to_email: str, alerts: List[Dict]) -> bool:
    """Sendet E-Mail mit Fristen-Alerts"""
    if not alerts:
        return False
    
    # Gmail Konfiguration (aus Invoice-App)
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USER = os.getenv("GMAIL_USER", "info@sbsdeutschland.com")
    SMTP_PASS = os.getenv("GMAIL_APP_PASSWORD", "")
    
    if not SMTP_PASS:
        print("⚠️ Gmail nicht konfiguriert")
        return False
    
    # E-Mail erstellen
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"⚠️ {len(alerts)} Vertragsfristen erfordern Ihre Aufmerksamkeit"
    msg['From'] = f"SBS Vertragsmanagement <{SMTP_USER}>"
    msg['To'] = to_email
    
    # HTML Content
    alert_rows = ""
    for a in alerts:
        urgency_color = "#ef4444" if a['days_until'] <= 7 else "#f59e0b" if a['days_until'] <= 14 else "#3b82f6"
        alert_rows += f"""
        <tr>
            <td style="padding:12px;border-bottom:1px solid #e5e7eb;">{a.get('filename', 'Unbekannt')}</td>
            <td style="padding:12px;border-bottom:1px solid #e5e7eb;">{a['deadline_date']}</td>
            <td style="padding:12px;border-bottom:1px solid #e5e7eb;">
                <span style="background:{urgency_color};color:white;padding:4px 12px;border-radius:20px;font-size:13px;">
                    {a['days_until']} Tage
                </span>
            </td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f4f7fa;padding:40px 20px;">
        <div style="max-width:600px;margin:0 auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
            <div style="background:linear-gradient(135deg,#003856,#004d73);color:white;padding:32px;text-align:center;">
                <h1 style="margin:0;font-size:24px;">⚠️ Vertragsfristen-Warnung</h1>
                <p style="margin:12px 0 0;opacity:0.9;">SBS Vertragsmanagement</p>
            </div>
            <div style="padding:32px;">
                <p style="color:#374151;font-size:16px;line-height:1.6;">
                    Die folgenden Verträge erfordern Ihre Aufmerksamkeit:
                </p>
                <table style="width:100%;border-collapse:collapse;margin:24px 0;">
                    <thead>
                        <tr style="background:#f8fafc;">
                            <th style="padding:12px;text-align:left;border-bottom:2px solid #e5e7eb;">Vertrag</th>
                            <th style="padding:12px;text-align:left;border-bottom:2px solid #e5e7eb;">Frist</th>
                            <th style="padding:12px;text-align:left;border-bottom:2px solid #e5e7eb;">Verbleibend</th>
                        </tr>
                    </thead>
                    <tbody>
                        {alert_rows}
                    </tbody>
                </table>
                <div style="text-align:center;margin-top:32px;">
                    <a href="https://contract.sbsdeutschland.com/history" 
                       style="display:inline-block;background:#003856;color:white;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:600;">
                        Verträge prüfen →
                    </a>
                </div>
            </div>
            <div style="background:#f8fafc;padding:20px;text-align:center;color:#6b7280;font-size:13px;">
                SBS Deutschland GmbH & Co. KG · Weinheim<br>
                <a href="https://contract.sbsdeutschland.com/settings" style="color:#003856;">Alert-Einstellungen ändern</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html, 'html'))
    
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"✅ Alert-Email gesendet an {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email-Fehler: {e}")
        return False

def mark_alerts_sent(alert_ids: List[int]):
    """Markiert Alerts als gesendet"""
    conn = get_db()
    for aid in alert_ids:
        conn.execute("""
            UPDATE deadline_alerts 
            SET status = 'sent', sent_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (aid,))
    conn.commit()
    conn.close()

def run_daily_check():
    """Führt die tägliche Fristen-Prüfung aus"""
    print(f"\n{'='*50}")
    print(f"🕐 Fristen-Check: {datetime.now().isoformat()}")
    print(f"{'='*50}")
    
    # Tabellen initialisieren
    init_alerts_table()
    
    # Kommende Fristen finden
    upcoming = get_upcoming_deadlines(days_ahead=30)
    print(f"\n📋 {len(upcoming)} Verträge mit Fristen in den nächsten 30 Tagen")
    
    if not upcoming:
        print("✅ Keine dringenden Fristen")
        return
    
    # Alerts erstellen
    all_alerts = []
    for contract in upcoming:
        alerts = create_alerts_for_contract(contract)
        for alert in alerts:
            save_alert(alert, "luis220195@gmail.com")  # Admin-Email
            all_alerts.append({**alert, 'filename': contract['filename']})
    
    print(f"⚠️ {len(all_alerts)} Alerts erstellt")
    
    # E-Mail senden (wenn aktiviert)
    if all_alerts:
        critical = [a for a in all_alerts if a['days_until'] <= 7]
        if critical:
            send_alert_email("luis220195@gmail.com", critical)
    
    print(f"\n{'='*50}\n")

if __name__ == "__main__":
    run_daily_check()
