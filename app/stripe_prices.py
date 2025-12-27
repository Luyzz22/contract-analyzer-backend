"""
Stripe Price IDs - Production
Erstellt am: 2025-12-27
"""

STRIPE_PRICES = {
    "starter": {
        "monthly": "price_1Sj6QwDVswNSUYHMVozcIHKI",
        "yearly": "price_1Sj6QxDVswNSUYHMfQXeZRgr",
        "name": "Starter",
        "monthly_amount": 69,
        "yearly_amount": 690
    },
    "professional": {
        "monthly": "price_1Sj6QxDVswNSUYHMlIqtJeL7",
        "yearly": "price_1Sj6QyDVswNSUYHMEkO4FW6e",
        "name": "Professional",
        "monthly_amount": 179,
        "yearly_amount": 1790
    },
    "enterprise": {
        "monthly": "price_1Sj6QyDVswNSUYHMdf7jhW7L",
        "yearly": "price_1Sj6QyDVswNSUYHMnVvcLUvo",
        "name": "Enterprise",
        "monthly_amount": 449,
        "yearly_amount": 4490
    }
}

def get_price_id(plan: str, interval: str = "monthly") -> str:
    """Holt Price ID für Plan und Interval"""
    plan = plan.lower()
    if plan not in STRIPE_PRICES:
        raise ValueError(f"Unknown plan: {plan}")
    return STRIPE_PRICES[plan][interval]

def get_all_prices():
    """Gibt alle Preise zurück"""
    return STRIPE_PRICES
