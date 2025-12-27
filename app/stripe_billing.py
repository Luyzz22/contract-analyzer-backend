"""
Stripe Billing Integration
- Checkout Sessions für Upgrades
- Webhook Handling
- Subscription Management
"""

import os
import stripe
from typing import Dict, Optional
from datetime import datetime

# Stripe Konfiguration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Produkt/Preis IDs (werden bei erster Verwendung erstellt)
PRICE_IDS = {
    "starter_monthly": None,
    "starter_yearly": None,
    "professional_monthly": None,
    "professional_yearly": None,
    "enterprise_monthly": None,
    "enterprise_yearly": None,
}

# Plan Preise in Cents
PLAN_PRICES = {
    "starter": {"monthly": 6900, "yearly": 69000},  # 69€/Monat, 690€/Jahr (2 Monate gratis)
    "professional": {"monthly": 17900, "yearly": 179000},  # 179€/Monat
    "enterprise": {"monthly": 44900, "yearly": 449000},  # 449€/Monat
}

def ensure_products_exist():
    """Erstellt Stripe Produkte und Preise falls nicht vorhanden"""
    global PRICE_IDS
    
    # Prüfe ob wir schon Preise haben
    try:
        prices = stripe.Price.list(limit=20, active=True)
        for price in prices.data:
            nickname = price.nickname
            if nickname and nickname in PRICE_IDS:
                PRICE_IDS[nickname] = price.id
        
        # Wenn alle Preise existieren, fertig
        if all(PRICE_IDS.values()):
            return PRICE_IDS
    except Exception as e:
        print(f"Stripe Preis-Check Fehler: {e}")
    
    # Erstelle Produkte falls nötig
    products = {}
    for plan_name in ["starter", "professional", "enterprise"]:
        try:
            # Suche existierendes Produkt
            existing = stripe.Product.search(query=f"name:'{plan_name.title()} Plan'")
            if existing.data:
                products[plan_name] = existing.data[0]
            else:
                # Erstelle neues Produkt
                products[plan_name] = stripe.Product.create(
                    name=f"{plan_name.title()} Plan",
                    description=f"SBS Vertragsanalyse {plan_name.title()} Plan",
                    metadata={"plan_id": plan_name}
                )
        except Exception as e:
            print(f"Produkt-Fehler {plan_name}: {e}")
    
    # Erstelle Preise
    for plan_name, prices in PLAN_PRICES.items():
        if plan_name not in products:
            continue
            
        product_id = products[plan_name].id
        
        for interval, amount in [("monthly", prices["monthly"]), ("yearly", prices["yearly"])]:
            nickname = f"{plan_name}_{interval}"
            if PRICE_IDS.get(nickname):
                continue
                
            try:
                price = stripe.Price.create(
                    product=product_id,
                    unit_amount=amount,
                    currency="eur",
                    recurring={"interval": "month" if interval == "monthly" else "year"},
                    nickname=nickname,
                    metadata={"plan_id": plan_name, "interval": interval}
                )
                PRICE_IDS[nickname] = price.id
                print(f" Preis erstellt: {nickname} = {price.id}")
            except Exception as e:
                print(f"Preis-Fehler {nickname}: {e}")
    
    return PRICE_IDS

def create_checkout_session(
    user_email: str,
    plan_id: str,
    interval: str = "monthly",
    success_url: str = None,
    cancel_url: str = None
) -> Dict:
    """Erstellt eine Stripe Checkout Session für Plan-Upgrade"""
    
    ensure_products_exist()
    
    price_key = f"{plan_id}_{interval}"
    price_id = PRICE_IDS.get(price_key)
    
    if not price_id:
        return {"success": False, "error": f"Unbekannter Plan: {price_key}"}
    
    try:
        # Kunde suchen oder erstellen
        customers = stripe.Customer.list(email=user_email, limit=1)
        if customers.data:
            customer_id = customers.data[0].id
        else:
            customer = stripe.Customer.create(
                email=user_email,
                metadata={"source": "contract_app"}
            )
            customer_id = customer.id
        
        # Checkout Session erstellen
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=success_url or "https://contract.sbsdeutschland.com/billing?success=true",
            cancel_url=cancel_url or "https://contract.sbsdeutschland.com/billing?canceled=true",
            metadata={
                "user_email": user_email,
                "plan_id": plan_id,
                "interval": interval
            },
            subscription_data={
                "metadata": {
                    "user_email": user_email,
                    "plan_id": plan_id
                }
            },
            allow_promotion_codes=True,
        )
        
        return {
            "success": True,
            "checkout_url": session.url,
            "session_id": session.id
        }
        
    except stripe.error.StripeError as e:
        return {"success": False, "error": str(e)}

def create_portal_session(user_email: str) -> Dict:
    """Erstellt eine Stripe Customer Portal Session für Self-Service"""
    try:
        customers = stripe.Customer.list(email=user_email, limit=1)
        if not customers.data:
            return {"success": False, "error": "Kein Stripe-Kunde gefunden"}
        
        session = stripe.billing_portal.Session.create(
            customer=customers.data[0].id,
            return_url="https://contract.sbsdeutschland.com/billing"
        )
        
        return {"success": True, "portal_url": session.url}
        
    except stripe.error.StripeError as e:
        return {"success": False, "error": str(e)}

def handle_webhook(payload: bytes, sig_header: str) -> Dict:
    """Verarbeitet Stripe Webhook Events"""
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError:
        return {"success": False, "error": "Invalid payload"}
    except stripe.error.SignatureVerificationError:
        return {"success": False, "error": "Invalid signature"}
    
    # Event verarbeiten
    event_type = event["type"]
    data = event["data"]["object"]
    
    print(f" Stripe Webhook: {event_type}")
    
    if event_type == "checkout.session.completed":
        return handle_checkout_completed(data)
    
    elif event_type == "customer.subscription.updated":
        return handle_subscription_updated(data)
    
    elif event_type == "customer.subscription.deleted":
        return handle_subscription_deleted(data)
    
    elif event_type == "invoice.paid":
        return handle_invoice_paid(data)
    
    elif event_type == "invoice.payment_failed":
        return handle_payment_failed(data)
    
    return {"success": True, "message": f"Event {event_type} ignored"}

def handle_checkout_completed(session: Dict) -> Dict:
    """Verarbeitet erfolgreichen Checkout"""
    from .usage_tracking import set_user_plan
    
    user_email = session.get("metadata", {}).get("user_email")
    plan_id = session.get("metadata", {}).get("plan_id")
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    
    if user_email and plan_id:
        set_user_plan(user_email, plan_id, customer_id, subscription_id)
        print(f" Plan aktiviert: {user_email} → {plan_id}")
        
        # Audit Log
        try:
            from .enterprise_features import log_audit
            log_audit(user_email, "subscription_upgrade", "billing", None, f"Upgrade auf {plan_id}", None, None)
        except:
            pass
        
        return {"success": True, "message": f"Plan {plan_id} für {user_email} aktiviert"}
    
    return {"success": False, "error": "Missing metadata"}

def handle_subscription_updated(subscription: Dict) -> Dict:
    """Verarbeitet Subscription-Änderungen"""
    from .usage_tracking import set_user_plan
    
    user_email = subscription.get("metadata", {}).get("user_email")
    plan_id = subscription.get("metadata", {}).get("plan_id")
    status = subscription.get("status")
    
    if user_email and status == "active":
        set_user_plan(user_email, plan_id, subscription.get("customer"), subscription.get("id"))
        print(f" Subscription aktualisiert: {user_email} → {plan_id}")
    
    return {"success": True}

def handle_subscription_deleted(subscription: Dict) -> Dict:
    """Verarbeitet Subscription-Kündigung"""
    from .usage_tracking import set_user_plan
    
    user_email = subscription.get("metadata", {}).get("user_email")
    
    if user_email:
        set_user_plan(user_email, "free")  # Zurück auf Free
        print(f" Subscription gekündigt: {user_email} → free")
        
        try:
            from .enterprise_features import log_audit
            log_audit(user_email, "subscription_canceled", "billing", None, "Abo gekündigt", None, None)
        except:
            pass
    
    return {"success": True}

def handle_invoice_paid(invoice: Dict) -> Dict:
    """Verarbeitet bezahlte Rechnung"""
    customer_email = invoice.get("customer_email")
    amount = invoice.get("amount_paid", 0) / 100
    print(f" Rechnung bezahlt: {customer_email} - €{amount:.2f}")
    return {"success": True}

def handle_payment_failed(invoice: Dict) -> Dict:
    """Verarbeitet fehlgeschlagene Zahlung"""
    customer_email = invoice.get("customer_email")
    print(f" Zahlung fehlgeschlagen: {customer_email}")
    # Hier könnte man eine E-Mail senden
    return {"success": True}

def get_subscription_status(user_email: str) -> Dict:
    """Holt den aktuellen Subscription-Status von Stripe"""
    try:
        customers = stripe.Customer.list(email=user_email, limit=1)
        if not customers.data:
            return {"has_subscription": False, "status": "none"}
        
        subscriptions = stripe.Subscription.list(
            customer=customers.data[0].id,
            status="active",
            limit=1
        )
        
        if subscriptions.data:
            sub = subscriptions.data[0]
            return {
                "has_subscription": True,
                "status": sub.status,
                "plan_id": sub.metadata.get("plan_id", "unknown"),
                "current_period_end": datetime.fromtimestamp(sub.current_period_end).isoformat(),
                "cancel_at_period_end": sub.cancel_at_period_end
            }
        
        return {"has_subscription": False, "status": "none"}
        
    except stripe.error.StripeError as e:
        return {"has_subscription": False, "status": "error", "error": str(e)}

print(" Stripe Billing Modul geladen")
