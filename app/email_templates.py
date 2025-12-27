"""
E-Mail Templates für SBS Vertragsanalyse
"""

TEMPLATES = {
    "welcome": {
        "subject": "Willkommen bei SBS Vertragsanalyse 🎉",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 40px 20px; }
        .header { background: linear-gradient(135deg, #003856, #004d73); color: white; padding: 40px; text-align: center; border-radius: 12px 12px 0 0; }
        .content { background: #f8fafc; padding: 40px; border-radius: 0 0 12px 12px; }
        .btn { display: inline-block; background: #003856; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; }
        .footer { text-align: center; padding: 20px; color: #64748b; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Willkommen bei SBS Vertragsanalyse!</h1>
        </div>
        <div class="content">
            <p>Hallo {name},</p>
            <p>vielen Dank für Ihre Registrierung! Ihr Konto ist jetzt aktiv und Sie können sofort loslegen.</p>
            
            <h3>🚀 Ihre nächsten Schritte:</h3>
            <ol>
                <li><strong>Ersten Vertrag hochladen</strong> - Testen Sie die KI-Analyse</li>
                <li><strong>Fristen-Alerts einrichten</strong> - Nie wieder Kündigungsfristen verpassen</li>
                <li><strong>Contract Copilot nutzen</strong> - Fragen Sie die KI zu Ihren Verträgen</li>
            </ol>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="https://contract.sbsdeutschland.com/upload" class="btn">Jetzt Vertrag analysieren →</a>
            </p>
            
            <p>Bei Fragen stehen wir Ihnen gerne zur Verfügung.</p>
            <p>Beste Grüße,<br>Ihr SBS Deutschland Team</p>
        </div>
        <div class="footer">
            <p>SBS Deutschland GmbH & Co. KG<br>In der Dell 19, 69469 Weinheim</p>
            <p><a href="https://sbsdeutschland.com/static/landing/datenschutz.html">Datenschutz</a> | <a href="https://sbsdeutschland.com/static/landing/impressum.html">Impressum</a></p>
        </div>
    </div>
</body>
</html>
"""
    },
    
    "subscription_confirmed": {
        "subject": "Ihre Buchung ist bestätigt ✅",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 40px 20px; }
        .header { background: linear-gradient(135deg, #003856, #004d73); color: white; padding: 40px; text-align: center; border-radius: 12px 12px 0 0; }
        .content { background: #f8fafc; padding: 40px; border-radius: 0 0 12px 12px; }
        .plan-box { background: white; border: 2px solid #003856; border-radius: 12px; padding: 24px; text-align: center; margin: 20px 0; }
        .btn { display: inline-block; background: #003856; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; }
        .footer { text-align: center; padding: 20px; color: #64748b; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Buchung bestätigt! 🎉</h1>
        </div>
        <div class="content">
            <p>Hallo {name},</p>
            <p>vielen Dank für Ihre Buchung! Ihr Upgrade wurde erfolgreich aktiviert.</p>
            
            <div class="plan-box">
                <h2 style="margin:0;color:#003856;">{plan_name}</h2>
                <p style="font-size:2rem;margin:10px 0;color:#003856;">{amount}€ / {interval}</p>
            </div>
            
            <h3>Ihre neuen Features:</h3>
            <ul>
                <li>✅ Erweiterte Vertragsanalyse</li>
                <li>✅ Mehr Copilot-Anfragen</li>
                <li>✅ Priority Support</li>
                <li>✅ Team-Funktionen</li>
            </ul>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="https://contract.sbsdeutschland.com/dashboard" class="btn">Zum Dashboard →</a>
            </p>
            
            <p>Beste Grüße,<br>Ihr SBS Deutschland Team</p>
        </div>
        <div class="footer">
            <p>SBS Deutschland GmbH & Co. KG<br>In der Dell 19, 69469 Weinheim</p>
        </div>
    </div>
</body>
</html>
"""
    },
    
    "deadline_reminder": {
        "subject": "⏰ Frist-Erinnerung: {contract_name}",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 40px 20px; }
        .alert-box { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .btn { display: inline-block; background: #003856; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⏰ Frist-Erinnerung</h1>
        
        <div class="alert-box">
            <strong>{contract_name}</strong><br>
            Frist: <strong>{deadline_date}</strong><br>
            Verbleibend: <strong>{days_remaining} Tage</strong>
        </div>
        
        <p>Handeln Sie jetzt, um diese Frist nicht zu verpassen.</p>
        
        <p style="margin: 30px 0;">
            <a href="https://contract.sbsdeutschland.com/contracts/{contract_id}" class="btn">Vertrag ansehen →</a>
        </p>
    </div>
</body>
</html>
"""
    }
}

def get_template(name: str) -> dict:
    return TEMPLATES.get(name, {})

def render_template(name: str, **kwargs) -> tuple:
    """Rendert Template mit Variablen, gibt (subject, html) zurück"""
    template = TEMPLATES.get(name)
    if not template:
        return None, None
    
    subject = template["subject"].format(**kwargs)
    html = template["html"].format(**kwargs)
    return subject, html
