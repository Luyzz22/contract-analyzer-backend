"""
SBS Contract Intelligence - Enterprise Frontend
Exaktes Header/Footer Design wie Invoice App (app.sbsdeutschland.com)
Mit allen 8 Vertragstypen und Enterprise Navigation
"""

# =============================================================================
# CFO ENTERPRISE SAAS - NAVIGATION ARCHITECTURE
# =============================================================================
#
# Header Navigation (angepasst für Contract Intelligence):
# - Hauptnav: Analyse | Verlauf | Analytics | Tools ▼ | [User] ▼
# - Tools Dropdown: Vertragsvergleich, Klausel-Bibliothek, Export-Historie, → KI-Rechnungen
# - User Dropdown:
#   - WORKSPACE: Analyse, Verlauf, Analytics, Export-Historie
#   - KONTO: Einstellungen, Abrechnung, Team, Audit-Log
#   - APPS: → KI-Rechnungen (Cross-Link)
#
# Footer (4 Spalten - dunkelblau):
# - Branding: Logo, Tagline, Adresse
# - App: Analyse, Verlauf, Analytics, Vergleich, Bibliothek
# - Konto: Einstellungen, Abrechnung, Team, Export-Historie
# - Support: Hilfe & FAQ, Kontakt, Impressum, Datenschutz
#
# Vertragstypen (8 Enterprise-Standard):
# 👔 Arbeitsvertrag, ☁️ SaaS-Vertrag, 🤝 NDA, 🏭 Lieferant,
# 📋 Dienstleistung, 🏢 Mietvertrag, 🛒 Kaufvertrag, ⚖️ Allgemein
# =============================================================================

# Shared CSS - Exakt wie Invoice App
SBS_CSS = '''
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");

:root {
  --sbs-blü: #003856;
  --sbs-blü-dark: #002a42;
  --sbs-blü-light: #00507a;
  --sbs-yellow: #FFB900;
  --sbs-bg: #f4f7fa;
  --sbs-text: #111827;
  --sbs-muted: #6b7280;
  --sbs-border: #e5e7eb;
  --sbs-card: #ffffff;
  --sbs-success: #10b981;
  --sbs-warning: #f59e0b;
  --sbs-danger: #ef4444;
  --sbs-critical: #dc2626;
  --sbs-high: #ea580c;
  --sbs-medium: #d97706;
  --sbs-low: #16a34a;
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

/* ============================================
   HEADER - Exakt wie Invoice App
   ============================================ */
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

.header-logo img {
  height: 40px;
  width: auto;
}

.header-logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.header-logo-text .brand {
  font-size: 15px;
  font-weight: 600;
  color: var(--sbs-blü);
}

.header-logo-text .subtitle {
  font-size: 12px;
  color: var(--sbs-muted);
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-nav a {
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--sbs-text);
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.header-nav a:hover {
  background: rgba(0,56,86,0.05);
  color: var(--sbs-blü);
}

.header-nav a.active {

/* Home Button */
.home-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  color: var(--primary);
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
.app-switcher-btn:hover { background: rgba(0,56,86,0.08); color: var(--primary); }
.app-item { display: flex !important; align-items: center; gap: 12px; padding: 10px 16px !important; }
  color: var(--sbs-blü);

/* Home Button */
.home-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  color: var(--primary);
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
.app-switcher-btn:hover { background: rgba(0,56,86,0.08); color: var(--primary); }
.app-item { display: flex !important; align-items: center; gap: 12px; padding: 10px 16px !important; }
  background: rgba(0,56,86,0.08);

/* Home Button */
.home-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  color: var(--primary);
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
.app-switcher-btn:hover { background: rgba(0,56,86,0.08); color: var(--primary); }
.app-item { display: flex !important; align-items: center; gap: 12px; padding: 10px 16px !important; }
}

/* Home Button */
.home-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  color: var(--primary);
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
.app-switcher-btn:hover { background: rgba(0,56,86,0.08); color: var(--primary); }
.app-item { display: flex !important; align-items: center; gap: 12px; padding: 10px 16px !important; }

/* Dropdown Menus */
.dropdown {
  position: relative;
}

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

.dropdown-toggle:hover {
  background: rgba(0,56,86,0.05);
  color: var(--sbs-blü);
}

.dropdown-toggle svg {
  width: 16px;
  height: 16px;
  transition: transform 0.2s ease;
}

.dropdown:hover .dropdown-toggle svg {
  transform: rotate(180deg);
}

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

.dropdown:hover .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-section {
  padding: 4px 0;
}

.dropdown-section:not(:last-child) {
  border-bottom: 1px solid var(--sbs-border);
  margin-bottom: 4px;
  padding-bottom: 8px;
}

.dropdown-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--sbs-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 8px 12px 4px;
}

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

.dropdown-item:hover {
  background: rgba(0,56,86,0.05);
  color: var(--sbs-blü);
}

.dropdown-item .icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.dropdown-item.cross-link {
  color: var(--sbs-yellow);
  font-weight: 500;
}

.dropdown-item.cross-link:hover {
  background: rgba(255,185,0,0.1);
  color: var(--sbs-yellow);
}

/* User Button */
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

.user-btn:hover {
  background: rgba(0,56,86,0.1);
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: var(--sbs-blü);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--sbs-text);
}

.user-btn svg {
  width: 16px;
  height: 16px;
  color: var(--sbs-muted);
}

/* ============================================
   MAIN CONTENT
   ============================================ */
main {
  flex: 1;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px;
}

/* Hero Section - Dark Gradient */
.hero {
  background: linear-gradient(135deg, var(--sbs-blü) 0%, var(--sbs-blü-dark) 100%);
  color: #fff;
  padding: 48px 24px;
}

.hero .container {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.1);
  padding: 8px 16px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 20px;
}

.hero-badge .dot {
  width: 8px;
  height: 8px;
  background: var(--sbs-yellow);
  border-radius: 50%;
}

.hero h1 {
  font-size: 2.25rem;
  font-weight: 700;
  margin-bottom: 12px;
  color: #fff;
}

.hero p {
  font-size: 1.1rem;
  opacity: 0.9;
  max-width: 600px;
}

/* Cards */
.card {
  background: var(--sbs-card);
  border-radius: 16px;
  border: 1px solid var(--sbs-border);
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}

.card-body {
  padding: 32px;
}

/* Upload Zone */
.upload-zone {
  border: 2px dashed var(--sbs-border);
  border-radius: 16px;
  padding: 48px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #fafbfc;
}

.upload-zone:hover {
  border-color: var(--sbs-blü);
  background: rgba(0,56,86,0.02);
}

.upload-zone.dragover {
  border-color: var(--sbs-yellow);
  background: rgba(255,185,0,0.05);
}

.upload-zone.has-file {
  border-color: var(--sbs-success);
  background: rgba(16,185,129,0.05);
}

.upload-icon {
  font-size: 3.5rem;
  margin-bottom: 16px;
}

.upload-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--sbs-text);
  margin-bottom: 8px;
}

.upload-subtitle {
  font-size: 0.9rem;
  color: var(--sbs-muted);
}

/* Contract Type Selection - 8 Types Grid */
.type-section {
  margin-top: 32px;
}

.type-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--sbs-text);
  margin-bottom: 16px;
}

.type-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

@media (max-width: 768px) {
  .type-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.type-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 12px;
  border: 2px solid var(--sbs-border);
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
  font-weight: 500;
  color: var(--sbs-text);
}

.type-btn:hover {
  border-color: var(--sbs-blü);
  background: rgba(0,56,86,0.02);
}

.type-btn.selected {
  border-color: var(--sbs-yellow);
  background: rgba(255,185,0,0.08);
}

.type-btn .emoji {
  font-size: 1.5rem;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 28px;
  font-size: 15px;
  font-weight: 600;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-primary {
  background: var(--sbs-yellow);
  color: var(--sbs-blü);
}

.btn-primary:hover {
  background: var(--sbs-blü);
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,56,86,0.25);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-full {
  width: 100%;
}

/* Trust Bar */
.trust-bar {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 24px;
  margin-top: 32px;
  padding: 24px;
  background: rgba(0,56,86,0.02);
  border-radius: 12px;
}

.trust-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--sbs-muted);
}

.trust-item .icon {
  font-size: 18px;
}

/* File Info */
.file-info {
  display: none;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding: 14px 18px;
  background: rgba(16,185,129,0.1);
  border-radius: 10px;
  border: 1px solid rgba(16,185,129,0.2);
}

.file-info.show {
  display: flex;
}

.file-info .file-icon {
  font-size: 20px;
}

.file-info .file-name {
  flex: 1;
  font-weight: 500;
  color: var(--sbs-text);
}

.file-info .file-remove {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.05);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: var(--sbs-muted);
  transition: all 0.15s ease;
}

.file-info .file-remove:hover {
  background: rgba(239,68,68,0.1);
  color: var(--sbs-danger);
}

/* ============================================
   FOOTER - Exakt wie Invoice App (dunkelblau)
   ============================================ */
footer {
  background: var(--sbs-blü-dark);
  color: #fff;
  margin-top: auto;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 64px 24px 32px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr 1fr;
  gap: 48px;
  margin-bottom: 48px;
}

@media (max-width: 768px) {
  .footer-grid {
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }
}

@media (max-width: 480px) {
  .footer-grid {
    grid-template-columns: 1fr;
  }
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.footer-logo img {
  height: 36px;
  width: auto;
  filter: brightness(0) invert(1);
}

.footer-logo-text {
  display: flex;
  flex-direction: column;
}

.footer-logo-text .name {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.footer-logo-text .sub {
  font-size: 13px;
  color: rgba(255,255,255,0.7);
}

.footer-tagline {
  font-size: 14px;
  color: rgba(255,255,255,0.7);
  line-height: 1.6;
}

.footer-address {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: rgba(255,255,255,0.6);
}

.footer-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--sbs-yellow);
  margin-bottom: 20px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.footer-section ul {
  list-style: none;
}

.footer-section li {
  margin-bottom: 12px;
}

.footer-section a {
  font-size: 14px;
  color: rgba(255,255,255,0.8);
  text-decoration: none;
  transition: color 0.15s ease;
}

.footer-section a:hover {
  color: var(--sbs-yellow);
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 32px;
  border-top: 1px solid rgba(255,255,255,0.1);
  font-size: 14px;
  color: rgba(255,255,255,0.5);
}

@media (max-width: 768px) {
  .footer-bottom {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
}

.footer-bottom .heart {
  color: #ef4444;
}

/* ============================================
   RESULT DISPLAY
   ============================================ */
.result-card {
  margin-top: 32px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px 32px;
  border-bottom: 1px solid var(--sbs-border);
}

.result-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--sbs-text);
}

.result-meta {
  font-size: 14px;
  color: var(--sbs-muted);
  margin-top: 4px;
}

.risk-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;
}

.risk-badge.critical { background: rgba(220,38,38,0.1); color: var(--sbs-critical); }
.risk-badge.high { background: rgba(234,88,12,0.1); color: var(--sbs-high); }
.risk-badge.medium { background: rgba(217,119,6,0.1); color: var(--sbs-medium); }
.risk-badge.low, .risk-badge.minimal { background: rgba(22,163,74,0.1); color: var(--sbs-low); }

/* Tabs */
.tabs {
  display: flex;
  gap: 4px;
  padding: 16px 32px;
  background: #f8fafc;
  border-bottom: 1px solid var(--sbs-border);
}

.tab {
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  color: var(--sbs-muted);
  background: none;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab:hover {
  color: var(--sbs-text);
}

.tab.active {
  background: #fff;
  color: var(--sbs-blü);
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.tab-content {
  display: none;
  padding: 32px;
}

.tab-content.active {
  display: block;
}

/* Data Grid */
.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.data-section {
  background: #fafbfc;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--sbs-border);
}

.data-section h4 {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--sbs-blü);
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--sbs-border);
}

.data-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid rgba(0,0,0,0.04);
}

.data-row:last-child {
  border-bottom: none;
}

.data-label {
  font-size: 14px;
  color: var(--sbs-muted);
}

.data-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--sbs-text);
  text-align: right;
}

/* Risk Items */
.risk-item {
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 16px;
  border-left: 4px solid;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.risk-item.critical { border-color: var(--sbs-critical); background: rgba(220,38,38,0.02); }
.risk-item.high { border-color: var(--sbs-high); background: rgba(234,88,12,0.02); }
.risk-item.medium { border-color: var(--sbs-medium); background: rgba(217,119,6,0.02); }
.risk-item.low { border-color: var(--sbs-low); background: rgba(22,163,74,0.02); }

.risk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 12px;
}

.risk-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--sbs-text);
}

.risk-severity {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  padding: 4px 10px;
  border-radius: 4px;
}

.risk-severity.critical { background: rgba(220,38,38,0.1); color: var(--sbs-critical); }
.risk-severity.high { background: rgba(234,88,12,0.1); color: var(--sbs-high); }
.risk-severity.medium { background: rgba(217,119,6,0.1); color: var(--sbs-medium); }
.risk-severity.low { background: rgba(22,163,74,0.1); color: var(--sbs-low); }

.risk-description {
  font-size: 14px;
  color: var(--sbs-muted);
  margin-bottom: 16px;
  line-height: 1.6;
}

.risk-clause {
  font-size: 14px;
  padding: 16px;
  background: rgba(0,0,0,0.02);
  border-radius: 8px;
  border-left: 3px solid var(--sbs-border);
  font-style: italic;
  color: var(--sbs-text);
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.risk-clause:hover {
  background: rgba(0,56,86,0.04);
  border-left-color: var(--sbs-blü);
}

.risk-legal {
  display: inline-block;
  font-size: 13px;
  padding: 8px 14px;
  background: rgba(0,56,86,0.06);
  border-radius: 6px;
  color: var(--sbs-blü);
  margin-bottom: 16px;
}

.risk-recommendation {
  font-size: 14px;
  padding-top: 16px;
  border-top: 1px solid rgba(0,0,0,0.06);
  line-height: 1.6;
}

.risk-recommendation strong {
  color: var(--sbs-success);
}

/* Export Section */
.export-section {
  display: flex;
  gap: 12px;
  padding: 24px 32px;
  border-top: 1px solid var(--sbs-border);
  background: #fafbfc;
}

.export-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 20px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid var(--sbs-border);
  border-radius: 10px;
  background: #fff;
  color: var(--sbs-text);
  text-decoration: none;
  transition: all 0.15s ease;
}

.export-btn:hover {
  border-color: var(--sbs-blü);
  background: rgba(0,56,86,0.02);
}

.export-btn.primary {
  background: var(--sbs-yellow);
  color: var(--sbs-blü);
  border-color: var(--sbs-yellow);
}

.export-btn.primary:hover {
  background: var(--sbs-blü);
  color: #fff;
  border-color: var(--sbs-blü);
}

/* Loading */
.loading {
  text-align: center;
  padding: 60px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 3px solid var(--sbs-border);
  border-top-color: var(--sbs-blü);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Chat Modal */
.chat-modal {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 1000;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.chat-modal.show {
  display: flex;
}

.chat-box {
  background: #fff;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  max-height: 85vh;
  overflow: hidden;
  box-shadow: 0 24px 48px rgba(0,0,0,0.2);
}

.chat-header {
  background: linear-gradient(135deg, var(--sbs-blü), var(--sbs-blü-dark));
  color: #fff;
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h3 {
  font-size: 18px;
  font-weight: 600;
}

.chat-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.1);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.chat-close:hover {
  background: rgba(255,255,255,0.2);
}

.chat-body {
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
}

/* Summary Box */
.summary-box {
  background: linear-gradient(135deg, rgba(0,56,86,0.04), rgba(0,56,86,0.08));
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  border-left: 4px solid var(--sbs-blü);
}

.summary-box h3 {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--sbs-muted);
  margin-bottom: 12px;
}

.summary-box p {
  font-size: 15px;
  line-height: 1.7;
  color: var(--sbs-text);
}

/* No Risks */
.no-risks {
  text-align: center;
  padding: 60px 40px;
  background: rgba(22,163,74,0.05);
  border-radius: 16px;
  border: 1px solid rgba(22,163,74,0.2);
}

.no-risks .icon {
  font-size: 4rem;
  margin-bottom: 16px;
}

.no-risks p {
  font-size: 16px;
  font-weight: 500;
  color: var(--sbs-low);
}

/* Explain Button */
.explain-btn {
  padding: 8px 14px;
  background: #fff;
  border: 1px solid var(--sbs-blü);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--sbs-blü);
  cursor: pointer;
  transition: all 0.15s ease;
}

.explain-btn:hover {
  background: var(--sbs-blü);
  color: #fff;
}
</style>
'''

# =============================================================================
# SHARED HEADER COMPONENT - Exakt wie Invoice App
# =============================================================================
SBS_HEADER = '''
<header>
  <div class="header-container">
    <!-- Home Button -->
    <a href="https://app.sbsdeutschland.com/dashboard" class="home-btn" title="Dashboard">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
        <polyline points="9 22 9 12 15 12 15 22"></polyline>
      </svg>
    </a>
    
    <a href="/" class="header-logo">
      <img src="/static/sbs-logo-new.png" alt="SBS Logo" onerror="this.style.display='none'">
      <div class="header-logo-text">
        <span class="brand">SBS Deutschland</span>
        <span class="subtitle">Smart Business Service · Weinheim</span>
      </div>
    </a>
    
    <nav class="header-nav">
      <a href="/upload" id="nav-upload">Analyse</a>
      <a href="/history" id="nav-history">Verlauf</a>
      <a href="/analytics" id="nav-analytics">Analytics</a>
      
      <!-- Tools Dropdown -->
      <div class="dropdown">
        <button class="dropdown-toggle">
          Tools
          <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
        </button>
        <div class="dropdown-menu">
          <div class="dropdown-section">
            <a href="/compare" class="dropdown-item">
              <span class="icon">⚖️</span>
              Vertragsvergleich
            </a>
            <a href="/library" class="dropdown-item">
              <span class="icon">📚</span>
              Klausel-Bibliothek
            </a>
            <a href="/exports" class="dropdown-item">
              <span class="icon">📁</span>
              Export-Historie
            </a>
          </div>
          <div class="dropdown-section">
            <a href="https://app.sbsdeutschland.com" class="dropdown-item cross-link" target="_blank">
              <span class="icon">🧾</span>
              → KI-Rechnungen
            </a>
          </div>
        </div>
      </div>
      
      <!-- App Switcher -->
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
        <div class="dropdown-menu app-switcher-menu" style="width:300px;">
          <div class="dropdown-section">
            <div class="dropdown-label">SBS Plattform</div>
            <a href="https://app.sbsdeutschland.com/dashboard" class="dropdown-item app-item">
              <span class="app-icon" style="background:linear-gradient(135deg,#003856,#004d73);width:36px;height:36px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;font-size:16px;color:white;">🏠</span>
              <div style="display:flex;flex-direction:column;"><strong>Dashboard</strong><small style="color:#64748b;">Übersicht & Kennzahlen</small></div>
            </a>
          </div>
          <div class="dropdown-section">
            <div class="dropdown-label">Produkte</div>
            <a href="https://app.sbsdeutschland.com" class="dropdown-item app-item">
              <span class="app-icon" style="background:linear-gradient(135deg,#22c55e,#16a34a);width:36px;height:36px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;font-size:16px;color:white;">📄</span>
              <div style="display:flex;flex-direction:column;"><strong>KI-Rechnungen</strong><small style="color:#64748b;">Rechnungsverarbeitung</small></div>
            </a>
            <a href="/" class="dropdown-item app-item" style="background:rgba(255,185,0,0.1);border-left:3px solid #FFB900;">
              <span class="app-icon" style="background:linear-gradient(135deg,#f59e0b,#d97706);width:36px;height:36px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;font-size:16px;color:white;">📋</span>
              <div style="display:flex;flex-direction:column;"><strong>KI-Verträge</strong><small style="color:#64748b;">Vertragsanalyse</small></div>
            </a>
          </div>
        </div>
      </div>
      
      <!-- User Dropdown -->
      <div class="dropdown">
        <button class="user-btn dropdown-toggle">
          <div class="user-avatar">L</div>
          <span class="user-name">Luis Schenk</span>
          <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
        </button>
        <div class="dropdown-menu" style="min-width: 240px;">
          <div class="dropdown-section">
            <div class="dropdown-label">Workspace</div>
            <a href="/upload" class="dropdown-item">
              <span class="icon">📤</span>
              Analyse
            </a>
            <a href="/history" class="dropdown-item">
              <span class="icon">📊</span>
              Verlauf
            </a>
            <a href="/analytics" class="dropdown-item">
              <span class="icon">📈</span>
              Analytics
            </a>
            <a href="/exports" class="dropdown-item">
              <span class="icon">📁</span>
              Export-Historie
            </a>
          </div>
          <div class="dropdown-section">
            <div class="dropdown-label">Konto</div>
            <a href="/settings" class="dropdown-item">
              <span class="icon">⚙️</span>
              Einstellungen
            </a>
            <a href="/billing" class="dropdown-item">
              <span class="icon">💳</span>
              Abrechnung
            </a>
            <a href="/team" class="dropdown-item">
              <span class="icon">👥</span>
              Team
            </a>
            <a href="/audit" class="dropdown-item">
              <span class="icon">📋</span>
              Audit-Log
            </a>
          </div>
          <div class="dropdown-section">
            <div class="dropdown-label">Apps</div>
            <a href="https://app.sbsdeutschland.com" class="dropdown-item cross-link" target="_blank">
              <span class="icon">🧾</span>
              → KI-Rechnungen
            </a>
          </div>
        </div>
      </div>
    </nav>
  </div>
</header>
'''

# =============================================================================
# SHARED FOOTER COMPONENT - Exakt wie Invoice App (dunkelblau)
# =============================================================================
SBS_FOOTER = '''
<footer>
  <div class="footer-container">
    <div class="footer-grid">
      <!-- Brand Column -->
      <div class="footer-brand">
        <div class="footer-logo">
          <img src="/static/sbs-logo-new.png" alt="SBS Logo" onerror="this.style.display='none'">
          <div class="footer-logo-text">
            <span class="name">SBS Deutschland</span>
            <span class="sub">Smart Business Service</span>
          </div>
        </div>
        <p class="footer-tagline">
          Enterprise KI-Vertragsanalyse.<br>
          Entwickelt und betrieben in Deutschland.
        </p>
        <div class="footer-address">
          📍 In der Dell 19, 69469 Weinheim
        </div>
      </div>
      
      <!-- App Column -->
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
      
      <!-- Konto Column -->
      <div class="footer-section">
        <h4>Konto</h4>
        <ul>
          <li><a href="/settings">Einstellungen</a></li>
          <li><a href="/billing">Abrechnung</a></li>
          <li><a href="/team">Team</a></li>
          <li><a href="/exports">Export-Historie</a></li>
        </ul>
      </div>
      
      <!-- Support Column -->
      <div class="footer-section">
        <h4>Support</h4>
        <ul>
          <li><a href="/help">Hilfe & FAQ</a></li>
          <li><a href="mailto:info@sbsdeutschland.com">Kontakt</a></li>
          <li><a href="https://sbsdeutschland.com/sbshomepage/impressum.html" target="_blank">Impressum</a></li>
          <li><a href="https://sbsdeutschland.com/sbshomepage/datenschutz.html" target="_blank">Datenschutz</a></li>
        </ul>
      </div>
    </div>
    
    <div class="footer-bottom">
      <span>© 2025 SBS Deutschland GmbH & Co. KG</span>
      <span>Made with <span class="heart">❤️</span> in Weinheim</span>
    </div>
  </div>
</footer>
'''

# =============================================================================
# UPLOAD PAGE - Mit allen 8 Vertragstypen
# =============================================================================
def get_upload_page():
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vertragsanalyse | SBS Contract Intelligence</title>
  <link rel="icon" href="/static/favicon.ico">
  {SBS_CSS}
</head>
<body>
  {SBS_HEADER}
  
  <main>
    <section class="hero">
      <div class="container">
        <div class="hero-badge">
          <span class="dot"></span>
          KI-VERTRAGSANALYSE
        </div>
        <h1>Vertrag analysieren</h1>
        <p>Laden Sie Ihren Vertrag hoch und erhalten Sie eine KI-gestützte Risikoanalyse nach deutschem Recht in Sekunden.</p>
      </div>
    </section>
    
    <div class="container">
      <div class="card">
        <div class="card-body">
          <!-- Upload Zone -->
          <div class="upload-zone" id="uploadZone">
            <div class="upload-icon">📄</div>
            <div class="upload-title">Dateien hier ablegen</div>
            <div class="upload-subtitle">ODER</div>
            <div class="upload-subtitle" style="margin-top: 8px;">Klicken zum Auswählen (PDF, max. 10 MB)</div>
            <input type="file" id="fileInput" accept=".pdf,.docx" style="display:none">
          </div>
          
          <!-- File Info -->
          <div class="file-info" id="fileInfo">
            <span class="file-icon">📄</span>
            <span class="file-name" id="fileName"></span>
            <button class="file-remove" id="removeFile">✕</button>
          </div>
          
          <!-- Contract Type Selection - 8 Types -->
          <div class="type-section">
            <div class="type-label">Vertragstyp auswählen</div>
            <div class="type-grid">
              <button class="type-btn selected" data-type="employment">
                <span class="emoji">👔</span>
                Arbeitsvertrag
              </button>
              <button class="type-btn" data-type="saas">
                <span class="emoji">☁️</span>
                SaaS-Vertrag
              </button>
              <button class="type-btn" data-type="nda">
                <span class="emoji">🤝</span>
                NDA
              </button>
              <button class="type-btn" data-type="vendor">
                <span class="emoji">🏭</span>
                Lieferant
              </button>
              <button class="type-btn" data-type="service">
                <span class="emoji">📋</span>
                Dienstleistung
              </button>
              <button class="type-btn" data-type="rental">
                <span class="emoji">🏢</span>
                Mietvertrag
              </button>
              <button class="type-btn" data-type="purchase">
                <span class="emoji">🛒</span>
                Kaufvertrag
              </button>
              <button class="type-btn" data-type="general">
                <span class="emoji">⚖️</span>
                Allgemein
              </button>
            </div>
          </div>
          
          <!-- Analyze Button -->
          <button class="btn btn-primary btn-full" id="analyzeBtn" disabled style="margin-top: 32px;">
            Vertrag analysieren
          </button>
        </div>
      </div>
      
      <!-- Result Container -->
      <div id="result"></div>
      
      <!-- Trust Bar -->
      <div class="trust-bar">
        <div class="trust-item">
          <span class="icon">🇩🇪</span>
          Made in Germany
        </div>
        <div class="trust-item">
          <span class="icon">🔒</span>
          DSGVO konform
        </div>
        <div class="trust-item">
          <span class="icon">⚖️</span>
          Deutsches Recht
        </div>
        <div class="trust-item">
          <span class="icon">🤖</span>
          GPT-4o powered
        </div>
      </div>
    </div>
  </main>
  
  <!-- Chat Modal -->
  <div class="chat-modal" id="chatModal">
    <div class="chat-box">
      <div class="chat-header">
        <h3>🤖 Klausel erklärt</h3>
        <button class="chat-close" onclick="closeChat()">×</button>
      </div>
      <div class="chat-body" id="chatBody"></div>
    </div>
  </div>
  
  {SBS_FOOTER}
  
  <script>
    // Active nav highlighting
    document.getElementById('nav-upload').classList.add('active');
    
    // File upload handling
    const zone = document.getElementById('uploadZone');
    const input = document.getElementById('fileInput');
    const info = document.getElementById('fileInfo');
    const fname = document.getElementById('fileName');
    const removeBtn = document.getElementById('removeFile');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const result = document.getElementById('result');
    const typeButtons = document.querySelectorAll('.type-btn');
    
    let selectedFile = null;
    let selectedType = 'employment';
    let contractId = null;
    
    // Click to upload
    zone.onclick = () => input.click();
    
    // Drag & drop
    zone.ondragover = (e) => {{
      e.preventDefault();
      zone.classList.add('dragover');
    }};
    
    zone.ondragleave = () => zone.classList.remove('dragover');
    
    zone.ondrop = (e) => {{
      e.preventDefault();
      zone.classList.remove('dragover');
      if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
    }};
    
    // File input change
    input.onchange = (e) => {{
      if (e.target.files[0]) setFile(e.target.files[0]);
    }};
    
    // Remove file
    removeBtn.onclick = (e) => {{
      e.stopPropagation();
      clearFile();
    }};
    
    function setFile(file) {{
      if (file.size > 10 * 1024 * 1024) {{
        alert('Datei zu groß. Maximal 10 MB erlaubt.');
        return;
      }}
      selectedFile = file;
      fname.textContent = file.name;
      info.classList.add('show');
      zone.classList.add('has-file');
      analyzeBtn.disabled = false;
    }}
    
    function clearFile() {{
      selectedFile = null;
      input.value = '';
      info.classList.remove('show');
      zone.classList.remove('has-file');
      analyzeBtn.disabled = trü;
    }}
    
    // Type selection
    typeButtons.forEach(btn => {{
      btn.onclick = () => {{
        typeButtons.forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        selectedType = btn.dataset.type;
      }};
    }});
    
    // Analyze
    analyzeBtn.onclick = async () => {{
      if (!selectedFile) return;
      
      analyzeBtn.disabled = trü;
      result.innerHTML = `
        <div class="card result-card">
          <div class="loading">
            <div class="spinner"></div>
            <p>Analyse läuft (15-30 Sekunden)...</p>
          </div>
        </div>
      `;
      
      try {{
        // Upload
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('contract_type', selectedType);
        
        const uploadRes = await fetch('/api/v3/contracts/upload', {{
          method: 'POST',
          body: formData
        }});
        
        const uploadData = await uploadRes.json();
        if (!uploadRes.ok) throw new Error(uploadData.detail || 'Upload fehlgeschlagen');
        
        contractId = uploadData.contract_id;
        
        // Analyze
        const analyzeRes = await fetch(`/api/v3/contracts/${{contractId}}/analyze`, {{
          method: 'POST'
        }});
        
        const analyzeData = await analyzeRes.json();
        if (!analyzeRes.ok) throw new Error(analyzeData.detail || 'Analyse fehlgeschlagen');
        
        showResult(analyzeData);
        
      }} catch (error) {{
        result.innerHTML = `
          <div class="card result-card">
            <div class="card-body" style="text-align: center; padding: 60px;">
              <div style="font-size: 4rem; margin-bottom: 20px;">❌</div>
              <p style="color: var(--sbs-danger); font-size: 16px; margin-bottom: 20px;">${{error.message}}</p>
              <button class="btn btn-primary" onclick="location.reload()">Erneut versuchen</button>
            </div>
          </div>
        `;
      }}
      
      analyzeBtn.disabled = false;
    }};
    
    function showResult(data) {{
      const ra = data.risk_assessment || {{}};
      const ed = data.extracted_data || {{}};
      const riskLevel = ra.overall_risk_level || 'low';
      const riskScore = ra.overall_risk_score || 0;
      
      const riskLabels = {{
        critical: '🔴 Kritisch',
        high: '🟠 Hoch',
        medium: '🟡 Mittel',
        low: '🟢 Niedrig',
        minimal: '⚪ Minimal'
      }};
      
      let html = `
        <div class="card result-card">
          <div class="result-header">
            <div>
              <div class="result-title">${{data.source_filename || 'Vertrag'}}</div>
              <div class="result-meta">${{data.fields_extracted || 0}}/${{data.fields_total || 42}} Felder · ${{(data.processing_time_seconds || 0).toFixed(2)}}s</div>
            </div>
            <div class="risk-badge ${{riskLevel}}">${{riskLabels[riskLevel] || riskLevel}} · ${{riskScore}}/100</div>
          </div>
          
          <div class="tabs">
            <button class="tab active" data-tab="overview">Übersicht</button>
            <button class="tab" data-tab="details">Details</button>
            <button class="tab" data-tab="risks">Risiken</button>
          </div>
          
          <div class="tab-content active" id="tab-overview">
            ${{ra.executive_summary ? `<div class="summary-box"><h3>Zusammenfassung</h3><p>${{ra.executive_summary}}</p></div>` : ''}}
            <div class="data-grid">
              ${{buildDataSections(ed)}}
            </div>
            ${{renderRisks(ra, 3)}}
          </div>
          
          <div class="tab-content" id="tab-details">
            <div class="data-grid">
              ${{buildDetailSections(ed)}}
            </div>
          </div>
          
          <div class="tab-content" id="tab-risks">
            ${{renderRisks(ra, -1)}}
          </div>
          
          <div class="export-section">
            <a href="/api/v3/contracts/${{contractId}}/export/json" class="export-btn" download>📥 JSON Export</a>
            <a href="/api/v3/contracts/${{contractId}}/export/pdf" class="export-btn primary" target="_blank">📄 PDF Report</a>
          </div>
        </div>
      `;
      
      result.innerHTML = html;
      
      // Tab switching
      document.querySelectorAll('.tab').forEach(tab => {{
        tab.onclick = () => {{
          document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
          document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
          tab.classList.add('active');
          document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
        }};
      }});
    }}
    
    function buildDataSections(ed) {{
      let html = '';
      if (ed.employer) html += section('Arbeitgeber', [['Name', ed.employer.name], ['Adresse', ed.employer.address], ['Vertreter', ed.employer.contact_person]]);
      if (ed.employee) html += section('Arbeitnehmer', [['Name', ed.employee.name], ['Adresse', ed.employee.address]]);
      if (ed.provider) html += section('Anbieter', [['Name', ed.provider.name], ['Adresse', ed.provider.address]]);
      if (ed.customer) html += section('Kunde', [['Name', ed.customer.name], ['Adresse', ed.customer.address]]);
      if (ed.supplier) html += section('Lieferant', [['Name', ed.supplier.name], ['Adresse', ed.supplier.address]]);
      if (ed.buyer) html += section('Käufer', [['Name', ed.buyer.name], ['Adresse', ed.buyer.address]]);
      html += section('Vertrag', [
        ['Position', ed.job_title],
        ['Service', ed.service_name],
        ['Gegenstand', ed.contract_subject],
        ['Beginn', formatDate(ed.start_date)],
        ['Befristung', ed.termination?.fixed_term ? 'bis ' + formatDate(ed.termination.end_date) : (ed.contract_term?.initial_term_months ? ed.contract_term.initial_term_months + ' Monate' : 'Unbefristet')]
      ]);
      if (ed.compensation) html += section('Vergütung', [['Bruttogehalt', formatCurrency(ed.compensation.base_salary_gross)], ['Bonus', formatCurrency(ed.compensation.bonus_target)]]);
      if (ed.pricing) html += section('Preise', [['Preis', formatCurrency(ed.pricing.amount) + (ed.pricing.billing_period ? ' / ' + ed.pricing.billing_period : '')], ['Modell', ed.pricing.model]]);
      return html;
    }}
    
    function buildDetailSections(ed) {{
      let html = '';
      if (ed.working_conditions) html += section('Arbeitszeit', [['Wochenstunden', (ed.working_conditions.weekly_hours || '-') + 'h'], ['Homeoffice', ed.working_conditions.home_office_allowed ? '✓ Ja' : '✗ Nein'], ['Überstunden', ed.working_conditions.overtime_included_in_salary ? (ed.working_conditions.overtime_cap_hours ? ed.working_conditions.overtime_cap_hours + 'h abgegolten' : '⚠️ Pauschal') : 'Gesondert']]);
      if (ed.vacation) html += section('Urlaub', [['Tage/Jahr', ed.vacation.days_per_year]]);
      if (ed.probation) html += section('Probezeit', [['Dauer', (ed.probation.duration_months || '-') + ' Monate'], ['Kündigung', ed.probation.notice_period_during_probation]]);
      if (ed.termination) html += section('Kündigung', [['Frist AN', ed.termination.notice_period_employee], ['Befristet', ed.termination.fixed_term ? 'Ja' : 'Nein']]);
      if (ed.contract_term) html += section('Laufzeit', [['Initial', (ed.contract_term.initial_term_months || '-') + ' Monate'], ['Auto-Renewal', ed.contract_term.auto_renewal ? 'Ja' : 'Nein'], ['Kündigungsfrist', (ed.contract_term.notice_period_days || '-') + ' Tage']]);
      if (ed.sla) html += section('SLA', [['Verfügbarkeit', (ed.sla.uptime_percentage || '-') + '%'], ['Reaktion kritisch', ed.sla.response_time_critical]]);
      if (ed.data_protection) html += section('Datenschutz', [['AVV vorhanden', ed.data_protection.dpa_included ? '✓ Ja' : '✗ Nein'], ['Standort', ed.data_protection.data_location], ['EU garantiert', ed.data_protection.data_location_guaranteed_eu ? '✓ Ja' : '✗ Nein']]);
      if (ed.warranty) html += section('Gewährleistung', [['Dauer', (ed.warranty.duration_months || '-') + ' Monate']]);
      if (ed.non_compete) html += section('Wettbewerbsverbot', [['Während Beschäftigung', ed.non_compete.during_employment ? '✓' : '✗'], ['Nachvertraglich', ed.non_compete.post_employment ? (ed.non_compete.missing_compensation ? '⚠️ Ohne Karenz' : '✓') : '✗']]);
      if (ed.confidentiality) html += section('Vertraulichkeit', [['Klausel', ed.confidentiality.confidentiality_clause ? '✓' : '✗'], ['Dauer', ed.confidentiality.duration]]);
      return html;
    }}
    
    function section(title, rows) {{
      let html = `<div class="data-section"><h4>${{title}}</h4>`;
      rows.forEach(([label, value]) => {{
        if (value) html += `<div class="data-row"><span class="data-label">${{label}}</span><span class="data-value">${{value}}</span></div>`;
      }});
      return html + '</div>';
    }}
    
    function renderRisks(ra, limit) {{
      const allRisks = [
        ...(ra.critical_risks || []),
        ...(ra.high_risks || []),
        ...(ra.medium_risks || []),
        ...(ra.low_risks || [])
      ];
      
      if (!allRisks.length) {{
        return '<div class="no-risks"><div class="icon">✅</div><p>Keine Risiken identifiziert</p></div>';
      }}
      
      const risks = limit > 0 ? allRisks.slice(0, limit) : allRisks;
      
      let html = '<div class="risk-list">';
      risks.forEach(risk => {{
        const clauseText = (risk.clause_text || '').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        html += `
          <div class="risk-item ${{risk.risk_level}}">
            <div class="risk-header">
              <span class="risk-title">${{risk.issü_title}}</span>
              <div style="display: flex; align-items: center; gap: 8px;">
                <button class="explain-btn" onclick="explainClause('${{clauseText}}')">💬 Erklären</button>
                <span class="risk-severity ${{risk.risk_level}}">${{risk.risk_level}}</span>
              </div>
            </div>
            <div class="risk-description">${{risk.issü_description}}</div>
            ${{risk.clause_text ? `<div class="risk-clause" onclick="explainClause('${{clauseText}}')">"${{risk.clause_text}}"</div>` : ''}}
            <div class="risk-legal">📖 ${{risk.legal_basis}}</div>
            ${{risk.recommendation ? `<div class="risk-recommendation"><strong>Empfehlung:</strong> ${{risk.recommendation}}</div>` : ''}}
          </div>
        `;
      }});
      
      if (limit > 0 && allRisks.length > limit) {{
        html += `<p style="text-align: center; color: var(--sbs-muted); margin-top: 16px;">+ ${{allRisks.length - limit}} weitere Risiken im Tab "Risiken"</p>`;
      }}
      
      html += '</div>';
      return html;
    }}
    
    function formatDate(d) {{
      if (!d) return null;
      try {{
        return new Date(d).toLocaleDateString('de-DE');
      }} catch {{
        return d;
      }}
    }}
    
    function formatCurrency(a) {{
      if (!a) return null;
      return new Intl.NumberFormat('de-DE', {{ style: 'currency', currency: 'EUR' }}).format(a);
    }}
    
    // Chat Modal
    function explainClause(clauseText) {{
      const modal = document.getElementById('chatModal');
      const body = document.getElementById('chatBody');
      
      modal.classList.add('show');
      body.innerHTML = `
        <div style="background: #f8fafc; padding: 16px; border-radius: 8px; border-left: 4px solid var(--sbs-blü); margin-bottom: 20px; font-style: italic;">"${{clauseText}}"</div>
        <div class="loading">
          <div class="spinner"></div>
          <p>KI analysiert...</p>
        </div>
      `;
      
      fetch('/api/v3/clause/explain', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ clause_text: clauseText, contract_type: selectedType }})
      }})
      .then(r => r.json())
      .then(data => {{
        if (data.detail) throw new Error(data.detail);
        
        const riskLabels = {{
          low: 'Niedriges Risiko',
          medium: 'Mittleres Risiko',
          high: 'Hohes Risiko',
          critical: 'Kritisch'
        }};
        
        body.innerHTML = `
          <div style="background: #f8fafc; padding: 16px; border-radius: 8px; border-left: 4px solid var(--sbs-blü); margin-bottom: 20px; font-style: italic;">"${{clauseText}}"</div>
          <span class="risk-badge ${{data.risk_level}}" style="margin-bottom: 16px;">${{riskLabels[data.risk_level] || data.risk_level}}</span>
          <div style="margin-top: 20px;">
            <h4 style="font-size: 13px; color: var(--sbs-muted); margin-bottom: 8px;">Was bedeutet das?</h4>
            <p style="line-height: 1.6;">${{data.explanation}}</p>
          </div>
          <div style="margin-top: 20px;">
            <h4 style="font-size: 13px; color: var(--sbs-muted); margin-bottom: 8px;">Rechtliche Einschätzung</h4>
            <p style="line-height: 1.6;">${{data.legal_assessment}}</p>
          </div>
          ${{data.related_laws?.length ? `
            <div style="margin-top: 20px;">
              <h4 style="font-size: 13px; color: var(--sbs-muted); margin-bottom: 8px;">Relevante Gesetze</h4>
              <div style="display: flex; flex-wrap: wrap; gap: 8px;">${{data.related_laws.map(l => `<span style="background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 6px; font-size: 13px;">${{l}}</span>`).join('')}}</div>
            </div>
          ` : ''}}
          ${{data.recommendations?.length ? `
            <div style="margin-top: 20px;">
              <h4 style="font-size: 13px; color: var(--sbs-muted); margin-bottom: 8px;">Empfehlungen</h4>
              <ul style="list-style: none; padding: 0;">${{data.recommendations.map(r => `<li style="padding: 8px 0; border-bottom: 1px solid var(--sbs-border);">💡 ${{r}}</li>`).join('')}}</ul>
            </div>
          ` : ''}}
        `;
      }})
      .catch(error => {{
        body.innerHTML = `
          <div style="background: #f8fafc; padding: 16px; border-radius: 8px; border-left: 4px solid var(--sbs-blü); margin-bottom: 20px; font-style: italic;">"${{clauseText}}"</div>
          <div style="text-align: center; color: var(--sbs-danger); padding: 40px;">
            ❌ ${{error.message}}
          </div>
        `;
      }});
    }}
    
    function closeChat() {{
      document.getElementById('chatModal').classList.remove('show');
    }}
    
    document.getElementById('chatModal').onclick = (e) => {{
      if (e.target.id === 'chatModal') closeChat();
    }};
  </script>
</body>
</html>'''


# =============================================================================
# LANDING PAGE
# =============================================================================
def get_landing_page():
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SBS Contract Intelligence | KI-Vertragsanalyse</title>
  <link rel="icon" href="/static/favicon.ico">
  {SBS_CSS}
  <style>
    .landing-hero {{
      background: linear-gradient(135deg, var(--sbs-blü) 0%, var(--sbs-blü-dark) 100%);
      color: #fff;
      padding: 100px 24px;
      text-align: center;
    }}
    .landing-hero h1 {{
      font-size: 3rem;
      font-weight: 700;
      margin-bottom: 20px;
      color: #fff;
    }}
    .landing-hero p {{
      font-size: 1.25rem;
      opacity: 0.9;
      max-width: 600px;
      margin: 0 auto 40px;
    }}
    .features-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 24px;
      margin-top: 60px;
    }}
    .feature-card {{
      background: #fff;
      border-radius: 16px;
      padding: 32px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.08);
      text-align: center;
    }}
    .feature-icon {{
      font-size: 3rem;
      margin-bottom: 20px;
    }}
    .feature-card h3 {{
      font-size: 1.25rem;
      margin-bottom: 12px;
      color: var(--sbs-blü);
    }}
    .feature-card p {{
      color: var(--sbs-muted);
      line-height: 1.6;
    }}
  </style>
</head>
<body>
  {SBS_HEADER}
  
  <main>
    <section class="landing-hero">
      <div class="hero-badge" style="margin: 0 auto 24px;">
        <span class="dot"></span>
        KI-VERTRAGSANALYSE
      </div>
      <h1>Verträge intelligent analysieren</h1>
      <p>Laden Sie Ihre Verträge hoch und unsere KI identifiziert Risiken, prüft Klauseln und liefert rechtliche Einschätzungen nach deutschem Recht.</p>
      <a href="/upload" class="btn btn-primary" style="font-size: 18px; padding: 18px 40px;">
        Jetzt Vertrag analysieren →
      </a>
    </section>
    
    <div class="container">
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">⚡</div>
          <h3>Schnelle Analyse</h3>
          <p>Vollständige Vertragsanalyse in unter 30 Sekunden. Extrahieren Sie alle relevanten Daten automatisch.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">⚖️</div>
          <h3>Deutsches Recht</h3>
          <p>Spezialisiert auf deutsche Verträge. Prüfung gegen BGB, HGB, ArbG und weitere relevante Gesetze.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🎯</div>
          <h3>Risikoerkennung</h3>
          <p>Automatische Identifikation kritischer Klauseln mit Risikobewertung und Handlungsempfehlungen.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3>8 Vertragstypen</h3>
          <p>Arbeits-, SaaS-, NDA-, Lieferanten-, Dienstleistungs-, Miet-, Kauf- und allgemeine Verträge.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🔒</div>
          <h3>DSGVO konform</h3>
          <p>Alle Daten werden in Deutschland verarbeitet und nach höchsten Sicherheitsstandards geschützt.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📤</div>
          <h3>Export & Reports</h3>
          <p>Exportieren Sie Analysen als JSON oder professionelle PDF-Reports für Ihre Dokumentation.</p>
        </div>
      </div>
      
      <div class="trust-bar" style="margin-top: 80px;">
        <div class="trust-item">
          <span class="icon">🇩🇪</span>
          Made in Germany
        </div>
        <div class="trust-item">
          <span class="icon">🔒</span>
          DSGVO konform
        </div>
        <div class="trust-item">
          <span class="icon">⚖️</span>
          Deutsches Recht
        </div>
        <div class="trust-item">
          <span class="icon">🤖</span>
          GPT-4o powered
        </div>
      </div>
    </div>
  </main>
  
  {SBS_FOOTER}
</body>
</html>'''


# =============================================================================
# HISTORY PAGE
# =============================================================================
def get_history_page():
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verlauf | SBS Contract Intelligence</title>
  <link rel="icon" href="/static/favicon.ico">
  {SBS_CSS}
  <style>
    .history-table {{
      width: 100%;
      background: #fff;
      border-radius: 16px;
      border-collapse: collapse;
      box-shadow: 0 4px 24px rgba(0,0,0,0.06);
      overflow: hidden;
    }}
    .history-table th,
    .history-table td {{
      padding: 16px 20px;
      text-align: left;
      border-bottom: 1px solid var(--sbs-border);
    }}
    .history-table th {{
      background: #f8fafc;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--sbs-muted);
    }}
    .history-table tr:hover {{
      background: rgba(0,56,86,0.02);
      cursor: pointer;
    }}
    .risk-dot {{
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      margin-right: 8px;
    }}
    .risk-dot.critical {{ background: var(--sbs-critical); }}
    .risk-dot.high {{ background: var(--sbs-high); }}
    .risk-dot.medium {{ background: var(--sbs-medium); }}
    .risk-dot.low {{ background: var(--sbs-low); }}
    .empty-state {{
      text-align: center;
      padding: 80px 40px;
      background: #fff;
      border-radius: 16px;
    }}
    .empty-state .icon {{
      font-size: 4rem;
      margin-bottom: 20px;
    }}
  </style>
</head>
<body>
  {SBS_HEADER}
  
  <main>
    <section class="hero">
      <div class="container">
        <div class="hero-badge">
          <span class="dot"></span>
          VERLAUF
        </div>
        <h1>Analysierte Verträge</h1>
        <p>Übersicht aller durchgeführten Vertragsanalysen.</p>
      </div>
    </section>
    
    <div class="container">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
        <h2 style="font-size: 1.25rem; color: var(--sbs-muted);">Letzte Analysen</h2>
        <a href="/upload" class="btn btn-primary">+ Neuer Vertrag</a>
      </div>
      
      <div id="historyContent">
        <div class="empty-state">
          <div class="icon">📋</div>
          <h3 style="margin-bottom: 12px;">Noch keine Verträge analysiert</h3>
          <p style="color: var(--sbs-muted); margin-bottom: 24px;">Laden Sie Ihren ersten Vertrag hoch um zu starten.</p>
          <a href="/upload" class="btn btn-primary">Vertrag hochladen →</a>
        </div>
      </div>
    </div>
  </main>
  
  {SBS_FOOTER}
  
  <script>
    document.getElementById('nav-history').classList.add('active');
    
    fetch('/api/v3/contracts?limit=50')
      .then(r => r.json())
      .then(data => {{
        if (data.items && data.items.length) {{
          let html = `
            <table class="history-table">
              <thead>
                <tr>
                  <th>Dateiname</th>
                  <th>Typ</th>
                  <th>Risiko</th>
                  <th>Datum</th>
                </tr>
              </thead>
              <tbody>
          `;
          
          data.items.forEach(item => {{
            const riskLevel = item.risk_level || 'low';
            html += `
              <tr onclick="window.location='/contracts/${{item.id}}'">
                <td>${{item.filename}}</td>
                <td>${{item.contract_type}}</td>
                <td>
                  <span class="risk-dot ${{riskLevel}}"></span>
                  ${{item.risk_score || '-'}}/100
                </td>
                <td>${{new Date(item.created_at).toLocaleDateString('de-DE')}}</td>
              </tr>
            `;
          }});
          
          html += '</tbody></table>';
          document.getElementById('historyContent').innerHTML = html;
        }}
      }})
      .catch(() => {{}});
  </script>
</body>
</html>'''


# =============================================================================
# ANALYTICS PAGE
# =============================================================================
def get_analytics_page():
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Analytics | SBS Contract Intelligence</title>
  <link rel="icon" href="/static/favicon.ico">
  {SBS_CSS}
  <style>
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-bottom: 40px;
    }}
    .kpi-card {{
      background: #fff;
      border-radius: 16px;
      padding: 28px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    }}
    .kpi-label {{
      font-size: 13px;
      color: var(--sbs-muted);
      margin-bottom: 8px;
    }}
    .kpi-value {{
      font-size: 2.5rem;
      font-weight: 700;
      color: var(--sbs-blü);
    }}
    .kpi-value.critical {{
      color: var(--sbs-critical);
    }}
    .kpi-value.success {{
      color: var(--sbs-success);
    }}
  </style>
</head>
<body>
  {SBS_HEADER}
  
  <main>
    <section class="hero">
      <div class="container">
        <div class="hero-badge">
          <span class="dot"></span>
          ANALYTICS
        </div>
        <h1>📊 Dashboard</h1>
        <p>Vertragsübersicht und Risikokennzahlen auf einen Blick.</p>
      </div>
    </section>
    
    <div class="container">
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">Verträge gesamt</div>
          <div class="kpi-value" id="kpiTotal">-</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Analysiert</div>
          <div class="kpi-value success" id="kpiAnalyzed">-</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Kritische Risiken</div>
          <div class="kpi-value critical" id="kpiCritical">-</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Ø Risiko-Score</div>
          <div class="kpi-value" id="kpiAvg">-</div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-body">
          <h3 style="margin-bottom: 24px; color: var(--sbs-muted);">Risikoverteilung</h3>
          <div id="chartPlaceholder" style="text-align: center; padding: 60px; color: var(--sbs-muted);">
            Laden Sie Verträge hoch um Statistiken zu sehen.
          </div>
        </div>
      </div>
    </div>
  </main>
  
  {SBS_FOOTER}
  
  <script>
    document.getElementById('nav-analytics').classList.add('active');
    
    fetch('/api/v3/dashboard/summary')
      .then(r => r.json())
      .then(data => {{
        document.getElementById('kpiTotal').textContent = data.total_contracts || 0;
        document.getElementById('kpiAnalyzed').textContent = data.active_contracts || 0;
        document.getElementById('kpiCritical').textContent = data.critical_risk_count || 0;
        document.getElementById('kpiAvg').textContent = data.avg_risk_score || 0;
      }})
      .catch(() => {{}});
  </script>
</body>
</html>'''


# =============================================================================
# HELP PAGE
# =============================================================================
def get_help_page():
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hilfe & FAQ | SBS Contract Intelligence</title>
  <link rel="icon" href="/static/favicon.ico">
  {SBS_CSS}
  <style>
    .faq-item {{
      background: #fff;
      border-radius: 12px;
      margin-bottom: 16px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.04);
      overflow: hidden;
    }}
    .faq-question {{
      padding: 20px 24px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .faq-question:hover {{
      background: rgba(0,56,86,0.02);
    }}
    .faq-answer {{
      padding: 0 24px;
      max-height: 0;
      overflow: hidden;
      transition: all 0.3s ease;
    }}
    .faq-item.open .faq-answer {{
      padding: 0 24px 24px;
      max-height: 500px;
    }}
    .faq-item.open .faq-arrow {{
      transform: rotate(180deg);
    }}
    .faq-arrow {{
      transition: transform 0.3s ease;
    }}
  </style>
</head>
<body>
  {SBS_HEADER}
  
  <main>
    <section class="hero">
      <div class="container">
        <div class="hero-badge">
          <span class="dot"></span>
          SUPPORT
        </div>
        <h1>Hilfe & FAQ</h1>
        <p>Antworten auf häufig gestellte Fragen zur Vertragsanalyse.</p>
      </div>
    </section>
    
    <div class="container">
      <div class="faq-item">
        <div class="faq-question" onclick="this.parentElement.classList.toggle('open')">
          <span>Welche Dateiformate werden unterstützt?</span>
          <span class="faq-arrow">▼</span>
        </div>
        <div class="faq-answer">
          <p style="color: var(--sbs-muted); line-height: 1.7;">Aktuell werden PDF-Dateien bis 10 MB unterstützt. DOCX-Support ist in Planung.</p>
        </div>
      </div>
      
      <div class="faq-item">
        <div class="faq-question" onclick="this.parentElement.classList.toggle('open')">
          <span>Wie lange dauert eine Analyse?</span>
          <span class="faq-arrow">▼</span>
        </div>
        <div class="faq-answer">
          <p style="color: var(--sbs-muted); line-height: 1.7;">Eine vollständige Vertragsanalyse dauert typischerweise 15-30 Sekunden, abhängig von der Dokumentlänge.</p>
        </div>
      </div>
      
      <div class="faq-item">
        <div class="faq-question" onclick="this.parentElement.classList.toggle('open')">
          <span>Welche Vertragstypen werden unterstützt?</span>
          <span class="faq-arrow">▼</span>
        </div>
        <div class="faq-answer">
          <p style="color: var(--sbs-muted); line-height: 1.7;">Wir unterstützen 8 Vertragstypen: Arbeitsverträge, SaaS-Verträge, NDAs, Lieferantenverträge, Dienstleistungsverträge, Mietverträge, Kaufverträge und allgemeine Verträge.</p>
        </div>
      </div>
      
      <div class="faq-item">
        <div class="faq-question" onclick="this.parentElement.classList.toggle('open')">
          <span>Sind meine Daten sicher?</span>
          <span class="faq-arrow">▼</span>
        </div>
        <div class="faq-answer">
          <p style="color: var(--sbs-muted); line-height: 1.7;">Ja, alle Daten werden DSGVO-konform in Deutschland verarbeitet und nach höchsten Sicherheitsstandards geschützt. Verträge werden nach der Analyse auf Wunsch gelöscht.</p>
        </div>
      </div>
      
      <div style="margin-top: 48px; text-align: center;">
        <h3 style="margin-bottom: 16px;">Noch Fragen?</h3>
        <p style="color: var(--sbs-muted); margin-bottom: 24px;">Kontaktieren Sie uns gerne per E-Mail.</p>
        <a href="mailto:info@sbsdeutschland.com" class="btn btn-primary">📧 Kontakt aufnehmen</a>
      </div>
    </div>
  </main>
  
  {SBS_FOOTER}
</body>
</html>'''


# =============================================================================
# EXPORT ALL PAGES
# =============================================================================
__all__ = [
    'SBS_CSS',
    'SBS_HEADER', 
    'SBS_FOOTER',
    'get_upload_page',
    'get_landing_page',
    'get_history_page',
    'get_analytics_page',
    'get_help_page'
]
