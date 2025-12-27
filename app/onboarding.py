"""
Onboarding Flow für neü User
- Willkommens-Wizard
- Feature-Highlights
- Erster Vertrag Upload
"""

from .pages_enterprise import PAGE_CSS, get_header, get_footer

def get_onboarding_page(user_name: str = "User", user_email: str = None, step: int = 1):
    header = get_header(user_name, "")
    
    return '''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>Willkommen - SBS Vertragsanalyse</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
''' + PAGE_CSS + '''
<style>
.onboarding-container { min-height: 100vh; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); }
.onboarding-card { max-width: 700px; margin: 60px auto; background: white; border-radius: 24px; box-shadow: 0 20px 60px rgba(0,0,0,0.1); overflow: hidden; }
.onboarding-header { background: linear-gradient(135deg, #003856, #004d73); color: white; padding: 40px; text-align: center; }
.onboarding-header h1 { margin: 0 0 8px; font-size: 2rem; }
.onboarding-header p { margin: 0; opacity: 0.9; }
.onboarding-body { padding: 40px; }
.step-indicator { display: flex; justify-content: center; gap: 12px; margin-bottom: 32px; }
.step-dot { width: 12px; height: 12px; border-radius: 50%; background: #e2e8f0; transition: all 0.3s; }
.step-dot.active { background: #003856; transform: scale(1.2); }
.step-dot.completed { background: #10b981; }
.step-content { display: none; animation: fadeIn 0.3s ease; }
.step-content.active { display: block; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.feature-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 24px 0; }
.feature-card { background: #f8fafc; border-radius: 16px; padding: 24px; text-align: center; border: 2px solid transparent; cursor: pointer; transition: all 0.2s; }
.feature-card:hover { border-color: #003856; transform: translateY(-2px); }
.feature-card.selected { border-color: #003856; background: #eff6ff; }
.feature-icon { font-size: 2.5rem; margin-bottom: 12px; }
.feature-title { font-weight: 600; color: #1e293b; margin-bottom: 4px; }
.feature-desc { font-size: 0.85rem; color: #64748b; }

.upload-zone { border: 3px dashed #cbd5e1; border-radius: 16px; padding: 48px; text-align: center; cursor: pointer; transition: all 0.2s; background: #f8fafc; }
.upload-zone:hover { border-color: #003856; background: #eff6ff; }
.upload-zone.dragover { border-color: #FFB900; background: #fffbeb; }
.upload-icon { font-size: 3rem; margin-bottom: 16px; }
.upload-text { color: #64748b; }
.upload-text strong { color: #1e293b; display: block; font-size: 1.1rem; margin-bottom: 4px; }

.btn-row { display: flex; gap: 12px; justify-content: space-between; margin-top: 32px; }
.btn { padding: 14px 28px; border-radius: 12px; font-size: 1rem; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; }
.btn-primary { background: linear-gradient(135deg, #003856, #004d73); color: white; }
.btn-primary:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(0,56,86,0.3); }
.btn-secondary { background: #f1f5f9; color: #475569; }
.btn-secondary:hover { background: #e2e8f0; }
.btn-skip { background: transparent; color: #94a3b8; }

.checklist { text-align: left; margin: 24px 0; }
.checklist-item { display: flex; align-items: center; gap: 12px; padding: 16px; background: #f8fafc; border-radius: 12px; margin-bottom: 12px; }
.checklist-item input { width: 20px; height: 20px; accent-color: #003856; }
.checklist-item label { flex: 1; color: #1e293b; }
.checklist-item small { color: #64748b; display: block; font-size: 0.85rem; }

.success-animation { text-align: center; padding: 40px 0; }
.success-icon { font-size: 5rem; margin-bottom: 24px; animation: bounce 0.5s ease; }
@keyframes bounce { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
.confetti { position: fixed; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; z-index: 1000; }
</style>
</head>
<body>
<div class="onboarding-container">
  <div class="onboarding-card">
    <div class="onboarding-header">
      <h1>Willkommen bei SBS Vertragsanalyse</h1>
      <p>Lassen Sie uns Ihr Konto in wenigen Schritten einrichten</p>
    </div>
    
    <div class="onboarding-body">
      <div class="step-indicator">
        <span class="step-dot active" data-step="1"></span>
        <span class="step-dot" data-step="2"></span>
        <span class="step-dot" data-step="3"></span>
        <span class="step-dot" data-step="4"></span>
      </div>
      
      <!-- Step 1: Begruessung -->
      <div id="step1" class="step-content active">
        <h2 style="text-align:center;margin-bottom:16px;">Hallo ''' + user_name + '''!</h2>
        <p style="text-align:center;color:#64748b;margin-bottom:32px;">
          Wir freuen uns, Sie an Bord zu haben. In nur 3 Minuten richten wir Ihr Konto ein.
        </p>
        
        <div class="feature-grid">
          <div class="feature-card" onclick="selectFeature(this, 'analysis')">
            <div class="feature-icon">📄</div>
            <div class="feature-title">Vertragsanalyse</div>
            <div class="feature-desc">KI analysiert Ihre Vertraege automatisch</div>
          </div>
          <div class="feature-card" onclick="selectFeature(this, 'deadlines')">
            <div class="feature-icon">⏰</div>
            <div class="feature-title">Fristen-Alerts</div>
            <div class="feature-desc">Nie wieder eine Kündigungsfrist verpassen</div>
          </div>
          <div class="feature-card" onclick="selectFeature(this, 'copilot')">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">Contract Copilot</div>
            <div class="feature-desc">Fragen Sie die KI zu Ihren Vertraegen</div>
          </div>
          <div class="feature-card" onclick="selectFeature(this, 'export')">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Export & Reports</div>
            <div class="feature-desc">Excel, PDF und detaillierte Berichte</div>
          </div>
        </div>
        
        <div class="btn-row">
          <span></span>
          <button class="btn btn-primary" onclick="nextStep()">Weiter</button>
        </div>
      </div>
      
      <!-- Step 2: Ersten Vertrag hochladen -->
      <div id="step2" class="step-content">
        <h2 style="text-align:center;margin-bottom:8px;">Laden Sie Ihren ersten Vertrag hoch</h2>
        <p style="text-align:center;color:#64748b;margin-bottom:24px;">
          Testen Sie die KI-Analyse mit einem echten Vertrag
        </p>
        
        <div class="upload-zone" id="uploadZone" onclick="document.getElementById('fileInput').click()">
          <div class="upload-icon">📎</div>
          <div class="upload-text">
            <strong>Vertrag hier ablegen</strong>
            oder klicken zum Auswählen (PDF, max. 20MB)
          </div>
          <input type="file" id="fileInput" accept=".pdf" style="display:none" onchange="handleFile(this)">
        </div>
        <p id="fileName" style="text-align:center;margin-top:12px;color:#10b981;display:none;"></p>
        
        <div class="btn-row">
          <button class="btn btn-secondary" onclick="prevStep()">Zurück</button>
          <div>
            <button class="btn btn-skip" onclick="nextStep()">Überspringen</button>
            <button class="btn btn-primary" id="analyzeBtn" onclick="analyzeContract()" disabled>Analysieren</button>
          </div>
        </div>
      </div>
      
      <!-- Step 3: Einstellungen -->
      <div id="step3" class="step-content">
        <h2 style="text-align:center;margin-bottom:8px;">Personalisieren Sie Ihre Erfahrung</h2>
        <p style="text-align:center;color:#64748b;margin-bottom:24px;">
          Wählen Sie, welche Benachrichtigungen Sie erhalten möchten
        </p>
        
        <div class="checklist">
          <div class="checklist-item">
            <input type="checkbox" id="notifyDeadlines" checked>
            <label for="notifyDeadlines">
              Fristen-Erinnerungen
              <small>30, 14, 7 und 1 Tag vor Ablauf</small>
            </label>
          </div>
          <div class="checklist-item">
            <input type="checkbox" id="notifyWeekly" checked>
            <label for="notifyWeekly">
              Woechentliche Zusammenfassung
              <small>Überblick ueber anstehende Fristen</small>
            </label>
          </div>
          <div class="checklist-item">
            <input type="checkbox" id="notifyRisks">
            <label for="notifyRisks">
              Risiko-Warnungen
              <small>Bei kritischen Vertragsklauseln</small>
            </label>
          </div>
          <div class="checklist-item">
            <input type="checkbox" id="enable2FA">
            <label for="enable2FA">
              2FA aktivieren
              <small>Zusaetzliche Sicherheit für Ihr Konto</small>
            </label>
          </div>
        </div>
        
        <div class="btn-row">
          <button class="btn btn-secondary" onclick="prevStep()">Zurück</button>
          <button class="btn btn-primary" onclick="saveSettings()">Einstellungen speichern</button>
        </div>
      </div>
      
      <!-- Step 4: Fertig -->
      <div id="step4" class="step-content">
        <div class="success-animation">
          <div class="success-icon">🎉</div>
          <h2>Alles eingerichtet!</h2>
          <p style="color:#64748b;margin:16px 0 32px;">
            Ihr Konto ist bereit. Entdecken Sie jetzt alle Funktionen.
          </p>
          
          <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:16px;max-width:400px;margin:0 auto;">
            <a href="/upload" class="btn btn-primary" style="text-decoration:none;text-align:center;">Vertrag hochladen</a>
            <a href="/dashboard" class="btn btn-secondary" style="text-decoration:none;text-align:center;">Zum Dashboard</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
let currentStep = 1;
let selectedFile = null;
const totalSteps = 4;

function updateStepIndicator() {
  document.querySelectorAll('.step-dot').forEach((dot, i) => {
    dot.classList.remove('active', 'completed');
    if (i + 1 < currentStep) dot.classList.add('completed');
    if (i + 1 === currentStep) dot.classList.add('active');
  });
}

function showStep(step) {
  document.querySelectorAll('.step-content').forEach(el => el.classList.remove('active'));
  document.getElementById('step' + step).classList.add('active');
  currentStep = step;
  updateStepIndicator();
  
  if (step === 4) {
    // Confetti effect
    createConfetti();
    // Mark onboarding complete
    fetch('/api/onboarding/complete', { method: 'POST' });
  }
}

function nextStep() {
  if (currentStep < totalSteps) showStep(currentStep + 1);
}

function prevStep() {
  if (currentStep > 1) showStep(currentStep - 1);
}

function selectFeature(el, feature) {
  el.classList.toggle('selected');
}

function handleFile(input) {
  if (input.files && input.files[0]) {
    selectedFile = input.files[0];
    document.getElementById('fileName').textContent = selectedFile.name;
    document.getElementById('fileName').style.display = 'block';
    document.getElementById('analyzeBtn').disabled = false;
  }
}

async function analyzeContract() {
  if (!selectedFile) return;
  
  const btn = document.getElementById('analyzeBtn');
  btn.disabled = true;
  btn.textContent = 'Analysiere...';
  
  const formData = new FormData();
  formData.append('file', selectedFile);
  
  try {
    const res = await fetch('/api/v3/contracts/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    
    if (data.contract_id) {
      btn.textContent = 'Erfolgreich!';
      setTimeout(() => nextStep(), 1000);
    } else {
      throw new Error(data.error || 'Upload fehlgeschlagen');
    }
  } catch (e) {
    alert('Fehler: ' + e.message);
    btn.disabled = false;
    btn.textContent = 'Analysieren';
  }
}

async function saveSettings() {
  const settings = {
    notify_deadlines: document.getElementById('notifyDeadlines').checked,
    notify_weekly: document.getElementById('notifyWeekly').checked,
    notify_risks: document.getElementById('notifyRisks').checked,
    enable_2fa: document.getElementById('enable2FA').checked
  };
  
  try {
    await fetch('/api/settings/notifications', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    });
    
    if (settings.enable_2fa) {
      // Redirect to 2FA setup after onboarding
      sessionStorage.setItem('setup2fa', 'true');
    }
    
    nextStep();
  } catch (e) {
    console.error(e);
    nextStep();
  }
}

function createConfetti() {
  const colors = ['#003856', '#FFB900', '#10b981', '#f59e0b', '#ec4899'];
  for (let i = 0; i < 50; i++) {
    const confetti = document.createElement('div');
    confetti.style.cssText = `
      position: fixed;
      width: 10px;
      height: 10px;
      background: \${colors[Math.floor(Math.random() * colors.length)]};
      left: \${Math.random() * 100}%;
      top: -10px;
      border-radius: 50%;
      animation: fall \${2 + Math.random() * 2}s linear forwards;
      z-index: 1000;
    `;
    document.body.appendChild(confetti);
    setTimeout(() => confetti.remove(), 4000);
  }
  
  const style = document.createElement('style');
  style.textContent = '@keyframes fall { to { top: 100vh; transform: rotate(720deg); } }';
  document.head.appendChild(style);
}

// Drag & Drop
const uploadZone = document.getElementById('uploadZone');
uploadZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadZone.classList.add('dragover');
});
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
uploadZone.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadZone.classList.remove('dragover');
  if (e.dataTransfer.files[0]) {
    document.getElementById('fileInput').files = e.dataTransfer.files;
    handleFile(document.getElementById('fileInput'));
  }
});

// Check if should setup 2FA
if (sessionStorage.getItem('setup2fa')) {
  sessionStorage.removeItem('setup2fa');
  // Could auto-redirect to /security
}
</script>
</body>
</html>'''
