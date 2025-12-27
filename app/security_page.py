"""Security Settings Page mit 2FA Setup"""

from .pages_enterprise import PAGE_CSS, get_header, get_footer

def get_security_page(user_name: str = "User", user_email: str = None):
    header = get_header(user_name, "settings")
    footer = get_footer()
    
    return '''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>Sicherheit - SBS Vertragsanalyse</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
''' + PAGE_CSS + '''
<style>
.security-container { max-width: 800px; margin: 0 auto; padding: 40px 24px; }
.security-card { background: white; border-radius: 16px; padding: 32px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
.security-card h3 { margin: 0 0 8px; color: #1e293b; display: flex; align-items: center; gap: 12px; }
.security-card p { color: #64748b; margin: 0 0 24px; }
.status-badge { padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
.status-enabled { background: #dcfce7; color: #166534; }
.status-disabled { background: #fee2e2; color: #991b1b; }
.btn-2fa { padding: 12px 24px; border: none; border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-enable { background: linear-gradient(135deg, #003856, #004d73); color: white; }
.btn-enable:hover { transform: scale(1.02); }
.btn-disable { background: #fee2e2; color: #991b1b; }
.btn-disable:hover { background: #fecaca; }
.setup-modal { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; align-items: center; justify-content: center; }
.setup-modal.active { display: flex; }
.modal-content { background: white; border-radius: 20px; padding: 40px; max-width: 450px; width: 90%; text-align: center; }
.modal-content h2 { margin: 0 0 16px; color: #1e293b; }
.modal-content p { color: #64748b; margin-bottom: 24px; }
.qr-code { margin: 24px auto; padding: 16px; background: white; border-radius: 12px; display: inline-block; border: 2px solid #e2e8f0; }
.qr-code img { max-width: 200px; }
.secret-code { font-family: monospace; background: #f1f5f9; padding: 12px 20px; border-radius: 8px; font-size: 1.1rem; letter-spacing: 2px; margin: 16px 0; word-break: break-all; }
.code-input { width: 100%; padding: 16px; font-size: 1.5rem; text-align: center; letter-spacing: 8px; border: 2px solid #e2e8f0; border-radius: 12px; margin: 16px 0; }
.code-input:focus { outline: none; border-color: #003856; }
.backup-codes { background: #fffbeb; border: 2px solid #fbbf24; border-radius: 12px; padding: 20px; margin: 20px 0; text-align: left; }
.backup-codes h4 { margin: 0 0 12px; color: #92400e; }
.backup-codes ul { margin: 0; padding-left: 0; list-style: none; display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.backup-codes li { font-family: monospace; background: white; padding: 8px 12px; border-radius: 6px; font-size: 0.95rem; }
.modal-actions { display: flex; gap: 12px; justify-content: center; margin-top: 24px; }
.btn-secondary { background: #f1f5f9; color: #475569; padding: 12px 24px; border: none; border-radius: 10px; cursor: pointer; }
.step-indicator { display: flex; justify-content: center; gap: 8px; margin-bottom: 24px; }
.step { width: 10px; height: 10px; border-radius: 50%; background: #e2e8f0; }
.step.active { background: #003856; }
.attempts-list { margin-top: 16px; }
.attempt-item { display: flex; justify-content: space-between; padding: 12px; border-bottom: 1px solid #f1f5f9; }
.attempt-success { color: #166534; }
.attempt-failed { color: #991b1b; }
</style>
</head>
<body>
''' + header + '''

<div class="hero" style="padding:40px 24px;">
  <div class="container" style="text-align:center;">
    <h1 style="font-size:2rem;margin:12px 0;">Sicherheitseinstellungen</h1>
    <p style="opacity:0.9;">Schuetzen Sie Ihr Konto mit Zwei-Faktor-Authentifizierung</p>
  </div>
</div>

<div class="security-container">
  <div class="security-card">
    <div style="display:flex;justify-content:space-between;align-items:start;">
      <div>
        <h3>Zwei-Faktor-Authentifizierung (2FA)</h3>
        <p>Zusaetzliche Sicherheitsebene fuer Ihr Konto mit TOTP-App (Google Authenticator, Authy, etc.)</p>
      </div>
      <span id="2faStatus" class="status-badge status-disabled">Deaktiviert</span>
    </div>
    <div id="2faActions">
      <button class="btn-2fa btn-enable" onclick="start2FASetup()">2FA aktivieren</button>
    </div>
    <div id="2faInfo" style="display:none;margin-top:20px;padding-top:20px;border-top:1px solid #e2e8f0;">
      <p style="margin:0;"><strong>Aktiviert seit:</strong> <span id="enabledAt">-</span></p>
      <p style="margin:8px 0 0;"><strong>Backup-Codes verbleibend:</strong> <span id="backupCount">-</span></p>
    </div>
  </div>

  <div class="security-card">
    <h3>Letzte Anmeldeversuche</h3>
    <p>Ueberpruefen Sie verdaechtige Aktivitaeten</p>
    <div id="attemptsList" class="attempts-list">
      <p style="color:#94a3b8;text-align:center;">Keine Daten verfuegbar</p>
    </div>
  </div>
  
  <div class="security-card">
    <h3>Passwort aendern</h3>
    <p>Aendern Sie regelmaessig Ihr Passwort fuer maximale Sicherheit</p>
    <button class="btn-2fa btn-secondary" onclick="alert('SSO-Passwort wird ueber Google verwaltet')">Passwort aendern</button>
  </div>
</div>

<!-- Setup Modal -->
<div id="setupModal" class="setup-modal">
  <div class="modal-content">
    <!-- Step 1: QR Code -->
    <div id="step1" class="setup-step">
      <div class="step-indicator"><span class="step active"></span><span class="step"></span><span class="step"></span></div>
      <h2>2FA einrichten</h2>
      <p>Scannen Sie den QR-Code mit Ihrer Authenticator-App</p>
      <div class="qr-code"><img id="qrCodeImg" src="" alt="QR Code"></div>
      <p style="font-size:0.85rem;color:#64748b;">Oder geben Sie diesen Code manuell ein:</p>
      <div class="secret-code" id="secretCode">XXXX XXXX XXXX XXXX</div>
      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeModal()">Abbrechen</button>
        <button class="btn-2fa btn-enable" onclick="showStep(2)">Weiter</button>
      </div>
    </div>
    
    <!-- Step 2: Verify -->
    <div id="step2" class="setup-step" style="display:none;">
      <div class="step-indicator"><span class="step"></span><span class="step active"></span><span class="step"></span></div>
      <h2>Code bestaetigen</h2>
      <p>Geben Sie den 6-stelligen Code aus Ihrer App ein</p>
      <input type="text" id="verifyCode" class="code-input" maxlength="6" placeholder="000000" autocomplete="off">
      <p id="verifyError" style="color:#991b1b;display:none;">Ungueltiger Code</p>
      <div class="modal-actions">
        <button class="btn-secondary" onclick="showStep(1)">Zurueck</button>
        <button class="btn-2fa btn-enable" onclick="verify2FA()">Bestaetigen</button>
      </div>
    </div>
    
    <!-- Step 3: Backup Codes -->
    <div id="step3" class="setup-step" style="display:none;">
      <div class="step-indicator"><span class="step"></span><span class="step"></span><span class="step active"></span></div>
      <h2>Backup-Codes sichern</h2>
      <p>Speichern Sie diese Codes an einem sicheren Ort. Sie koennen sie verwenden, falls Sie keinen Zugriff auf Ihre App haben.</p>
      <div class="backup-codes">
        <h4>Ihre Backup-Codes:</h4>
        <ul id="backupCodesList"></ul>
      </div>
      <div class="modal-actions">
        <button class="btn-2fa btn-enable" onclick="finish2FASetup()">Fertig</button>
      </div>
    </div>
  </div>
</div>

<!-- Disable Modal -->
<div id="disableModal" class="setup-modal">
  <div class="modal-content">
    <h2>2FA deaktivieren</h2>
    <p>Geben Sie Ihren aktuellen 2FA-Code ein, um die Zwei-Faktor-Authentifizierung zu deaktivieren.</p>
    <input type="text" id="disableCode" class="code-input" maxlength="6" placeholder="000000" autocomplete="off">
    <p id="disableError" style="color:#991b1b;display:none;">Ungueltiger Code</p>
    <div class="modal-actions">
      <button class="btn-secondary" onclick="closeDisableModal()">Abbrechen</button>
      <button class="btn-2fa btn-disable" onclick="disable2FA()">Deaktivieren</button>
    </div>
  </div>
</div>

''' + footer + '''

<script>
let currentSecret = '';

async function load2FAStatus() {
  try {
    const res = await fetch('/api/2fa/status');
    const data = await res.json();
    
    const statusEl = document.getElementById('2faStatus');
    const actionsEl = document.getElementById('2faActions');
    const infoEl = document.getElementById('2faInfo');
    
    if (data.enabled) {
      statusEl.textContent = 'Aktiviert';
      statusEl.className = 'status-badge status-enabled';
      actionsEl.innerHTML = '<button class="btn-2fa btn-disable" onclick="showDisableModal()">2FA deaktivieren</button>';
      infoEl.style.display = 'block';
      document.getElementById('enabledAt').textContent = data.enabled_at ? new Date(data.enabled_at).toLocaleDateString('de-DE') : '-';
      document.getElementById('backupCount').textContent = data.backup_codes_remaining || '0';
    } else {
      statusEl.textContent = 'Deaktiviert';
      statusEl.className = 'status-badge status-disabled';
      actionsEl.innerHTML = '<button class="btn-2fa btn-enable" onclick="start2FASetup()">2FA aktivieren</button>';
      infoEl.style.display = 'none';
    }
  } catch (e) {
    console.error('Status error:', e);
  }
}

async function start2FASetup() {
  try {
    const res = await fetch('/api/2fa/setup', { method: 'POST' });
    const data = await res.json();
    
    if (data.error) {
      alert(data.error);
      return;
    }
    
    currentSecret = data.secret;
    document.getElementById('qrCodeImg').src = data.qr_code;
    document.getElementById('secretCode').textContent = data.secret.match(/.{1,4}/g).join(' ');
    document.getElementById('setupModal').classList.add('active');
    showStep(1);
  } catch (e) {
    alert('Fehler beim Setup: ' + e.message);
  }
}

function showStep(step) {
  document.querySelectorAll('.setup-step').forEach(el => el.style.display = 'none');
  document.getElementById('step' + step).style.display = 'block';
  if (step === 2) {
    document.getElementById('verifyCode').value = '';
    document.getElementById('verifyCode').focus();
  }
}

async function verify2FA() {
  const code = document.getElementById('verifyCode').value;
  if (code.length !== 6) {
    document.getElementById('verifyError').style.display = 'block';
    return;
  }
  
  try {
    const res = await fetch('/api/2fa/enable', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: code })
    });
    const data = await res.json();
    
    if (data.success) {
      document.getElementById('verifyError').style.display = 'none';
      const list = document.getElementById('backupCodesList');
      list.innerHTML = data.backup_codes.map(c => '<li>' + c + '</li>').join('');
      showStep(3);
    } else {
      document.getElementById('verifyError').textContent = data.error || 'Ungueltiger Code';
      document.getElementById('verifyError').style.display = 'block';
    }
  } catch (e) {
    alert('Fehler: ' + e.message);
  }
}

function finish2FASetup() {
  closeModal();
  load2FAStatus();
}

function closeModal() {
  document.getElementById('setupModal').classList.remove('active');
}

function showDisableModal() {
  document.getElementById('disableCode').value = '';
  document.getElementById('disableError').style.display = 'none';
  document.getElementById('disableModal').classList.add('active');
}

function closeDisableModal() {
  document.getElementById('disableModal').classList.remove('active');
}

async function disable2FA() {
  const code = document.getElementById('disableCode').value;
  if (code.length !== 6) {
    document.getElementById('disableError').style.display = 'block';
    return;
  }
  
  try {
    const res = await fetch('/api/2fa/disable', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: code })
    });
    const data = await res.json();
    
    if (data.success) {
      closeDisableModal();
      load2FAStatus();
    } else {
      document.getElementById('disableError').textContent = data.error || 'Ungueltiger Code';
      document.getElementById('disableError').style.display = 'block';
    }
  } catch (e) {
    alert('Fehler: ' + e.message);
  }
}

// Init
load2FAStatus();
</script>
</body>
</html>'''
