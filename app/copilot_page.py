"""Contract Copilot Page - Chat mit Verträgen"""

from .pages_enterprise import PAGE_CSS, get_header, get_footer

def get_copilot_page(user_name: str = "User"):
    """Generiert die Contract Copilot Seite"""
    
    header = get_header(user_name, "copilot")
    footer = get_footer()
    
    copilot_css = '''<style>
    .copilot-main { padding: 32px 24px 60px; background: #f1f5f9; min-height: calc(100vh - 200px); }
    .copilot-layout { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 320px; gap: 24px; }
    @media (max-width: 960px) { .copilot-layout { grid-template-columns: 1fr; } }
    .chat-card { background: white; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,56,86,0.1); overflow: hidden; display: flex; flex-direction: column; height: 600px; }
    .chat-header { background: linear-gradient(135deg, #003856, #004d73); color: white; padding: 20px 24px; display: flex; align-items: center; gap: 16px; }
    .chat-header-icon { width: 48px; height: 48px; background: rgba(255,255,255,0.15); border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 24px; }
    .chat-header-info h2 { margin: 0; font-size: 1.25rem; }
    .chat-header-info p { margin: 4px 0 0; font-size: 0.85rem; opacity: 0.85; }
    .chat-messages { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; background: #f8fafc; }
    .message { max-width: 85%; padding: 14px 18px; border-radius: 18px; line-height: 1.5; font-size: 0.95rem; }
    .message-user { align-self: flex-end; background: #003856; color: white; border-bottom-right-radius: 6px; }
    .message-assistant { align-self: flex-start; background: white; color: #1e293b; border: 1px solid #e2e8f0; border-bottom-left-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
    .message-typing { display: flex; gap: 6px; padding: 16px 20px; }
    .message-typing span { width: 8px; height: 8px; background: #94a3b8; border-radius: 50%; animation: typing 1.4s infinite; }
    .message-typing span:nth-child(2) { animation-delay: 0.2s; }
    .message-typing span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typing { 0%, 60%, 100% { transform: translateY(0); opacity: 0.4; } 30% { transform: translateY(-6px); opacity: 1; } }
    .chat-input-area { padding: 16px 20px; background: white; border-top: 1px solid #e2e8f0; }
    .chat-input-wrapper { display: flex; gap: 12px; align-items: flex-end; }
    .chat-input { flex: 1; padding: 14px 18px; border: 2px solid #e2e8f0; border-radius: 14px; font-size: 0.95rem; resize: none; min-height: 50px; max-height: 120px; font-family: inherit; }
    .chat-input:focus { outline: none; border-color: #003856; }
    .chat-send-btn { width: 50px; height: 50px; border: none; background: linear-gradient(135deg, #003856, #004d73); color: white; border-radius: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
    .chat-send-btn:hover { transform: scale(1.05); box-shadow: 0 4px 12px rgba(0,56,86,0.3); }
    .chat-send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .sidebar-card { background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); overflow: hidden; }
    .sidebar-header { padding: 16px 20px; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #1e293b; }
    .sidebar-content { padding: 12px; max-height: 250px; overflow-y: auto; }
    .contract-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 10px; cursor: pointer; border: 2px solid transparent; }
    .contract-item:hover { background: #f1f5f9; }
    .contract-item.selected { background: rgba(0,56,86,0.08); border-color: #003856; }
    .contract-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
    .contract-icon.low { background: #dcfce7; }
    .contract-icon.medium { background: #fef3c7; }
    .contract-icon.high { background: #fee2e2; }
    .contract-info { flex: 1; min-width: 0; }
    .contract-info strong { display: block; font-size: 0.85rem; color: #1e293b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .contract-info small { color: #64748b; font-size: 0.75rem; }
    .quick-actions { padding: 16px; display: flex; flex-direction: column; gap: 8px; }
    .quick-action { padding: 10px 14px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 0.85rem; color: #475569; cursor: pointer; text-align: left; }
    .quick-action:hover { background: #003856; color: white; border-color: #003856; }
    .welcome-message { text-align: center; padding: 60px 30px; color: #64748b; }
    .welcome-message h3 { color: #1e293b; margin-bottom: 12px; }
    .welcome-suggestions { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 24px; }
    .welcome-suggestion { padding: 10px 16px; background: white; border: 1px solid #e2e8f0; border-radius: 20px; font-size: 0.85rem; cursor: pointer; }
    .welcome-suggestion:hover { background: #003856; color: white; border-color: #003856; }
</style>'''
    
    html = '''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>Contract Copilot · SBS Vertragsanalyse</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link rel="icon" href="/static/favicon.ico">
''' + PAGE_CSS + copilot_css + '''
</head>
<body>
''' + header + '''
<div class="hero" style="padding:32px 24px;">
  <div class="container">
    <div class="hero-badge"><span class="dot" style="background:#22d3ee;box-shadow:0 0 12px rgba(34,211,238,0.6);"></span> CONTRACT COPILOT</div>
    <h1 style="font-size:2rem;margin:12px 0 8px;">🤖 Contract Copilot</h1>
    <p style="opacity:0.9;">Ihr KI-Assistent für Vertragsanalyse, Risikobewertung und rechtliche Fragen.</p>
  </div>
</div>

<div class="copilot-main">
  <div class="copilot-layout">
    <div class="chat-card">
      <div class="chat-header">
        <div class="chat-header-icon">🤖</div>
        <div class="chat-header-info">
          <h2>Contract Copilot</h2>
          <p>Powered by GPT-4 · Vertragsexperte</p>
        </div>
      </div>
      
      <div class="chat-messages" id="chatMessages">
        <div class="welcome-message">
          <h3>👋 Willkommen beim Contract Copilot!</h3>
          <p>Ich helfe bei Fragen zu Verträgen, analysiere Risiken und erkläre Klauseln.</p>
          <div class="welcome-suggestions">
            <div class="welcome-suggestion" onclick="askQuestion('Welche Verträge haben das höchste Risiko?')">🔴 Höchste Risiken?</div>
            <div class="welcome-suggestion" onclick="askQuestion('Fasse meine Verträge zusammen')">📋 Übersicht</div>
            <div class="welcome-suggestion" onclick="askQuestion('Welche Fristen laufen bald ab?')">⏰ Fristen</div>
            <div class="welcome-suggestion" onclick="askQuestion('Erkläre häufige Vertragsrisiken')">📚 Risiken</div>
          </div>
        </div>
      </div>
      
      <div class="chat-input-area">
        <div class="chat-input-wrapper">
          <textarea class="chat-input" id="chatInput" placeholder="Fragen Sie etwas über Ihre Verträge..." rows="1" onkeydown="handleKeyDown(event)"></textarea>
          <button class="chat-send-btn" id="sendBtn" onclick="sendMessage()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <div style="display:flex;flex-direction:column;gap:20px;">
      <div class="sidebar-card">
        <div class="sidebar-header">📄 Vertragskontext</div>
        <div class="sidebar-content" id="contractList">
          <div style="padding:20px;text-align:center;color:#64748b;">Laden...</div>
        </div>
      </div>
      
      <div class="sidebar-card">
        <div class="sidebar-header">⚡ Schnellaktionen</div>
        <div class="quick-actions">
          <button class="quick-action" onclick="askQuestion('Analysiere alle kritischen Risiken')">🔴 Kritische Risiken</button>
          <button class="quick-action" onclick="askQuestion('Welche Kündigungsfristen gibt es?')">📅 Kündigungsfristen</button>
          <button class="quick-action" onclick="askQuestion('Gibt es problematische Klauseln?')">⚠️ Problematische Klauseln</button>
          <button class="quick-action" onclick="askQuestion('Erstelle Handlungsempfehlung')">✅ Empfehlung</button>
        </div>
      </div>
    </div>
  </div>
</div>

''' + footer + '''
<script>
let selectedContractId = null;
let chatHistory = [];

async function loadContracts() {
  try {
    const res = await fetch('/api/copilot/contracts');
    const data = await res.json();
    const container = document.getElementById('contractList');
    if (data.contracts && data.contracts.length > 0) {
      container.innerHTML = data.contracts.map(function(c) {
        return '<div class="contract-item" onclick="selectContract(\\'' + c.id + '\\', this)"><div class="contract-icon ' + (c.risk_level || 'medium') + '">📄</div><div class="contract-info"><strong>' + c.filename + '</strong><small>' + c.type + '</small></div></div>';
      }).join('');
    } else {
      container.innerHTML = '<div style="padding:20px;text-align:center;color:#64748b;">Keine Verträge.<br><a href="/upload">Hochladen</a></div>';
    }
  } catch(e) { console.error(e); }
}

function selectContract(id, el) {
  document.querySelectorAll('.contract-item').forEach(function(i) { i.classList.remove('selected'); });
  if (selectedContractId === id) { selectedContractId = null; } 
  else { selectedContractId = id; el.classList.add('selected'); }
}

function handleKeyDown(e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }

function askQuestion(q) { document.getElementById('chatInput').value = q; sendMessage(); }

function addMessage(role, content) {
  var container = document.getElementById('chatMessages');
  var welcome = container.querySelector('.welcome-message');
  if (welcome) welcome.remove();
  var div = document.createElement('div');
  div.className = 'message message-' + role;
  div.innerHTML = content.replace(/\\n/g, '<br>');
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function showTyping() {
  var container = document.getElementById('chatMessages');
  var div = document.createElement('div');
  div.className = 'message message-assistant message-typing';
  div.id = 'typingIndicator';
  div.innerHTML = '<span></span><span></span><span></span>';
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function hideTyping() { var el = document.getElementById('typingIndicator'); if (el) el.remove(); }

async function sendMessage() {
  var input = document.getElementById('chatInput');
  var btn = document.getElementById('sendBtn');
  var message = input.value.trim();
  if (!message) return;
  
  input.value = ''; input.disabled = trü; btn.disabled = trü;
  addMessage('user', message);
  chatHistory.push({role: 'user', content: message});
  showTyping();
  
  try {
    var res = await fetch('/api/copilot/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ message: message, contract_id: selectedContractId, history: chatHistory.slice(-10) })
    });
    var data = await res.json();
    hideTyping();
    if (data.success) {
      addMessage('assistant', data.answer);
      chatHistory.push({role: 'assistant', content: data.answer});
    } else {
      addMessage('assistant', 'Fehler: ' + (data.error || 'Unbekannt'));
    }
  } catch(e) { hideTyping(); addMessage('assistant', 'Verbindungsfehler'); }
  
  input.disabled = false; btn.disabled = false; input.focus();
}

loadContracts();
</script>
</body>
</html>'''
    
    return html
