"""Fristen-Übersicht Seite"""

from .pages_enterprise import PAGE_CSS, get_header, get_footer
from .deadline_alerts import get_upcoming_deadlines, init_alerts_table

def get_deadlines_page(user_name: str = "User"):
    """Generiert die Fristen-Übersicht Seite"""
    
    init_alerts_table()
    deadlines = get_upcoming_deadlines(days_ahead=90)
    
    header = get_header(user_name, "deadlines")
    footer = get_footer()
    
    # Stats berechnen
    critical = len([d for d in deadlines if d['days_until_end'] <= 7])
    warning = len([d for d in deadlines if 7 < d['days_until_end'] <= 30])
    upcoming = len([d for d in deadlines if d['days_until_end'] > 30])
    
    # Deadline Rows generieren
    deadline_rows = ""
    for d in deadlines:
        if d['days_until_end'] <= 7:
            urgency_class = "critical"
            urgency_badge = '<span class="badge badge-danger">Kritisch</span>'
        elif d['days_until_end'] <= 14:
            urgency_class = "high"
            urgency_badge = '<span class="badge badge-warning">Dringend</span>'
        elif d['days_until_end'] <= 30:
            urgency_class = "medium"
            urgency_badge = '<span class="badge badge-info">Bald</span>'
        else:
            urgency_class = "low"
            urgency_badge = '<span class="badge badge-muted">Geplant</span>'
        
        auto_renew = "✅ Ja" if d.get('auto_renew') else "❌ Nein"
        value = f"€{d.get('value', 0):,.0f}" if d.get('value') else "-"
        
        deadline_rows += f'''
        <tr class="deadline-row {urgency_class}">
            <td>
                <div class="contract-name">
                    <strong>{d['filename']}</strong>
                    <small>{d.get('vendor', 'Unbekannt')}</small>
                </div>
            </td>
            <td><span class="badge badge-muted">{d['contract_type']}</span></td>
            <td>{d['end_date']}</td>
            <td>
                <span class="days-badge {urgency_class}">{d['days_until_end']} Tage</span>
            </td>
            <td>{d.get('notice_deadline', '-')}</td>
            <td>{auto_renew}</td>
            <td>{value}</td>
            <td>{urgency_badge}</td>
            <td>
                <a href="/copilot?contract={d['contract_id']}" class="btn btn-secondary" style="padding:6px 12px;font-size:0.8rem;">🤖 Fragen</a>
            </td>
        </tr>
        '''
    
    if not deadline_rows:
        deadline_rows = '''
        <tr>
            <td colspan="9" style="text-align:center;padding:60px;color:#64748b;">
                <div style="font-size:48px;margin-bottom:16px;">🎉</div>
                <strong>Keine Fristen in den nächsten 90 Tagen</strong>
                <p style="margin-top:8px;">Alle Verträge sind im grünen Bereich.</p>
            </td>
        </tr>
        '''
    
    page_css = '''
    .deadline-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 32px; }
    @media (max-width: 768px) { .deadline-stats { grid-template-columns: repeat(2, 1fr); } }
    .deadline-stat { background: white; border-radius: 16px; padding: 24px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
    .deadline-stat.critical { border-left: 4px solid #ef4444; }
    .deadline-stat.warning { border-left: 4px solid #f59e0b; }
    .deadline-stat.upcoming { border-left: 4px solid #3b82f6; }
    .deadline-stat.total { border-left: 4px solid #003856; }
    .deadline-stat-value { font-size: 2.5rem; font-weight: 700; color: #1e293b; }
    .deadline-stat.critical .deadline-stat-value { color: #ef4444; }
    .deadline-stat.warning .deadline-stat-value { color: #f59e0b; }
    .deadline-stat.upcoming .deadline-stat-value { color: #3b82f6; }
    .deadline-stat-label { color: #64748b; margin-top: 4px; }
    
    .deadlines-table { width: 100%; border-collapse: collapse; }
    .deadlines-table th { background: #f8fafc; padding: 14px 16px; text-align: left; font-weight: 600; color: #475569; border-bottom: 2px solid #e2e8f0; }
    .deadlines-table td { padding: 16px; border-bottom: 1px solid #e2e8f0; }
    .deadline-row:hover { background: #f8fafc; }
    .deadline-row.critical { background: rgba(239,68,68,0.05); }
    .deadline-row.critical:hover { background: rgba(239,68,68,0.1); }
    
    .contract-name { display: flex; flex-direction: column; gap: 2px; }
    .contract-name strong { color: #1e293b; }
    .contract-name small { color: #64748b; font-size: 0.8rem; }
    
    .days-badge { padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
    .days-badge.critical { background: #fef2f2; color: #dc2626; }
    .days-badge.high { background: #fffbeb; color: #d97706; }
    .days-badge.medium { background: #eff6ff; color: #2563eb; }
    .days-badge.low { background: #f0fdf4; color: #16a34a; }
    
    .alert-banner { background: linear-gradient(135deg, #fef2f2, #fee2e2); border: 1px solid #fecaca; border-radius: 12px; padding: 20px 24px; margin-bottom: 24px; display: flex; align-items: center; gap: 16px; }
    .alert-banner-icon { font-size: 32px; }
    .alert-banner-content h4 { margin: 0 0 4px; color: #991b1b; }
    .alert-banner-content p { margin: 0; color: #b91c1c; font-size: 0.9rem; }
    '''
    
    # Alert Banner wenn kritische Fristen
    alert_banner = ""
    if critical > 0:
        alert_banner = f'''
        <div class="alert-banner">
            <div class="alert-banner-icon">🚨</div>
            <div class="alert-banner-content">
                <h4>{critical} Vertrag{"" if critical == 1 else "e"} mit kritischer Frist!</h4>
                <p>Diese Verträge laufen in weniger als 7 Tagen ab und erfordern sofortige Aufmerksamkeit.</p>
            </div>
        </div>
        '''
    
    html = '''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>Fristen-Übersicht · SBS Vertragsanalyse</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link rel="icon" href="/static/favicon.ico">
''' + PAGE_CSS + '''
<style>
''' + page_css + '''
</style>
</head>
<body>
''' + header + '''
<div class="hero" style="padding:32px 24px;">
  <div class="container">
    <div class="hero-badge"><span class="dot" style="background:#f59e0b;box-shadow:0 0 12px rgba(245,158,11,0.6);"></span> FRISTEN-MANAGEMENT</div>
    <h1 style="font-size:2rem;margin:12px 0 8px;">⏰ Vertragsfristen</h1>
    <p style="opacity:0.9;">Übersicht aller kommenden Vertragsfristen und Kündigungstermine.</p>
  </div>
</div>

<div class="page-container">
  ''' + alert_banner + '''
  
  <div class="deadline-stats">
    <div class="deadline-stat critical">
      <div class="deadline-stat-value">''' + str(critical) + '''</div>
      <div class="deadline-stat-label">Kritisch (&lt;7 Tage)</div>
    </div>
    <div class="deadline-stat warning">
      <div class="deadline-stat-value">''' + str(warning) + '''</div>
      <div class="deadline-stat-label">Dringend (7-30 Tage)</div>
    </div>
    <div class="deadline-stat upcoming">
      <div class="deadline-stat-value">''' + str(upcoming) + '''</div>
      <div class="deadline-stat-label">Geplant (&gt;30 Tage)</div>
    </div>
    <div class="deadline-stat total">
      <div class="deadline-stat-value">''' + str(len(deadlines)) + '''</div>
      <div class="deadline-stat-label">Gesamt (90 Tage)</div>
    </div>
  </div>
  
  <div class="content-card">
    <div class="content-card-header">
      <h3 class="content-card-title">📋 Kommende Fristen</h3>
      <button class="btn btn-primary" onclick="location.href='/copilot'">🤖 Mit Copilot analysieren</button>
    </div>
    <div class="content-card-body" style="padding:0;overflow-x:auto;">
      <table class="deadlines-table">
        <thead>
          <tr>
            <th>Vertrag</th>
            <th>Typ</th>
            <th>Enddatum</th>
            <th>Verbleibend</th>
            <th>Kündigungsfrist</th>
            <th>Auto-Verlängerung</th>
            <th>Wert</th>
            <th>Status</th>
            <th>Aktion</th>
          </tr>
        </thead>
        <tbody>
          ''' + deadline_rows + '''
        </tbody>
      </table>
    </div>
  </div>
</div>

''' + footer + '''
</body>
</html>'''
    
    return html
