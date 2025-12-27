from .enterprise_features import get_audit_logs, get_audit_stats, log_audit, get_team_members, get_team_stats, add_team_member, get_subscription, get_current_usage, get_billing_history, get_user_settings, update_user_settings, generate_api_key
# app/pages_enterprise.py
"""
Enterprise SaaS Seiten für Contract Intelligence
Mit exakt gleichem Header/Footer wie Upload-Page
"""

from datetime import datetime


# =============================================================================
# SHARED STYLES (identisch mit frontend.py)
# =============================================================================

PAGE_CSS = '''
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");

:root {
  --sbs-blue: #003856;
  --sbs-blue-dark: #002a42;
  --sbs-blue-light: #00507a;
  --sbs-yellow: #FFB900;
  --sbs-bg: #f4f7fa;
  --sbs-text: #111827;
  --sbs-muted: #6b7280;
  --sbs-border: #e5e7eb;
  --sbs-card: #ffffff;
  --sbs-success: #10b981;
  --sbs-warning: #f59e0b;
  --sbs-danger: #ef4444;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: "Inter", system-ui, -apple-system, sans-serif;
  background: var(--sbs-bg);
  color: var(--sbs-text);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

header {
  background: #fff;
  border-bottom: 1px solid var(--sbs-border);
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 72px;
}

.header-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.header-logo img { height: 40px; width: auto; }

.header-logo-text { display: flex; flex-direction: column; line-height: 1.3; }
.header-logo-text .brand { font-size: 15px; font-weight: 600; color: var(--sbs-blue); }
.header-logo-text .subtitle { font-size: 12px; color: var(--sbs-muted); }

.header-nav { display: flex; align-items: center; gap: 8px; }

.header-nav a {
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--sbs-text);
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.header-nav a:hover { background: rgba(0,56,86,0.05); color: var(--sbs-blue); }
.header-nav a.active { color: var(--sbs-blue); background: rgba(0,56,86,0.08); }

/* Home Button */
.home-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  color: var(--sbs-blue);
  background: rgba(0,56,86,0.08);
  margin-right: 12px;
  transition: all 0.2s;
}
.home-btn:hover { background: rgba(0,56,86,0.15); transform: scale(1.05); }

/* App Switcher */
.app-switcher-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}
.app-switcher-btn:hover { background: rgba(0,56,86,0.08); color: var(--sbs-blue); }

.app-switcher-menu { width: 320px; }

.app-item {
  display: flex !important;
  align-items: center;
  gap: 12px;
  padding: 12px 16px !important;
}
.app-item:hover { background: rgba(0,56,86,0.05); }
.app-item.active-app { background: rgba(255,185,0,0.1); border-left: 3px solid var(--sbs-yellow); }

.app-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: white;
  flex-shrink: 0;
}

.app-info { display: flex; flex-direction: column; }
.app-info strong { font-size: 14px; color: #1e293b; }
.app-info small { font-size: 12px; color: #64748b; }

.dropdown { position: relative; }

.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--sbs-text);
  background: none;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.dropdown-toggle:hover { background: rgba(0,56,86,0.05); color: var(--sbs-blue); }
.dropdown-toggle svg { width: 16px; height: 16px; transition: transform 0.2s ease; }
.dropdown:hover .dropdown-toggle svg { transform: rotate(180deg); }

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  min-width: 220px;
  background: #fff;
  border: 1px solid var(--sbs-border);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.12);
  padding: 8px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(8px);
  transition: all 0.2s ease;
  z-index: 1001;
}

.dropdown:hover .dropdown-menu { opacity: 1; visibility: visible; transform: translateY(0); }

.dropdown-section { padding: 4px 0; }
.dropdown-section:not(:last-child) { border-bottom: 1px solid var(--sbs-border); margin-bottom: 4px; padding-bottom: 8px; }
.dropdown-label { font-size: 11px; font-weight: 600; color: var(--sbs-muted); text-transform: uppercase; letter-spacing: 0.05em; padding: 8px 12px 4px; }

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  font-size: 14px;
  color: var(--sbs-text);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.15s ease;
}

.dropdown-item:hover { background: rgba(0,56,86,0.05); color: var(--sbs-blue); }
.dropdown-item .icon { font-size: 16px; width: 20px; text-align: center; }
.dropdown-item.cross-link { color: var(--sbs-yellow); font-weight: 500; }
.dropdown-item.cross-link:hover { background: rgba(255,185,0,0.1); }

.user-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px 6px 6px;
  background: rgba(0,56,86,0.05);
  border: none;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.user-btn:hover { background: rgba(0,56,86,0.1); }

.user-avatar {
  width: 32px;
  height: 32px;
  background: var(--sbs-blue);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.user-name { font-size: 14px; font-weight: 500; color: var(--sbs-text); }
.user-btn svg { width: 16px; height: 16px; color: var(--sbs-muted); }

main { flex: 1; }

.hero {
  background: linear-gradient(135deg, var(--sbs-blue) 0%, var(--sbs-blue-dark) 100%);
  color: #fff;
  padding: 48px 24px;
}

.hero .container { max-width: 1400px; margin: 0 auto; }
.hero-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 999px; font-size: 13px; font-weight: 500; margin-bottom: 20px; }
.hero-badge .dot { width: 8px; height: 8px; background: var(--sbs-yellow); border-radius: 50%; }
.hero h1 { font-size: 2.25rem; font-weight: 700; margin-bottom: 12px; color: #fff; }
.hero p { font-size: 1.1rem; opacity: 0.9; max-width: 600px; }

.page-container { max-width: 1200px; margin: 0 auto; padding: 40px 24px; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 32px; }
@media (max-width: 768px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }

.stat-card { background: #fff; border-radius: 12px; padding: 24px; border: 1px solid var(--sbs-border); box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.stat-value { font-size: 2rem; font-weight: 700; color: var(--sbs-blue); margin-bottom: 4px; }
.stat-label { font-size: 0.85rem; color: var(--sbs-muted); }

.content-card { background: #fff; border-radius: 16px; border: 1px solid var(--sbs-border); box-shadow: 0 4px 24px rgba(0,0,0,0.06); margin-bottom: 24px; }
.content-card-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid var(--sbs-border); }
.content-card-title { font-size: 1.1rem; font-weight: 600; color: var(--sbs-blue); }
.content-card-body { padding: 24px; }

.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 14px 16px; text-align: left; border-bottom: 1px solid var(--sbs-border); }
.data-table th { font-size: 0.75rem; font-weight: 600; color: var(--sbs-muted); text-transform: uppercase; letter-spacing: 0.05em; background: #fafbfc; }
.data-table tr:hover { background: rgba(0,56,86,0.02); }

.badge { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
.badge-success { background: rgba(16,185,129,0.1); color: #059669; }
.badge-warning { background: rgba(245,158,11,0.1); color: #d97706; }
.badge-danger { background: rgba(239,68,68,0.1); color: #dc2626; }
.badge-info { background: rgba(0,56,86,0.1); color: var(--sbs-blue); }

.form-group { margin-bottom: 20px; }
.form-label { display: block; font-size: 0.9rem; font-weight: 500; color: var(--sbs-text); margin-bottom: 8px; }
.form-input { width: 100%; padding: 12px 16px; font-size: 0.95rem; border: 1px solid var(--sbs-border); border-radius: 8px; transition: all 0.2s; }
.form-input:focus { outline: none; border-color: var(--sbs-blue); box-shadow: 0 0 0 3px rgba(0,56,86,0.1); }
.form-hint { font-size: 0.8rem; color: var(--sbs-muted); margin-top: 6px; }

.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
@media (max-width: 768px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } }

.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 12px 24px; font-size: 14px; font-weight: 600; border: none; border-radius: 8px; cursor: pointer; transition: all 0.2s; text-decoration: none; }
.btn-primary { background: var(--sbs-yellow); color: var(--sbs-blue); }
.btn-primary:hover { background: var(--sbs-blue); color: #fff; }
.btn-secondary { background: #f3f4f6; color: var(--sbs-text); border: 1px solid var(--sbs-border); }
.btn-secondary:hover { background: #e5e7eb; }
.btn-danger { background: #dc2626; color: #fff; }
.btn-danger:hover { background: #b91c1c; }

.empty-state { text-align: center; padding: 60px 20px; color: var(--sbs-muted); }
.empty-icon { font-size: 4rem; margin-bottom: 16px; opacity: 0.5; }

.plan-card { background: #fff; border: 2px solid var(--sbs-border); border-radius: 16px; padding: 32px; text-align: center; transition: all 0.2s; }
.plan-card:hover { border-color: var(--sbs-blue); }
.plan-card.current { border-color: var(--sbs-yellow); background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); }
.plan-price { font-size: 2.5rem; font-weight: 700; color: var(--sbs-blue); }
.plan-features { list-style: none; text-align: left; margin: 24px 0; }
.plan-features li { padding: 10px 0; border-bottom: 1px solid var(--sbs-border); font-size: 0.9rem; }

.user-row { display: flex; align-items: center; gap: 16px; }
.user-avatar-large { width: 48px; height: 48px; background: var(--sbs-blue); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 600; }
.user-info { flex: 1; }
.user-info strong { display: block; margin-bottom: 2px; }
.user-info small { color: var(--sbs-muted); }

footer { background: var(--sbs-blue-dark); color: #fff; margin-top: auto; }
.footer-container { max-width: 1400px; margin: 0 auto; padding: 64px 24px 32px; }
.footer-grid { display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr; gap: 48px; margin-bottom: 48px; }
@media (max-width: 768px) { .footer-grid { grid-template-columns: 1fr 1fr; gap: 32px; } }
.footer-brand { display: flex; flex-direction: column; gap: 16px; }
.footer-logo { display: flex; align-items: center; gap: 12px; }
.footer-logo img { height: 36px; width: auto; filter: brightness(0) invert(1); }
.footer-logo-text .name { font-size: 16px; font-weight: 600; color: #fff; }
.footer-logo-text .sub { font-size: 13px; color: rgba(255,255,255,0.7); }
.footer-tagline { font-size: 14px; color: rgba(255,255,255,0.7); line-height: 1.6; }
.footer-address { display: flex; align-items: center; gap: 8px; font-size: 14px; color: rgba(255,255,255,0.6); }
.footer-section h4 { font-size: 14px; font-weight: 600; color: var(--sbs-yellow); margin-bottom: 20px; text-transform: uppercase; letter-spacing: 0.03em; }
.footer-section ul { list-style: none; }
.footer-section li { margin-bottom: 12px; }
.footer-section a { font-size: 14px; color: rgba(255,255,255,0.8); text-decoration: none; transition: color 0.15s; }
.footer-section a:hover { color: #fff; }
.footer-bottom { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 24px; text-align: center; font-size: 14px; color: rgba(255,255,255,0.5); }
</style>
'''


def get_header(user_name: str = "User", active: str = ""):
    """Enterprise Header mit Home-Button und App-Switcher."""
    user_initial = user_name[0].upper() if user_name else "U"
    
    return f'''
<header>
  <div class="header-container">
    <!-- Home Button -->
    <a href="https://app.sbsdeutschland.com/dashboard" class="home-btn" title="Dashboard">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
        <polyline points="9 22 9 12 15 12 15 22"></polyline>
      </svg>
    </a>
    
    <!-- Logo -->
    <a href="/" class="header-logo">
      <img src="/static/sbs-logo-new.png" alt="SBS Logo">
      <div class="header-logo-text">
        <span class="brand">SBS Deutschland</span>
        <span class="subtitle">Smart Business Service · Weinheim</span>
      </div>
    </a>
    
    <nav class="header-nav">
      <a href="/upload" class="{"active" if active == "analyse" else ""}">Analyse</a>
      <a href="/history" class="{"active" if active == "verlauf" else ""}">Verlauf</a>
      <a href="/analytics" class="{"active" if active == "analytics" else ""}">Analytics</a>
      
      <div class="dropdown">
        <button class="dropdown-toggle">
          Tools
          <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
        </button>
        <div class="dropdown-menu">
          <div class="dropdown-section">
            <a href="/copilot" class="dropdown-item"><span class="icon">🤖</span> Contract Copilot</a>
            <a href="/deadlines" class="dropdown-item"><span class="icon">⏰</span> Fristen-Übersicht</a>
            <a href="/compare" class="dropdown-item"><span class="icon">⚖️</span> Vertragsvergleich</a>
            <a href="/library" class="dropdown-item"><span class="icon">📚</span> Klausel-Bibliothek</a>
            <a href="/exports" class="dropdown-item"><span class="icon">📥</span> Export-Historie</a>
          </div>
        </div>
      </div>
      
      <!-- App Switcher (Waffle) -->
      <div class="dropdown">
        <button class="app-switcher-btn" title="Apps wechseln">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="5" cy="5" r="2.5"/>
            <circle cx="12" cy="5" r="2.5"/>
            <circle cx="19" cy="5" r="2.5"/>
            <circle cx="5" cy="12" r="2.5"/>
            <circle cx="12" cy="12" r="2.5"/>
            <circle cx="19" cy="12" r="2.5"/>
            <circle cx="5" cy="19" r="2.5"/>
            <circle cx="12" cy="19" r="2.5"/>
            <circle cx="19" cy="19" r="2.5"/>
          </svg>
        </button>
        <div class="dropdown-menu app-switcher-menu">
          <div class="dropdown-section">
            <div class="dropdown-label">SBS Plattform</div>
            <a href="https://app.sbsdeutschland.com/dashboard" class="dropdown-item app-item">
              <span class="app-icon" style="background:linear-gradient(135deg,#003856,#004d73);">🏠</span>
              <div class="app-info">
                <strong>Dashboard</strong>
                <small>Übersicht & Kennzahlen</small>
              </div>
            </a>
          </div>
          <div class="dropdown-section">
            <div class="dropdown-label">Produkte</div>
            <a href="https://app.sbsdeutschland.com" class="dropdown-item app-item">
              <span class="app-icon" style="background:linear-gradient(135deg,#22c55e,#16a34a);">📄</span>
              <div class="app-info">
                <strong>KI-Rechnungen</strong>
                <small>Rechnungsverarbeitung</small>
              </div>
            </a>
            <a href="https://contract.sbsdeutschland.com" class="dropdown-item app-item active-app">
              <span class="app-icon" style="background:linear-gradient(135deg,#f59e0b,#d97706);">📋</span>
              <div class="app-info">
                <strong>KI-Verträge</strong>
                <small>Vertragsanalyse</small>
              </div>
            </a>
          </div>
        </div>
      </div>
      
      <!-- User Menu -->
      <div class="dropdown">
        <button class="user-btn">
          <div class="user-avatar">{user_initial}</div>
          <span class="user-name">{user_name}</span>
          <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
        </button>
        <div class="dropdown-menu">
          <div class="dropdown-section">
            <div class="dropdown-label">Workspace</div>
            <a href="/upload" class="dropdown-item"><span class="icon">🔍</span> Analyse</a>
            <a href="/history" class="dropdown-item"><span class="icon">📊</span> Verlauf</a>
            <a href="/analytics" class="dropdown-item"><span class="icon">📈</span> Analytics</a>
            <a href="/exports" class="dropdown-item"><span class="icon">📥</span> Export-Historie</a>
          </div>
          <div class="dropdown-section">
            <div class="dropdown-label">Konto</div>
            <a href="/settings" class="dropdown-item"><span class="icon">⚙️</span> Einstellungen</a>
            <a href="/billing" class="dropdown-item"><span class="icon">💳</span> Abrechnung</a>
            <a href="/team" class="dropdown-item"><span class="icon">👥</span> Team</a>
            <a href="/audit" class="dropdown-item"><span class="icon">📋</span> Audit-Log</a>
            <div style="border-top:1px solid #e2e8f0;margin:8px 0;"></div>
            <a href="/logout" class="dropdown-item" style="color:#dc2626;"><span class="icon">🚪</span> Abmelden</a>
          </div>
        </div>
      </div>
    </nav>
  </div>
</header>
'''


def get_footer():
    """Footer exakt wie in der Upload-Page."""
    return '''
<footer>
  <div class="footer-container">
    <div class="footer-grid">
      <div class="footer-brand">
        <div class="footer-logo">
          <img src="/static/sbs-logo-new.png" alt="SBS Logo" onerror="this.style.display='none'">
          <div class="footer-logo-text">
            <span class="name">SBS Deutschland</span>
            <span class="sub">Smart Business Service</span>
          </div>
        </div>
        <p class="footer-tagline">Enterprise KI-Vertragsanalyse.<br>Entwickelt und betrieben in Deutschland.</p>
        <div class="footer-address">📍 In der Dell 19, 69469 Weinheim</div>
      </div>
      
      <div class="footer-section">
        <h4>App</h4>
        <ul>
          <li><a href="/upload">Analyse</a></li>
          <li><a href="/history">Verlauf</a></li>
          <li><a href="/analytics">Analytics</a></li>
          <li><a href="/compare">Vergleich</a></li>
          <li><a href="/library">Bibliothek</a></li>
        </ul>
      </div>
      
      <div class="footer-section">
        <h4>Konto</h4>
        <ul>
          <li><a href="/settings">Einstellungen</a></li>
          <li><a href="/billing">Abrechnung</a></li>
          <li><a href="/team">Team</a></li>
          <li><a href="/exports">Export-Historie</a></li>
        </ul>
      </div>
      
      <div class="footer-section">
        <h4>Support</h4>
        <ul>
          <li><a href="/help">Hilfe & FAQ</a></li>
          <li><a href="mailto:info@sbsdeutschland.com">Kontakt</a></li>
          <li><a href="/impressum">Impressum</a></li>
          <li><a href="/datenschutz">Datenschutz</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">© 2025 SBS Deutschland GmbH & Co. KG</div>
  </div>
</footer>
'''


def page_wrapper(title: str, content: str, user_name: str = "User", active: str = ""):
    """Wrapper für alle Seiten."""
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | SBS Contract Intelligence</title>
  <link rel="icon" href="/static/favicon.ico">
  {PAGE_CSS}
</head>
<body>
{get_header(user_name, active)}
<main>
{content}
</main>
{get_footer()}
</body>
</html>'''


# ============================================================================
# TOOL PAGES
# ============================================================================

def get_compare_page(user_name: str = "User"):
    content = '''
<div class="hero">
  <div class="container">
    <div class="hero-badge"><span class="dot"></span> VERTRAGSVERGLEICH</div>
    <h1>⚖️ Verträge vergleichen</h1>
    <p>Vergleichen Sie zwei Verträge nebeneinander und identifizieren Sie Unterschiede.</p>
  </div>
</div>
<div class="page-container">
  <div class="grid-2">
    <div class="content-card">
      <div class="content-card-header"><h3 class="content-card-title">📄 Vertrag A</h3></div>
      <div class="content-card-body">
        <div class="empty-state" style="padding:40px;">
          <div class="empty-icon">📤</div>
          <p style="font-weight:600;margin-bottom:16px;">Vertrag auswählen</p>
          <select class="form-input" style="max-width:280px;margin:0 auto;"><option>-- Vertrag auswählen --</option></select>
        </div>
      </div>
    </div>
    <div class="content-card">
      <div class="content-card-header"><h3 class="content-card-title">📄 Vertrag B</h3></div>
      <div class="content-card-body">
        <div class="empty-state" style="padding:40px;">
          <div class="empty-icon">📤</div>
          <p style="font-weight:600;margin-bottom:16px;">Vertrag auswählen</p>
          <select class="form-input" style="max-width:280px;margin:0 auto;"><option>-- Vertrag auswählen --</option></select>
        </div>
      </div>
    </div>
  </div>
  <div style="text-align:center;margin-top:24px;"><button class="btn btn-primary" disabled style="opacity:0.5;">⚖️ Vergleich starten</button></div>
</div>'''
    return page_wrapper("Vertragsvergleich", content, user_name, "tools")


def get_library_page(user_name: str = "User"):
    clauses = [
        (1, "Kündigungsklausel Standard", "Allgemein", "success", "Niedrig", 47),
        (2, "Haftungsbegrenzung 1x ACV", "SaaS", "warning", "Mittel", 32),
        (3, "Geheimhaltung 5 Jahre", "NDA", "success", "Niedrig", 28),
        (4, "Auto-Renewal 30 Tage", "SaaS", "success", "Niedrig", 25),
        (5, "Datenlokation EU", "SaaS", "success", "Niedrig", 21),
        (6, "Eigentumsübergang", "Kaufvertrag", "success", "Niedrig", 19),
        (7, "Vertragsstrafe 10%", "Lieferant", "warning", "Mittel", 15),
        (8, "Indexmiete jährlich", "Mietvertrag", "warning", "Mittel", 12),
    ]
    rows = "".join([f'<tr><td><strong>{c[1]}</strong></td><td><span class="badge badge-info">{c[2]}</span></td><td><span class="badge badge-{c[3]}">{c[4]}</span></td><td>{c[5]}x</td><td><a href="/library/clause/{c[0]}" class="btn btn-secondary" style="padding:6px 14px;font-size:0.8rem;">Ansehen</a></td></tr>' for c in clauses])
    
    content = f'''
<div class="hero">
  <div class="container">
    <div class="hero-badge"><span class="dot"></span> KLAUSEL-BIBLIOTHEK</div>
    <h1>📚 Klausel-Bibliothek</h1>
    <p>Sammlung von Standardklauseln und Best Practices für verschiedene Vertragstypen.</p>
  </div>
</div>
<div class="page-container">
  <div class="stats-grid">
    <div class="stat-card"><div class="stat-value">48</div><div class="stat-label">Klauseln gesamt</div></div>
    <div class="stat-card"><div class="stat-value">8</div><div class="stat-label">Vertragstypen</div></div>
    <div class="stat-card"><div class="stat-value">234</div><div class="stat-label">Verwendungen</div></div>
    <div class="stat-card"><div class="stat-value">12</div><div class="stat-label">Eigene Klauseln</div></div>
  </div>
  <div class="content-card">
    <div class="content-card-header"><h3 class="content-card-title">Klauseln</h3><button class="btn btn-primary">+ Neue Klausel</button></div>
    <div class="content-card-body" style="padding:0;">
      <table class="data-table">
        <thead><tr><th>Klausel</th><th>Typ</th><th>Risiko</th><th>Nutzung</th><th>Aktion</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </div>
</div>'''
    return page_wrapper("Klausel-Bibliothek", content, user_name, "tools")


def get_exports_page(user_name: str = "User"):
    exports = [
        ("22.12.2025 14:32", "test_nda_analyse.pdf", "PDF", "danger", "124 KB"),
        ("22.12.2025 14:30", "test_nda_analyse.json", "JSON", "info", "8 KB"),
        ("18.12.2025 12:45", "saas_vertrag.pdf", "PDF", "danger", "156 KB"),
    ]
    rows = "".join([f'<tr><td>{e[0]}</td><td><strong>{e[1]}</strong></td><td><span class="badge badge-{e[3]}">{e[2]}</span></td><td>{e[4]}</td><td><button class="btn btn-secondary" style="padding:6px 14px;font-size:0.8rem;">⬇️ Download</button></td></tr>' for e in exports])
    
    content = f'''
<div class="hero">
  <div class="container">
    <div class="hero-badge"><span class="dot"></span> EXPORT-HISTORIE</div>
    <h1>📥 Export-Historie</h1>
    <p>Übersicht aller exportierten Analysen und Reports.</p>
  </div>
</div>
<div class="page-container">
  <div class="stats-grid" style="grid-template-columns:repeat(3,1fr);">
    <div class="stat-card"><div class="stat-value">127</div><div class="stat-label">Exporte gesamt</div></div>
    <div class="stat-card"><div class="stat-value">89</div><div class="stat-label">PDF Reports</div></div>
    <div class="stat-card"><div class="stat-value">38</div><div class="stat-label">JSON Exporte</div></div>
  </div>
  <div class="content-card">
    <div class="content-card-header"><h3 class="content-card-title">Letzte Exporte</h3></div>
    <div class="content-card-body" style="padding:0;">
      <table class="data-table">
        <thead><tr><th>Datum</th><th>Datei</th><th>Format</th><th>Größe</th><th>Aktion</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </div>
</div>'''
    return page_wrapper("Export-Historie", content, user_name, "tools")


# ============================================================================
# KONTO PAGES
# ============================================================================

def get_settings_page(user_name: str = "User", user_email: str = "user@sbsdeutschland.com"):
    settings = get_user_settings(user_email)
    
    api_key_html = ""
    if settings.get('api_key'):
        api_key_html = f'''<div id="apiKeyDisplay" style="background:#1e293b;border-radius:10px;padding:12px 16px;margin-top:12px;display:flex;align-items:center;gap:12px;">
          <code style="color:#22d3ee;word-break:break-all;flex:1;" id="apiKeyCode">{settings["api_key"]}</code>
          <button onclick="copyApiKey()" style="background:#334155;border:none;color:white;padding:8px 12px;border-radius:6px;cursor:pointer;" title="Kopieren">📋</button>
        </div>
        <button class="btn btn-danger" style="margin-top:12px;" onclick="revokeApiKey()">Widerrufen</button>'''
    else:
        api_key_html = '''<p style="color:var(--sbs-muted);margin-bottom:12px;">Noch kein API-Key generiert.</p>
        <button class="btn btn-primary" onclick="generateApiKey()" id="generateKeyBtn">API-Key generieren</button>
        <div id="newKeyDisplay" style="display:none;margin-top:12px;"></div>'''
    
    email_checked = 'checked' if settings.get('notification_email') else ''
    slack_checked = 'checked' if settings.get('notification_slack') else ''
    
    content = f"""
<style>
.toggle-switch {{ position: relative; display: inline-block; width: 52px; height: 28px; }}
.toggle-switch input {{ opacity: 0; width: 0; height: 0; }}
.toggle-slider {{ position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #cbd5e1; border-radius: 28px; transition: .3s; }}
.toggle-slider:before {{ position: absolute; content: ""; height: 22px; width: 22px; left: 3px; bottom: 3px; background-color: white; border-radius: 50%; transition: .3s; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
input:checked + .toggle-slider {{ background-color: #22c55e; }}
input:checked + .toggle-slider:before {{ transform: translateX(24px); }}
.toast {{ position:fixed; bottom:24px; right:24px; background:#1e293b; color:white; padding:16px 24px; border-radius:12px; display:none; z-index:2000; }}
.toast.show {{ display:block; animation: slideIn 0.3s ease; }}
@keyframes slideIn {{ from {{ transform:translateY(20px); opacity:0; }} to {{ transform:translateY(0); opacity:1; }} }}
</style>
<div class="hero">
  <div class="container">
    <div class="hero-badge"><span class="dot"></span> EINSTELLUNGEN</div>
    <h1>⚙️ Einstellungen</h1>
    <p>Verwalten Sie Ihr Konto und Ihre Präferenzen.</p>
  </div>
</div>
<div class="page-container">
  <div class="content-card">
    <div class="content-card-header"><h3 class="content-card-title">👤 Profil</h3></div>
    <div class="content-card-body">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
        <div><label style="display:block;margin-bottom:8px;font-weight:500;">Name</label><input type="text" value="{user_name}" style="width:100%;padding:12px 16px;border:1px solid #e2e8f0;border-radius:10px;font-size:0.95rem;"></div>
        <div><label style="display:block;margin-bottom:8px;font-weight:500;">E-Mail</label><input type="email" value="{user_email}" disabled style="width:100%;padding:12px 16px;border:1px solid #e2e8f0;border-radius:10px;font-size:0.95rem;background:#f8fafc;"></div>
      </div>
      <button class="btn btn-primary" style="margin-top:20px;">Speichern</button>
    </div>
  </div>
  
  <div class="content-card">
    <div class="content-card-header"><h3 class="content-card-title">🔒 Passwort ändern</h3></div>
    <div class="content-card-body">
      <form id="passwordForm" onsubmit="changePassword(event)">
        <div style="display:grid;gap:16px;max-width:400px;">
          <div><label style="display:block;margin-bottom:8px;font-weight:500;">Aktuelles Passwort</label><input type="password" id="currentPw" required style="width:100%;padding:12px 16px;border:1px solid #e2e8f0;border-radius:10px;font-size:0.95rem;"></div>
          <div><label style="display:block;margin-bottom:8px;font-weight:500;">Neues Passwort</label><input type="password" id="newPw" required minlength="8" style="width:100%;padding:12px 16px;border:1px solid #e2e8f0;border-radius:10px;font-size:0.95rem;"></div>
          <div><label style="display:block;margin-bottom:8px;font-weight:500;">Passwort bestätigen</label><input type="password" id="newPw2" required style="width:100%;padding:12px 16px;border:1px solid #e2e8f0;border-radius:10px;font-size:0.95rem;"></div>
        </div>
        <button type="submit" class="btn btn-primary" style="margin-top:20px;">Passwort ändern</button>
      </form>
    </div>
  </div>
  
  <div class="content-card">
    <div class="content-card-header"><h3 class="content-card-title">🔔 Benachrichtigungen</h3></div>
    <div class="content-card-body" style="padding:0 24px;">
      <div style="display:flex;justify-content:space-between;align-items:center;padding:16px 0;border-bottom:1px solid #e2e8f0;">
        <div><strong style="display:block;">E-Mail Benachrichtigungen</strong><small style="color:var(--sbs-muted);">Updates zu Ihren Verträgen per E-Mail</small></div>
        <label class="toggle-switch"><input type="checkbox" {email_checked} onchange="saveNotifications('email', this.checked)"><span class="toggle-slider"></span></label>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:center;padding:16px 0;">
        <div><strong style="display:block;">Slack Integration</strong><small style="color:var(--sbs-muted);">Benachrichtigungen an Slack senden</small></div>
        <label class="toggle-switch"><input type="checkbox" {slack_checked} onchange="saveNotifications('slack', this.checked)"><span class="toggle-slider"></span></label>
      </div>
    </div>
  </div>
  
  <div class="content-card">
    <div class="content-card-header"><h3 class="content-card-title">🔑 API-Zugang</h3></div>
    <div class="content-card-body">
      <p style="margin-bottom:16px;">Nutzen Sie unsere REST API für die Integration in Ihre Systeme.</p>
      {api_key_html}
    </div>
  </div>
  
  <div class="content-card" style="border-color:#fee2e2;">
    <div class="content-card-header"><h3 class="content-card-title" style="color:#dc2626;">🚪 Abmelden</h3></div>
    <div class="content-card-body">
      <p style="margin-bottom:16px;color:var(--sbs-muted);">Melden Sie sich von Ihrem Konto ab. Dies gilt für alle SBS-Anwendungen.</p>
      <a href="/logout" class="btn btn-danger">Abmelden</a>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
function showToast(msg, type) {{
  var t = document.getElementById('toast');
  t.innerHTML = (type==='success'?'✅ ':'❌ ') + msg;
  t.className = 'toast show';
  setTimeout(function(){{ t.className='toast'; }}, 3000);
}}

function copyApiKey() {{
  var code = document.getElementById('apiKeyCode');
  if (code) {{
    navigator.clipboard.writeText(code.textContent);
    showToast('API-Key kopiert!', 'success');
  }}
}}

function generateApiKey() {{
  var btn = document.getElementById('generateKeyBtn');
  btn.disabled = true;
  btn.textContent = 'Generiere...';
  
  fetch('/api/settings/generate-key', {{ method: 'POST' }})
    .then(r => r.json())
    .then(function(data) {{
      if (data.success) {{
        var display = document.getElementById('newKeyDisplay');
        display.style.display = 'block';
        display.innerHTML = '<div style="background:#1e293b;border-radius:10px;padding:12px 16px;"><code style="color:#22d3ee;word-break:break-all;">' + data.api_key + '</code></div><p style="color:#22c55e;margin-top:8px;">✅ API-Key generiert! Seite neu laden um ihn zu sehen.</p>';
        btn.style.display = 'none';
        showToast('API-Key erfolgreich generiert!', 'success');
      }} else {{
        showToast(data.error || 'Fehler beim Generieren', 'error');
        btn.disabled = false;
        btn.textContent = 'API-Key generieren';
      }}
    }});
}}

function revokeApiKey() {{
  if (!confirm('API-Key wirklich widerrufen? Alle Integrationen werden damit ungültig.')) return;
  
  fetch('/api/settings/revoke-key', {{ method: 'POST' }})
    .then(r => r.json())
    .then(function(data) {{
      if (data.success) {{
        showToast('API-Key widerrufen!', 'success');
        setTimeout(function() {{ location.reload(); }}, 1000);
      }} else {{
        showToast(data.error || 'Fehler', 'error');
      }}
    }});
}}

function saveNotifications(type, value) {{
  var fd = new FormData();
  fd.append('notification_' + type, value);
  
  fetch('/api/settings/notifications', {{ method: 'POST', body: fd }})
    .then(r => r.json())
    .then(function(data) {{
      if (data.success) {{
        showToast(type === 'email' ? 'E-Mail-Benachrichtigungen aktualisiert' : 'Slack-Integration aktualisiert', 'success');
      }}
    }});
}}

function changePassword(e) {{
  e.preventDefault();
  var cur = document.getElementById('currentPw').value;
  var newP = document.getElementById('newPw').value;
  var newP2 = document.getElementById('newPw2').value;
  
  if (newP !== newP2) {{
    showToast('Passwörter stimmen nicht überein', 'error');
    return;
  }}
  
  var fd = new FormData();
  fd.append('current_password', cur);
  fd.append('new_password', newP);
  
  fetch('/api/change-password', {{ method:'POST', body:fd }})
    .then(r => r.json())
    .then(function(data) {{
      if (data.success) {{
        showToast('Passwort erfolgreich geändert!', 'success');
        document.getElementById('passwordForm').reset();
      }} else {{
        showToast(data.error || 'Fehler', 'error');
      }}
    }});
}}
</script>"""
    return page_wrapper("Einstellungen", content, user_name, "settings")


def get_billing_page(user_name: str = "User", is_admin: bool = False, user_email: str = None):
    sub = get_subscription() or {}
    history = get_billing_history()
    
    # Echte Usage-Daten aus Tracking-System
    try:
        from .usage_tracking import get_usage_with_limits
        real_usage = get_usage_with_limits(user_email or "anonymous")
        usage = {
            "contracts_analyzed": real_usage["usage"]["analyses_count"],
            "max_contracts": real_usage["plan"]["analyses_per_month"] if real_usage["plan"]["analyses_per_month"] != -1 else "∞",
            "usage_percent": real_usage["limits"]["analyses"]["percentage"],
            "copilot_queries": real_usage["usage"]["copilot_queries"],
            "max_copilot": real_usage["plan"]["copilot_queries_per_month"] if real_usage["plan"]["copilot_queries_per_month"] != -1 else "∞",
            "copilot_percent": real_usage["limits"]["copilot"]["percentage"],
            "plan_name": real_usage["plan"]["name"],
            "plan_price": real_usage["plan"]["price"]
        }
    except Exception as e:
        print(f"Usage error: {e}")
        usage = get_current_usage()
    
    # Admin sieht Enterprise-Plan ohne Kosten
    if is_admin:
        plan_card = """
      <div class="content-card" style="background:linear-gradient(135deg, var(--sbs-blue), #004d73);color:white;margin-bottom:24px;">
        <div class="content-card-body">
          <div style="font-size:0.85rem;text-transform:uppercase;letter-spacing:0.1em;opacity:0.8;margin-bottom:8px;">⭐ ADMIN-ZUGANG</div>
          <div style="font-size:2rem;font-weight:700;">Enterprise</div>
          <p style="opacity:0.8;margin:8px 0 0;">Unbegrenzter Zugang zu allen Funktionen.</p>
          <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:12px;">
            <span style="background:rgba(255,255,255,0.2);padding:6px 12px;border-radius:6px;font-size:0.85rem;">✓ Unbegrenzte Benutzer</span>
            <span style="background:rgba(255,255,255,0.2);padding:6px 12px;border-radius:6px;font-size:0.85rem;">✓ Unbegrenzte Verträge</span>
            <span style="background:rgba(255,255,255,0.2);padding:6px 12px;border-radius:6px;font-size:0.85rem;">✓ Priority Support</span>
            <span style="background:rgba(255,255,255,0.2);padding:6px 12px;border-radius:6px;font-size:0.85rem;">✓ API-Zugang</span>
          </div>
        </div>
      </div>"""
    else:
        plan_name = sub.get('plan', 'professional').title()
        price = sub.get('price_cents', 17900) / 100
        period_end = sub.get('current_period_end', '')[:10] if sub.get('current_period_end') else 'N/A'
        plan_card = f"""
      <div class="content-card" style="background:linear-gradient(135deg, var(--sbs-blue), #004d73);color:white;margin-bottom:24px;">
        <div class="content-card-body">
          <div style="font-size:0.85rem;text-transform:uppercase;letter-spacing:0.1em;opacity:0.8;margin-bottom:8px;">Aktueller Plan: {plan_name}</div>
          <div style="font-size:2.5rem;font-weight:700;">{price:.0f}€ <span style="font-size:1rem;font-weight:400;opacity:0.8;">/ Monat</span></div>
          <p style="opacity:0.8;margin:8px 0 0;">Nächste Abrechnung: {period_end}</p>
          <div style="margin-top:24px;display:flex;gap:12px;">
            <a href="https://sbsdeutschland.com/loesungen/vertragsanalyse/preise.html" class="btn" style="background:white;color:var(--sbs-blue);text-decoration:none;">Plan ändern</a>
            <button class="btn btn-secondary" style="background:rgba(255,255,255,0.2);color:white;border:1px solid rgba(255,255,255,0.3);">Kündigen</button>
          </div>
        </div>
      </div>"""
    
    invoice_rows = ""
    if not is_admin:
        for inv in history:
            status_badge = '<span class="badge badge-success">Bezahlt</span>' if inv['status'] == 'paid' else '<span class="badge badge-warning">Offen</span>'
            invoice_rows += f'<tr><td style="font-family:monospace;">{inv["id"]}</td><td>{inv["date"]}</td><td><strong>{inv["amount"]}</strong></td><td>{status_badge}</td><td><button class="btn btn-secondary" style="padding:6px 14px;font-size:0.8rem;">PDF</button></td></tr>'
    
    invoice_section = ""
    if not is_admin and invoice_rows:
        invoice_section = f"""
      <div class="content-card">
        <div class="content-card-header"><h3 class="content-card-title">📄 Rechnungshistorie</h3></div>
        <div class="content-card-body" style="padding:0;">
          <table class="data-table">
            <thead><tr><th>Rechnungsnr.</th><th>Datum</th><th>Betrag</th><th>Status</th><th>Aktion</th></tr></thead>
            <tbody>{invoice_rows}</tbody>
          </table>
        </div>
      </div>"""
    
    content = f"""
<div class="hero">
  <div class="container">
    <div class="hero-badge"><span class="dot"></span> ABRECHNUNG</div>
    <h1>💳 Abrechnung</h1>
    <p>Verwalten Sie Ihr Abonnement und sehen Sie Ihre Rechnungen ein.</p>
  </div>
</div>
<div class="page-container">
  {plan_card}
  <div class="content-card">
    <div class="content-card-header"><h3 class="content-card-title">📊 Nutzung diesen Monat</h3></div>
    <div class="content-card-body">
      <div style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:8px;"><span>Verträge analysiert</span><strong>{usage['contracts_analyzed']} / {'∞' if is_admin else usage['max_contracts']}</strong></div>
        <div style="height:8px;background:#e2e8f0;border-radius:4px;overflow:hidden;"><div style="height:100%;width:{0 if is_admin else usage['usage_percent']}%;background:linear-gradient(90deg,var(--sbs-blue),var(--sbs-yellow));border-radius:4px;"></div></div>
      </div>
      <div class="stats-grid" style="margin-bottom:0;">
        <div class="stat-card"><div class="stat-value">{usage['contracts_analyzed']}</div><div class="stat-label">Verträge</div></div>
        <div class="stat-card"><div class="stat-value">{usage['pages_processed']}</div><div class="stat-label">Seiten</div></div>
        <div class="stat-card"><div class="stat-value">{usage['exports_generated']}</div><div class="stat-label">Exporte</div></div>
        <div class="stat-card"><div class="stat-value">{usage['api_calls']}</div><div class="stat-label">API-Aufrufe</div></div>
      </div>
    </div>
  </div>
  {invoice_section}
</div>"""
    return page_wrapper("Abrechnung", content, user_name, "settings")


def get_team_page(user_name: str = "User"):
    members = get_team_members()
    stats = get_team_stats()
    
    member_rows = ""
    for m in members:
        avatar_color = m.get('avatar_color', '#003856')
        initial = m['name'][0].upper() if m.get('name') else '?'
        
        role_badges = {'admin': '<span class="badge badge-danger">Admin</span>',
                       'editor': '<span class="badge badge-info">Editor</span>',
                       'viewer': '<span class="badge badge-muted">Viewer</span>'}
        role_badge = role_badges.get(m.get('role', 'viewer'), '<span class="badge badge-muted">Viewer</span>')
        
        status_badges = {'active': '<span class="badge badge-success">Aktiv</span>',
                         'pending': '<span class="badge badge-warning">Eingeladen</span>'}
        status_badge = status_badges.get(m.get('status', 'active'), '<span class="badge badge-muted">-</span>')
        
        member_rows += f"""
          <tr>
            <td><div class="user-row"><div class="user-avatar-large" style="background:{avatar_color};">{initial}</div><div class="user-info"><strong>{m['name']}</strong><small>{m['email']}</small></div></div></td>
            <td>{role_badge}</td>
            <td>{status_badge}</td>
            <td style="color:var(--sbs-muted);">-</td>
            <td><button class="btn btn-secondary" style="padding:6px 14px;font-size:0.8rem;">Bearbeiten</button></td>
          </tr>"""
    
    content = f"""
<div class="hero">
  <div class="container">
    <div class="hero-badge"><span class="dot"></span> TEAM</div>
    <h1>👥 Team verwalten</h1>
    <p>Laden Sie Teammitglieder ein und verwalten Sie Berechtigungen.</p>
  </div>
</div>
<div class="page-container">
  <div class="stats-grid">
    <div class="stat-card"><div class="stat-value">{stats['total']}</div><div class="stat-label">Teammitglieder</div></div>
    <div class="stat-card"><div class="stat-value">{stats['admins']}</div><div class="stat-label">Admins</div></div>
    <div class="stat-card"><div class="stat-value">{stats['max_users']}</div><div class="stat-label">Max. Sitze</div></div>
    <div class="stat-card"><div class="stat-value">{stats['available']}</div><div class="stat-label">Verfügbar</div></div>
  </div>
  <div class="content-card">
    <div class="content-card-header"><h3 class="content-card-title">Teammitglieder</h3><button class="btn btn-primary" onclick="openInviteModal()">+ Einladen</button></div>
    <div class="content-card-body" style="padding:0;">
      <table class="data-table">
        <thead><tr><th>Mitglied</th><th>Rolle</th><th>Status</th><th>Aktivität</th><th>Aktion</th></tr></thead>
        <tbody>{member_rows}</tbody>
      </table>
    </div>
  </div>
</div>"""
    
    # Modal HTML (außerhalb f-string)
    modal_html = """
<!-- Einladen Modal -->
<div id="inviteModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:1000;align-items:center;justify-content:center;">
  <div style="background:white;border-radius:16px;padding:32px;max-width:450px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
    <h3 style="margin:0 0 24px;color:#1e293b;">👥 Teammitglied einladen</h3>
    <div style="margin-bottom:16px;">
      <label style="display:block;font-weight:600;margin-bottom:6px;color:#475569;">Name</label>
      <input type="text" id="inviteName" placeholder="Max Mustermann" style="width:100%;padding:12px;border:1px solid #e2e8f0;border-radius:8px;font-size:14px;">
    </div>
    <div style="margin-bottom:16px;">
      <label style="display:block;font-weight:600;margin-bottom:6px;color:#475569;">E-Mail</label>
      <input type="email" id="inviteEmail" placeholder="max@firma.de" style="width:100%;padding:12px;border:1px solid #e2e8f0;border-radius:8px;font-size:14px;">
    </div>
    <div style="margin-bottom:24px;">
      <label style="display:block;font-weight:600;margin-bottom:6px;color:#475569;">Rolle</label>
      <select id="inviteRole" style="width:100%;padding:12px;border:1px solid #e2e8f0;border-radius:8px;font-size:14px;">
        <option value="viewer">Viewer - Nur lesen</option>
        <option value="editor">Editor - Bearbeiten</option>
        <option value="admin">Admin - Vollzugriff</option>
      </select>
    </div>
    <div style="display:flex;gap:12px;">
      <button onclick="closeInviteModal()" style="flex:1;padding:12px;border:1px solid #e2e8f0;background:white;border-radius:8px;cursor:pointer;font-weight:600;">Abbrechen</button>
      <button onclick="sendInvite()" style="flex:1;padding:12px;border:none;background:#003856;color:white;border-radius:8px;cursor:pointer;font-weight:600;">Einladen</button>
    </div>
  </div>
</div>
<script>
function openInviteModal(){document.getElementById('inviteModal').style.display='flex';}
function closeInviteModal(){document.getElementById('inviteModal').style.display='none';document.getElementById('inviteName').value='';document.getElementById('inviteEmail').value='';}
function sendInvite(){var n=document.getElementById('inviteName').value,e=document.getElementById('inviteEmail').value,r=document.getElementById('inviteRole').value;if(!n||!e){alert('Bitte Name und E-Mail eingeben');return;}var fd=new FormData();fd.append('name',n);fd.append('email',e);fd.append('role',r);fetch('/api/team/invite',{method:'POST',body:fd}).then(function(r){return r.json();}).then(function(d){if(d.success){alert('Einladung gesendet');closeInviteModal();location.reload();}else{alert(d.error||'Fehler');}});}
document.getElementById('inviteModal').onclick=function(e){if(e.target===this)closeInviteModal();};
</script>
"""
    return page_wrapper("Team", content + modal_html, user_name, "settings")


def get_audit_page(user_name: str = "User"):
    logs = get_audit_logs(limit=50)
    stats = get_audit_stats()
    
    log_rows = ""
    for log in logs:
        timestamp = log.get('timestamp', '')[:19].replace('T', ' ') if log.get('timestamp') else '-'
        action_badges = {'login': '<span class="badge badge-info">Login</span>',
                         'upload': '<span class="badge badge-success">Upload</span>',
                         'analyze': '<span class="badge badge-success">Analyse</span>',
                         'export': '<span class="badge badge-warning">Export</span>'}
        action_badge = action_badges.get(log.get('action', '').lower(), f'<span class="badge badge-muted">{log.get("action", "-")}</span>')
        log_rows += f'<tr><td style="font-family:monospace;font-size:0.85rem;">{timestamp}</td><td><strong>{log.get("user_name", log.get("user_email", "-"))}</strong></td><td>{action_badge}</td><td>{log.get("details", "-") or "-"}</td><td style="font-family:monospace;font-size:0.85rem;color:var(--sbs-muted);">{log.get("ip_address", "-")}</td></tr>'
    
    if not log_rows:
        log_rows = '<tr><td colspan="5" style="text-align:center;padding:40px;color:var(--sbs-muted);">Noch keine Aktivitäten protokolliert.</td></tr>'
    
    content = f"""
<div class="hero">
  <div class="container">
    <div class="hero-badge"><span class="dot"></span> AUDIT-LOG</div>
    <h1>📋 Audit-Log</h1>
    <p>Vollständige Protokollierung aller Aktivitäten.</p>
  </div>
</div>
<div class="page-container">
  <div class="stats-grid">
    <div class="stat-card"><div class="stat-value">{stats['today']}</div><div class="stat-label">Heute</div></div>
    <div class="stat-card"><div class="stat-value">{stats['this_week']}</div><div class="stat-label">Diese Woche</div></div>
    <div class="stat-card"><div class="stat-value">{stats['unique_users_today']}</div><div class="stat-label">Aktive User</div></div>
    <div class="stat-card"><div class="stat-value">{stats['total']}</div><div class="stat-label">Gesamt</div></div>
  </div>
  <div class="content-card">
    <div class="content-card-header"><h3 class="content-card-title">Aktivitäten</h3><button class="btn btn-secondary">CSV Export</button></div>
    <div class="content-card-body" style="padding:0;">
      <table class="data-table">
        <thead><tr><th>Zeitstempel</th><th>Benutzer</th><th>Aktion</th><th>Details</th><th>IP-Adresse</th></tr></thead>
        <tbody>{log_rows}</tbody>
      </table>
    </div>
  </div>
</div>"""
    return page_wrapper("Audit-Log", content, user_name, "settings")
