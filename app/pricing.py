"""SBS Contract Intelligence - Pricing & Usage Management"""

from enum import Enum
from typing import Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel
import hashlib

class PricingTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class TierLimits:
    """Limits pro Tier"""
    LIMITS = {
        PricingTier.FREE: {
            "analyses_per_month": 3,
            "contract_types": ["employment"],
            "pdf_export": False,
            "api_access": False,
            "clause_chat": False,
            "price_eur": 0,
        },
        PricingTier.PRO: {
            "analyses_per_month": 50,
            "contract_types": ["employment", "saas", "nda", "vendor"],
            "pdf_export": True,
            "api_access": False,
            "clause_chat": True,
            "price_eur": 49,
        },
        PricingTier.ENTERPRISE: {
            "analyses_per_month": -1,  # Unlimited
            "contract_types": ["employment", "saas", "nda", "vendor", "lease", "service", "msa"],
            "pdf_export": True,
            "api_access": True,
            "clause_chat": True,
            "clause_library": True,
            "contract_comparison": True,
            "price_eur": 299,
        },
    }
    
    @classmethod
    def get_limits(cls, tier: PricingTier) -> dict:
        return cls.LIMITS.get(tier, cls.LIMITS[PricingTier.FREE])


class UsageTracker:
    """Tracks usage per session/user"""
    
    def __init__(self):
        self._usage: Dict[str, dict] = {}
    
    def _get_session_key(self, identifier: str) -> str:
        """Generate consistent session key"""
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    
    def _get_month_key(self) -> str:
        """Current month as key"""
        return datetime.now().strftime("%Y-%m")
    
    def get_usage(self, identifier: str) -> dict:
        """Get usage for identifier"""
        key = self._get_session_key(identifier)
        month = self._get_month_key()
        
        if key not in self._usage:
            self._usage[key] = {}
        
        if month not in self._usage[key]:
            self._usage[key][month] = {
                "analyses": 0,
                "tier": PricingTier.FREE,
                "first_use": datetime.now().isoformat(),
            }
        
        return self._usage[key][month]
    
    def increment_usage(self, identifier: str) -> dict:
        """Increment analysis count"""
        usage = self.get_usage(identifier)
        usage["analyses"] += 1
        usage["last_use"] = datetime.now().isoformat()
        return usage
    
    def can_analyze(self, identifier: str) -> tuple[bool, str]:
        """Check if user can perform analysis"""
        usage = self.get_usage(identifier)
        tier = usage.get("tier", PricingTier.FREE)
        limits = TierLimits.get_limits(tier)
        
        max_analyses = limits["analyses_per_month"]
        current = usage["analyses"]
        
        if max_analyses == -1:  # Unlimited
            return True, "unlimited"
        
        if current >= max_analyses:
            return False, f"Limit erreicht ({current}/{max_analyses}). Upgrade auf Pro für mehr Analysen."
        
        remaining = max_analyses - current
        return True, f"{remaining} Analysen verbleibend"
    
    def set_tier(self, identifier: str, tier: PricingTier):
        """Set user tier (for upgrades)"""
        usage = self.get_usage(identifier)
        usage["tier"] = tier
    
    def get_tier(self, identifier: str) -> PricingTier:
        """Get user tier"""
        usage = self.get_usage(identifier)
        return usage.get("tier", PricingTier.FREE)


# Global tracker instance
usage_tracker = UsageTracker()


class PricingInfo(BaseModel):
    """Pricing information for display"""
    tier: str
    analyses_used: int
    analyses_limit: int
    analyses_remaining: int
    can_analyze: bool
    features: dict
    upgrade_url: Optional[str] = None
