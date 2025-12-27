"""Pricing/Upgrade Seite mit Stripe Integration"""

from .pages_enterprise import PAGE_CSS, get_header, get_footer

def get_pricing_page(user_name: str = "User", user_email: str = None, current_plan: str = "free"):
    header = get_header(user_name, "billing")
    footer = get_footer()
    
    def plan_button(plan_id, is_current):
        if is_current:
            return '<button class="plan-btn current" disabled>Aktueller Plan</button>'
        elif plan_id == "enterprise":
            return '<a href="mailto:info@sbsdeutschland.com?subject=Enterprise%20Anfrage" class="plan-btn contact">Kontakt aufnehmen</a>'
        else:
            return f'<button class="plan-btn upgrade" onclick="checkout(\'{plan_id}\')">Jetzt upgraden</button>'
    
    free_btn = plan_button('free', current_plan == 'free')
    starter_btn = plan_button('starter', current_plan == 'starter')
    pro_btn = plan_button('professional', current_plan == 'professional')
    ent_btn = plan_button('enterprise', current_plan == 'enterprise')
    
    free_class = 'current' if current_plan == 'free' else ''
    starter_class = 'current' if current_plan == 'starter' else ''
    pro_class = 'popular ' + ('current' if current_plan == 'professional' else '')
    ent_class = 'current' if current_plan == 'enterprise' else ''

    return '''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>Preise - SBS Vertragsanalyse</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    ''' + PAGE_CSS + '''
    .pricing-container { max-width: 1200px; margin: 0 auto; padding: 40px 24px; }
    .pricing-toggle { display: flex; justify-content: center; gap: 12px; margin-bottom: 40px; align-items: center; }
    .pricing-toggle label { color: #64748b; }
    .toggle-switch { position: relative; width: 56px; height: 28px; background: #e2e8f0; border-radius: 20px; cursor: pointer; }
    .toggle-switch::after { content: ""; position: absolute; top: 3px; left: 3px; width: 22px; height: 22px; background: white; border-radius: 50%; transition: transform 0.3s; }
    input:checked + .toggle-switch { background: #003856; }
    input:checked + .toggle-switch::after { transform: translateX(28px); }
    .save-badge { background: #10b981; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; }
    .pricing-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
    @media (max-width: 900px) { .pricing-grid { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 600px) { .pricing-grid { grid-template-columns: 1fr; } }
    .pricing-card { background: white; border-radius: 20px; padding: 32px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 2px solid transparent; position: relative; }
    .pricing-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0,0,0,0.12); }
    .pricing-card.popular { border-color: #003856; }
    .pricing-card.current { border-color: #10b981; }
    .plan-name { font-size: 1.25rem; font-weight: 700; color: #1e293b; margin-bottom: 8px; }
    .plan-desc { color: #64748b; font-size: 0.9rem; margin-bottom: 24px; }
    .plan-price .amount { font-size: 2.5rem; font-weight: 700; color: #003856; }
    .plan-price .period { color: #64748b; }
    .plan-features { list-style: none; padding: 0; margin: 24px 0; }
    .plan-features li { padding: 8px 0; color: #475569; font-size: 0.9rem; }
    .plan-btn { display: block; width: 100%; padding: 14px; border: none; border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer; text-align: center; text-decoration: none; }
    .plan-btn.upgrade { background: linear-gradient(135deg, #003856, #004d73); color: white; }
    .plan-btn.current { background: #e2e8f0; color: #64748b; }
    .plan-btn.contact { background: #f8fafc; color: #003856; border: 2px solid #003856; }
  </style>
</head>
<body>
''' + header + '''
<div class="hero" style="padding:40px 24px;text-align:center;">
  <div class="container">
    <h1 style="font-size:2.2rem;margin:12px 0;">Waehlen Sie Ihren Plan</h1>
    <p style="opacity:0.9;">Starten Sie kostenlos und upgraden Sie bei Bedarf.</p>
  </div>
</div>
<div class="pricing-container">
  <div class="pricing-toggle">
    <label>Monatlich</label>
    <input type="checkbox" id="yearlyToggle" style="display:none" onchange="toggleYearly()">
    <label class="toggle-switch" for="yearlyToggle"></label>
    <label>Jaehrlich</label>
    <span class="save-badge">2 Monate gratis</span>
  </div>
  <div class="pricing-grid">
    <div class="pricing-card ''' + free_class + '''">
      <div class="plan-name">Free</div>
      <div class="plan-desc">Fuer den Einstieg</div>
      <div class="plan-price"><span class="amount">0 EUR</span><span class="period"> / Monat</span></div>
      <ul class="plan-features">
        <li>5 Analysen/Monat</li>
        <li>20 Copilot-Anfragen</li>
        <li>10 Vertraege</li>
        <li>E-Mail Support</li>
      </ul>
      ''' + free_btn + '''
    </div>
    <div class="pricing-card ''' + starter_class + '''">
      <div class="plan-name">Starter</div>
      <div class="plan-desc">Fuer wachsende Teams</div>
      <div class="plan-price"><span class="amount">69 EUR</span><span class="period"> / Monat</span></div>
      <ul class="plan-features">
        <li>50 Analysen/Monat</li>
        <li>200 Copilot-Anfragen</li>
        <li>100 Vertraege</li>
        <li>3 Teammitglieder</li>
        <li>Fristen-Alerts</li>
      </ul>
      ''' + starter_btn + '''
    </div>
    <div class="pricing-card ''' + pro_class + '''">
      <div class="plan-name">Professional</div>
      <div class="plan-desc">Fuer professionelle Teams</div>
      <div class="plan-price"><span class="amount">179 EUR</span><span class="period"> / Monat</span></div>
      <ul class="plan-features">
        <li>200 Analysen/Monat</li>
        <li>1.000 Copilot-Anfragen</li>
        <li>500 Vertraege</li>
        <li>10 Teammitglieder</li>
        <li>API-Zugang</li>
        <li>Audit-Log</li>
      </ul>
      ''' + pro_btn + '''
    </div>
    <div class="pricing-card ''' + ent_class + '''">
      <div class="plan-name">Enterprise</div>
      <div class="plan-desc">Fuer grosse Organisationen</div>
      <div class="plan-price"><span class="amount">449 EUR</span><span class="period"> / Monat</span></div>
      <ul class="plan-features">
        <li>Unbegrenzte Analysen</li>
        <li>Unbegrenzt Copilot</li>
        <li>Unbegrenzte Vertraege</li>
        <li>Unbegrenzte User</li>
        <li>SSO / SAML</li>
        <li>Dedicated Support</li>
      </ul>
      ''' + ent_btn + '''
    </div>
  </div>
</div>
''' + footer + '''
<script>
var isYearly = false;
function toggleYearly() { isYearly = !isYearly; }
function checkout(planId) {
  var btn = event.target;
  btn.disabled = true;
  btn.textContent = 'Laden...';
  fetch('/api/billing/checkout', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({plan_id: planId, interval: isYearly ? 'yearly' : 'monthly'})
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.success && data.checkout_url) {
      window.location.href = data.checkout_url;
    } else {
      alert('Fehler: ' + (data.error || 'Checkout fehlgeschlagen'));
      btn.disabled = false;
      btn.textContent = 'Jetzt upgraden';
    }
  });
}
</script>
</body>
</html>'''
