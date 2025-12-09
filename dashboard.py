#!/usr/bin/env python3
"""
CFO Dashboard für Contract Analyzer
Zeigt KPIs, Kosten, Risiken und Tenant-Nutzung an.
Endpoint: GET /dashboard
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# ============================================================================
# DASHBOARD LOGIK
# ============================================================================

class DashboardService:
    """Service für CFO-Dashboard-Daten."""
    
    def __init__(self, db_path: str = "analysis.sqlite"):
        self.db_path = Path(db_path)
    
    def get_db_connection(self):
        """Gibt SQLite-Connection zurück."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_overview_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Gibt Übersichts-KPIs zurück."""
        with self.get_db_connection() as conn:
            rows = conn.execute(f"""
            SELECT 
                COUNT(*) as total_analyses,
                SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status='error' THEN 1 ELSE 0 END) as failed,
                AVG(duration_ms) as avg_duration_ms,
                SUM(COALESCE(llm_input_tokens, 0) + COALESCE(llm_output_tokens, 0)) as total_tokens,
                SUM(CASE WHEN contract_type='employment' THEN 1 ELSE 0 END) as employment_count,
                SUM(CASE WHEN contract_type='saas' THEN 1 ELSE 0 END) as saas_count
            FROM analysis_log
            WHERE datetime(created_at) > datetime('now', '-{days} days')
            """).fetchall()
            
            row = rows[0]
            total = row[0] or 0
            successful = row[1] or 0
            failed = row[2] or 0
            avg_duration = round(row[3] or 0, 1)
            total_tokens = row[4] or 0
            employment = row[5] or 0
            saas = row[6] or 0
            
            # Kosten-Schätzung (OpenAI GPT-4 mini: $0.0015 pro 1K Tokens)
            estimated_cost_usd = (total_tokens / 1000) * 0.0015
            
            return {
                "period_days": days,
                "total_analyses": total,
                "successful": successful,
                "failed": failed,
                "error_rate": round((failed / total * 100), 2) if total > 0 else 0,
                "avg_duration_ms": avg_duration,
                "total_tokens": total_tokens,
                "estimated_cost_usd": round(estimated_cost_usd, 2),
                "cost_per_analysis": round(estimated_cost_usd / total, 4) if total > 0 else 0,
                "contract_type_distribution": {
                    "employment": employment,
                    "saas": saas
                }
            }
    
    def get_risk_distribution(self, days: int = 30) -> Dict[str, Any]:
        """Gibt Risiko-Verteilung zurück."""
        with self.get_db_connection() as conn:
            # Durchschnittliche Risiken pro Analyse
            avg_row = conn.execute(f"""
            SELECT AVG(num_risk_flags) as avg_risks, MAX(num_risk_flags) as max_risks
            FROM analysis_log
            WHERE status='success' AND datetime(created_at) > datetime('now', '-{days} days')
            """).fetchone()
            
            # Verteilung nach Schweregrad (safe fallback)
            try:
                severity_rows = conn.execute(f"""
                SELECT severity, COUNT(*) as count
                FROM analysis_log, json_each(risk_flags)
                WHERE datetime(created_at) > datetime('now', '-{days} days')
                  AND risk_flags IS NOT NULL AND risk_flags != ''
                GROUP BY severity
                """).fetchall()
            except Exception:
                severity_rows = []
            
            severity_dist = {row[0]: row[1] for row in severity_rows}
            
            # Top-Risiken (häufigste Titel) - safe fallback
            try:
                top_risks = conn.execute(f"""
                SELECT json_extract(value, '$.title') as title, 
                       json_extract(value, '$.severity') as severity, 
                       COUNT(*) as count
                FROM analysis_log, json_each(risk_flags)
                WHERE datetime(created_at) > datetime('now', '-{days} days')
                  AND risk_flags IS NOT NULL AND risk_flags != ''
                GROUP BY title, severity
                ORDER BY count DESC
                LIMIT 10
                """).fetchall()
            except Exception:
                top_risks = []
            
            return {
                "avg_risk_flags_per_contract": round(avg_row[0] or 0, 2),
                "max_risk_flags": avg_row[1] or 0,
                "severity_distribution": severity_dist,
                "top_risks": [
                    {"title": row[0], "severity": row[1], "count": row[2]}
                    for row in top_risks
                ]
            }
    
    def get_tenant_metrics(self) -> List[Dict[str, Any]]:
        """Gibt Metriken pro Tenant zurück."""
        with self.get_db_connection() as conn:
            rows = conn.execute("""
            SELECT 
                tenant_id,
                analyses_monthly_limit,
                analyses_this_month,
                tokens_this_month,
                last_analysis_at
            FROM tenant_usage
            ORDER BY analyses_this_month DESC
            """).fetchall()
            
            return [
                {
                    "tenant_id": row[0],
                    "monthly_limit": row[1],
                    "analyses_this_month": row[2],
                    "tokens_this_month": row[3],
                    "last_analysis_at": row[4],
                    "usage_percent": round((row[2] / row[1] * 100), 2) if row[1] > 0 else 0
                }
                for row in rows
            ]
    
    def get_daily_trend(self, days: int = 14) -> List[Dict[str, Any]]:
        """Gibt Analysen pro Tag zurück."""
        with self.get_db_connection() as conn:
            rows = conn.execute(f"""
            SELECT DATE(created_at) as day, 
                   COUNT(*) as total,
                   SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as successful
            FROM analysis_log
            WHERE datetime(created_at) > datetime('now', '-{days} days')
            GROUP BY DATE(created_at)
            ORDER BY day ASC
            """).fetchall()
            
            return [
                {
                    "day": row[0],
                    "total": row[1],
                    "successful": row[2],
                    "error_rate": round(((row[1] - row[2]) / row[1] * 100), 2) if row[1] > 0 else 0
                }
                for row in rows
            ]

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="CFO Dashboard API",
    version="1.0.0",
    description="Dashboard für Contract Analyzer KPIs und Cost Tracking"
)

# Mounten des Dashboards unter /dashboard
dashboard_service = DashboardService()

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    """Zeigt das CFO-Dashboard als HTML-Seite."""
    try:
        metrics = dashboard_service.get_overview_metrics()
        risks = dashboard_service.get_risk_distribution()
        tenants = dashboard_service.get_tenant_metrics()
        trend = dashboard_service.get_daily_trend()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard-Fehler: {e}")
    
    # HTML Template
    html = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Contract Analyzer - CFO Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   background: #f5f7fa; color: #2c3e50; line-height: 1.6; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; padding: 2rem; text-align: center; }}
            .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                     gap: 1.5rem; margin-bottom: 2rem; }}
            .card {{ background: white; border-radius: 10px; padding: 1.5rem; 
                     box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid #667eea; }}
            .card h2 {{ color: #667eea; margin-bottom: 1rem; font-size: 1.2rem; }}
            .metric {{ display: flex; justify-content: space-between; padding: 0.5rem 0; 
                       border-bottom: 1px solid #eee; }}
            .metric:last-child {{ border-bottom: none; }}
            .metric-value {{ font-weight: bold; color: #2c3e50; }}
            .metric-value.warning {{ color: #e74c3c; }}
            .metric-value.success {{ color: #27ae60; }}
            .chart {{ height: 200px; display: flex; align-items: flex-end; gap: 5px; }}
            .bar {{ flex: 1; background: #667eea; border-radius: 3px 3px 0 0; 
                    min-height: 5px; transition: all 0.3s; }}
            .bar:hover {{ background: #764ba2; }}
            .trend-table {{ width: 100%; border-collapse: collapse; }}
            .trend-table th, .trend-table td {{ padding: 0.75rem; text-align: left; 
                                                border-bottom: 1px solid #eee; }}
            .trend-table th {{ background: #f8f9fa; color: #667eea; font-weight: 600; }}
            .risk-high {{ color: #e74c3c; }}
            .risk-medium {{ color: #f39c12; }}
            .risk-low {{ color: #95a5a6; }}
            .footer {{ text-align: center; padding: 2rem; color: #7f8c8d; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Contract Analyzer – CFO Dashboard</h1>
            <p>Zeitraum: Letzte {metrics["period_days"]} Tage</p>
        </div>
        
        <div class="container">
            
            <!-- KPI Karten -->
            <div class="grid">
                <div class="card">
                    <h2>📊 Analyse-Volumen</h2>
                    <div class="metric">
                        <span>Gesamte Analysen:</span>
                        <span class="metric-value">{metrics["total_analyses"]}</span>
                    </div>
                    <div class="metric">
                        <span>Erfolgreich:</span>
                        <span class="metric-value success">{metrics["successful"]}</span>
                    </div>
                    <div class="metric">
                        <span>Fehlgeschlagen:</span>
                        <span class="metric-value warning">{metrics["failed"]}</span>
                    </div>
                    <div class="metric">
                        <span>Fehlerrate:</span>
                        <span class="metric-value warning">{metrics["error_rate"]}%</span>
                    </div>
                </div>
                
                <div class="card">
                    <h2>💰 Kosten & Performance</h2>
                    <div class="metric">
                        <span>Geschätzte Kosten (USD):</span>
                        <span class="metric-value">${metrics["estimated_cost_usd"]}</span>
                    </div>
                    <div class="metric">
                        <span>Kosten pro Analyse:</span>
                        <span class="metric-value">${metrics["cost_per_analysis"]}</span>
                    </div>
                    <div class="metric">
                        <span>Durchschn. Dauer:</span>
                        <span class="metric-value">{metrics["avg_duration_ms"]}ms</span>
                    </div>
                    <div class="metric">
                        <span>Tokens gesamt:</span>
                        <span class="metric-value">{metrics["total_tokens"]:,}</span>
                    </div>
                </div>
                
                <div class="card">
                    <h2>📈 Vertragstypen</h2>
                    <div class="metric">
                        <span>Arbeitsverträge:</span>
                        <span class="metric-value">{metrics["contract_type_distribution"]["employment"]}</span>
                    </div>
                    <div class="metric">
                        <span>SaaS-Verträge:</span>
                        <span class="metric-value">{metrics["contract_type_distribution"]["saas"]}</span>
                    </div>
                </div>
            </div>
            
            <!-- Risiken -->
            <div class="card">
                <h2>🚨 Risiko-Analyse</h2>
                <div class="metric">
                    <span>Durchschn. Risiken pro Vertrag:</span>
                    <span class="metric-value">{risks["avg_risk_flags_per_contract"]}</span>
                </div>
                <div class="metric">
                    <span>Max. Risiken (einzelner Vertrag):</span>
                    <span class="metric-value warning">{risks["max_risk_flags"]}</span>
                </div>
                <div class="grid" style="margin-top: 1rem;">
                    <div>
                        <h3 style="color: #e74c3c;">High Risk</h3>
                        <p style="font-size: 1.5rem; font-weight: bold;">
                            {risks["severity_distribution"].get("high", 0)}
                        </p>
                    </div>
                    <div>
                        <h3 style="color: #f39c12;">Medium Risk</h3>
                        <p style="font-size: 1.5rem; font-weight: bold;">
                            {risks["severity_distribution"].get("medium", 0)}
                        </p>
                    </div>
                    <div>
                        <h3 style="color: #95a5a6;">Low Risk</h3>
                        <p style="font-size: 1.5rem; font-weight: bold;">
                            {risks["severity_distribution"].get("low", 0)}
                        </p>
                    </div>
                </div>
                <h3 style="margin-top: 1.5rem; margin-bottom: 0.5rem;">Top-Risiken:</h3>
                <ul style="padding-left: 1.5rem;">
    """
    
    for risk in risks["top_risks"]:
        html += f"""
                    <li class="risk-{risk['severity']}">
                        <strong>{risk['title']}</strong> ({risk['severity']}) - {risk['count']}x
                    </li>
        """
    
    html += """
                </ul>
            </div>
            
            <!-- Tenant-Nutzung -->
            <div class="card">
                <h2>👥 Tenant-Nutzung</h2>
                <table class="trend-table">
                    <thead>
                        <tr>
                            <th>Tenant</th>
                            <th>Monatliches Limit</th>
                            <th>Analysen</th>
                            <th>Verbrauch</th>
                            <th>Zuletzt aktiv</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for tenant in tenants:
        usage_class = ""
        if tenant["usage_percent"] > 90:
            usage_class = "risk-high"
        elif tenant["usage_percent"] > 70:
            usage_class = "risk-medium"
        
        html += f"""
                        <tr>
                            <td>{tenant["tenant_id"]}</td>
                            <td>{tenant["monthly_limit"]}</td>
                            <td>{tenant["analyses_this_month"]}</td>
                            <td class="{usage_class}">{tenant["usage_percent"]}%</td>
                            <td>{tenant["last_analysis_at"] or "Nie"}</td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
            
            <!-- Trenderlauf -->
            <div class="card">
                <h2>📅 Trenderlauf (Letzte 14 Tage)</h2>
                <table class="trend-table">
                    <thead>
                        <tr>
                            <th>Datum</th>
                            <th>Analysen</th>
                            <th>Erfolgreich</th>
                            <th>Fehlerrate</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for day in trend:
        html += f"""
                        <tr>
                            <td>{day["day"]}</td>
                            <td>{day["total"]}</td>
                            <td>{day["successful"]}</td>
                            <td class="{'risk-high' if day['error_rate'] > 10 else 'risk-medium' if day['error_rate'] > 5 else ''}">
                                {day["error_rate"]}%
                            </td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
            
            <div class="footer">
                <p>Contract Analyzer CFO Dashboard | Letzte Aktualisierung: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            </div>
            
        </div>
    </body>
    </html>
    """
    
    return html


# ============================================================================
# MAIN APP (falls direkt ausgeführt)
# ============================================================================

if __name__ == "__main__":
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard():
        return get_dashboard()
    
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
