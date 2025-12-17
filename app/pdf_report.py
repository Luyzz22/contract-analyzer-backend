"""SBS Contract Intelligence - PDF Report Generator"""

from datetime import datetime

def generate_report_html(data: dict) -> str:
    """Generiert HTML für PDF Report"""
    ra = data.get("risk_assessment", {})
    ed = data.get("extracted_data", {})
    level = ra.get("overall_risk_level", "low")
    score = ra.get("overall_risk_score", 0)
    
    level_colors = {"critical": "#dc2626", "high": "#ea580c", "medium": "#d97706", "low": "#16a34a", "minimal": "#16a34a"}
    level_labels = {"critical": "KRITISCH", "high": "HOCH", "medium": "MITTEL", "low": "NIEDRIG", "minimal": "MINIMAL"}
    
    def fmt_date(d):
        if not d: return "-"
        try: return datetime.fromisoformat(d.replace("Z","")).strftime("%d.%m.%Y")
        except: return d
    
    def fmt_curr(a):
        if not a: return "-"
        return f"{float(a):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    
    risks_html = ""
    all_risks = (ra.get("critical_risks", []) + ra.get("high_risks", []) + 
                 ra.get("medium_risks", []) + ra.get("low_risks", []))
    
    for r in all_risks:
        risks_html += f'''
        <div class="risk-item {r.get('risk_level', 'low')}">
            <div class="risk-header">
                <strong>{r.get('issue_title', '')}</strong>
                <span class="severity">{r.get('risk_level', '').upper()}</span>
            </div>
            <p>{r.get('issue_description', '')}</p>
            {f'<div class="clause">"{r.get("clause_text", "")}"</div>' if r.get('clause_text') else ''}
            <div class="legal">📖 {r.get('legal_basis', '')}</div>
            {f'<div class="recommendation"><strong>Empfehlung:</strong> {r.get("recommendation", "")}</div>' if r.get('recommendation') else ''}
        </div>
        '''
    
    if not risks_html:
        risks_html = '<div class="no-risks">✅ Keine kritischen Risiken identifiziert</div>'
    
    emp = ed.get("employer", {}) or {}
    ee = ed.get("employee", {}) or {}
    comp = ed.get("compensation", {}) or {}
    wc = ed.get("working_conditions", {}) or {}
    vac = ed.get("vacation", {}) or {}
    prob = ed.get("probation", {}) or {}
    term = ed.get("termination", {}) or {}
    nc = ed.get("non_compete", {}) or {}
    conf = ed.get("confidentiality", {}) or {}
    
    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@page {{ size: A4; margin: 2cm; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 11pt; line-height: 1.5; color: #1e293b; }}
.header {{ background: linear-gradient(135deg, #003856, #00507a); color: white; padding: 24px; margin: -2cm -2cm 24px -2cm; }}
.header h1 {{ margin: 0 0 4px 0; font-size: 20pt; }}
.header .subtitle {{ opacity: 0.8; font-size: 10pt; }}
.meta {{ display: flex; justify-content: space-between; margin-bottom: 24px; padding: 16px; background: #f8fafc; border-radius: 8px; }}
.meta-item {{ text-align: center; }}
.meta-label {{ font-size: 9pt; color: #64748b; text-transform: uppercase; }}
.meta-value {{ font-size: 14pt; font-weight: 600; color: #003856; }}
.risk-score {{ background: {level_colors.get(level, '#16a34a')}; color: white; padding: 16px 24px; border-radius: 8px; text-align: center; margin-bottom: 24px; }}
.risk-score .label {{ font-size: 10pt; opacity: 0.9; }}
.risk-score .value {{ font-size: 24pt; font-weight: 700; }}
.risk-score .level {{ font-size: 12pt; font-weight: 600; }}
.section {{ margin-bottom: 24px; }}
.section h2 {{ font-size: 12pt; color: #003856; border-bottom: 2px solid #003856; padding-bottom: 8px; margin-bottom: 16px; }}
.summary {{ background: #f0f9ff; border-left: 4px solid #003856; padding: 16px; margin-bottom: 24px; }}
.data-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
.data-box {{ background: #fafafa; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; }}
.data-box h3 {{ font-size: 9pt; text-transform: uppercase; color: #003856; margin: 0 0 12px 0; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0; }}
.data-row {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f1f5f9; }}
.data-row:last-child {{ border-bottom: none; }}
.data-label {{ color: #64748b; font-size: 10pt; }}
.data-value {{ font-weight: 500; text-align: right; }}
.risk-item {{ padding: 16px; margin-bottom: 12px; border-radius: 8px; border-left: 4px solid; page-break-inside: avoid; }}
.risk-item.critical {{ background: #fef2f2; border-color: #dc2626; }}
.risk-item.high {{ background: #fff7ed; border-color: #ea580c; }}
.risk-item.medium {{ background: #fffbeb; border-color: #d97706; }}
.risk-item.low {{ background: #f0fdf4; border-color: #16a34a; }}
.risk-header {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
.severity {{ font-size: 8pt; padding: 2px 8px; border-radius: 4px; background: rgba(0,0,0,0.1); }}
.clause {{ font-style: italic; background: rgba(0,0,0,0.03); padding: 8px 12px; border-radius: 4px; margin: 8px 0; font-size: 10pt; }}
.legal {{ font-size: 9pt; color: #003856; margin-top: 8px; }}
.recommendation {{ margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(0,0,0,0.1); font-size: 10pt; }}
.no-risks {{ text-align: center; padding: 32px; background: #f0fdf4; border-radius: 8px; color: #16a34a; font-weight: 500; }}
.footer {{ margin-top: 32px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 9pt; color: #64748b; text-align: center; }}
</style>
</head>
<body>
<div class="header">
    <h1>📋 Vertragsanalyse Report</h1>
    <div class="subtitle">SBS Contract Intelligence · Erstellt am {datetime.now().strftime("%d.%m.%Y um %H:%M Uhr")}</div>
</div>

<div class="meta">
    <div class="meta-item"><div class="meta-label">Datei</div><div class="meta-value">{data.get('source_filename', '-')}</div></div>
    <div class="meta-item"><div class="meta-label">Vertragstyp</div><div class="meta-value">{data.get('contract_type', '-').upper()}</div></div>
    <div class="meta-item"><div class="meta-label">Felder</div><div class="meta-value">{data.get('fields_extracted', 0)}/{data.get('fields_total', 42)}</div></div>
    <div class="meta-item"><div class="meta-label">Analysezeit</div><div class="meta-value">{data.get('processing_time_seconds', 0)}s</div></div>
</div>

<div class="risk-score">
    <div class="label">GESAMT-RISIKOBEWERTUNG</div>
    <div class="value">{score}/100</div>
    <div class="level">{level_labels.get(level, 'NIEDRIG')}</div>
</div>

{f'<div class="summary"><strong>Executive Summary:</strong> {ra.get("executive_summary", "")}</div>' if ra.get("executive_summary") else ''}

<div class="section">
    <h2>Vertragsdaten</h2>
    <div class="data-grid">
        <div class="data-box">
            <h3>Arbeitgeber</h3>
            <div class="data-row"><span class="data-label">Name</span><span class="data-value">{emp.get('name', '-')}</span></div>
            <div class="data-row"><span class="data-label">Adresse</span><span class="data-value">{emp.get('address', '-')}</span></div>
            <div class="data-row"><span class="data-label">Vertreter</span><span class="data-value">{emp.get('contact_person', '-')}</span></div>
        </div>
        <div class="data-box">
            <h3>Arbeitnehmer</h3>
            <div class="data-row"><span class="data-label">Name</span><span class="data-value">{ee.get('name', '-')}</span></div>
            <div class="data-row"><span class="data-label">Adresse</span><span class="data-value">{ee.get('address', '-')}</span></div>
        </div>
        <div class="data-box">
            <h3>Vertrag</h3>
            <div class="data-row"><span class="data-label">Position</span><span class="data-value">{ed.get('job_title', '-')}</span></div>
            <div class="data-row"><span class="data-label">Beginn</span><span class="data-value">{fmt_date(ed.get('start_date'))}</span></div>
            <div class="data-row"><span class="data-label">Befristung</span><span class="data-value">{'bis ' + fmt_date(term.get('end_date')) if term.get('fixed_term') else 'Unbefristet'}</span></div>
        </div>
        <div class="data-box">
            <h3>Vergütung</h3>
            <div class="data-row"><span class="data-label">Bruttogehalt</span><span class="data-value">{fmt_curr(comp.get('base_salary_gross'))}</span></div>
            <div class="data-row"><span class="data-label">Bonus</span><span class="data-value">{fmt_curr(comp.get('bonus_target')) if comp.get('bonus_target') else '-'}</span></div>
        </div>
        <div class="data-box">
            <h3>Arbeitszeit</h3>
            <div class="data-row"><span class="data-label">Wochenstunden</span><span class="data-value">{wc.get('weekly_hours', '-')}h</span></div>
            <div class="data-row"><span class="data-label">Überstunden</span><span class="data-value">{'Pauschal abgegolten' if wc.get('overtime_included_in_salary') else 'Gesondert vergütet'}</span></div>
        </div>
        <div class="data-box">
            <h3>Urlaub & Probezeit</h3>
            <div class="data-row"><span class="data-label">Urlaubstage</span><span class="data-value">{vac.get('days_per_year', '-')} Tage/Jahr</span></div>
            <div class="data-row"><span class="data-label">Probezeit</span><span class="data-value">{prob.get('duration_months', '-')} Monate</span></div>
        </div>
    </div>
</div>

<div class="section">
    <h2>Risikobewertung</h2>
    {risks_html}
</div>

<div class="footer">
    <p>Dieser Report wurde automatisch erstellt von SBS Contract Intelligence.</p>
    <p>Die Analyse ersetzt keine rechtliche Beratung. Bei Fragen wenden Sie sich an einen Fachanwalt.</p>
    <p>© {datetime.now().year} SBS Deutschland · www.sbsdeutschland.com</p>
</div>
</body>
</html>'''
