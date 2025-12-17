"""
SQLite Persistenz für Contract-App (mit datetime-Fix)
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, date
from decimal import Decimal
import logging
import time

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "contracts.db"
DB_PATH.parent.mkdir(exist_ok=True)

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON Encoder für datetime/date/Decimal"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def safe_json_dumps(data):
    """JSON dumps mit datetime-Support"""
    return json.dumps(data, cls=DateTimeEncoder)

def get_connection():
    """Erstellt DB-Verbindung mit erhöhtem Timeout"""
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_database():
    """Initialisiert die Datenbank"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contracts (
            contract_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            contract_type TEXT,
            file_path TEXT,
            uploaded_at TEXT NOT NULL,
            analyzed BOOLEAN DEFAULT 0,
            extracted_data TEXT,
            risk_assessment TEXT,
            analysis_result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")

def save_contract(contract_id: str, data: Dict, retries: int = 3) -> None:
    """Speichert einen Contract mit Retry-Logik"""
    for attempt in range(retries):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO contracts 
                (contract_id, filename, contract_type, file_path, uploaded_at, analyzed, 
                 extracted_data, risk_assessment, analysis_result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contract_id,
                data.get("filename"),
                data.get("contract_type"),
                data.get("file_path"),
                data.get("uploaded_at") or data.get("created_at"),
                1 if data.get("analyzed") else 0,
                safe_json_dumps(data.get("extracted_data")) if data.get("extracted_data") else None,
                safe_json_dumps(data.get("risk_assessment")) if data.get("risk_assessment") else None,
                safe_json_dumps(data.get("analysis_result")) if data.get("analysis_result") else None,
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"💾 Contract saved: {contract_id}")
            return
            
        except sqlite3.OperationalError as e:
            if "locked" in str(e) and attempt < retries - 1:
                time.sleep(0.5 * (attempt + 1))
                continue
            else:
                logger.error(f"❌ DB Error: {e}")
                raise
        except Exception as e:
            logger.error(f"❌ Unexpected error in save_contract: {e}")
            raise

def load_contract(contract_id: str) -> Optional[Dict]:
    """Lädt einen Contract"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM contracts WHERE contract_id = ?", (contract_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    data = dict(row)
    
    # JSON-Felder deserialisieren
    if data.get("extracted_data"):
        data["extracted_data"] = json.loads(data["extracted_data"])
    if data.get("risk_assessment"):
        data["risk_assessment"] = json.loads(data["risk_assessment"])
    if data.get("analysis_result"):
        data["analysis_result"] = json.loads(data["analysis_result"])
    
    data["analyzed"] = bool(data.get("analyzed"))
    
    return data

def load_all_contracts() -> Dict[str, Dict]:
    """Lädt alle Contracts in ein Dict"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT contract_id FROM contracts")
    rows = cursor.fetchall()
    conn.close()
    
    contracts = {}
    for row in rows:
        contract_id = row["contract_id"]
        contract = load_contract(contract_id)
        if contract:
            contracts[contract_id] = contract
    
    logger.info(f"📚 Loaded {len(contracts)} contracts from database")
    return contracts

def delete_contract(contract_id: str) -> bool:
    """Löscht einen Contract"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM contracts WHERE contract_id = ?", (contract_id,))
    success = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return success
