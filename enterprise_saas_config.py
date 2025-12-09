# enterprise_saas_config.py
"""
Enterprise SaaS Contract Standards Configuration
Based on Apple, Nvidia, SAP, and Fortune 500 vendor requirements
"""

ENTERPRISE_SAAS_STANDARDS = {
    "vendor_tiers": {
        "tier_1": {
            "name": "Strategic Vendor",
            "acv_threshold": 100000,  # EUR
            "requires_approval": ["CFO", "CISO", "General Counsel"],
            "audit_frequency": "quarterly"
        },
        "tier_2": {
            "name": "Enterprise Vendor",
            "acv_threshold": 50000,
            "requires_approval": ["Procurement", "IT Director"],
            "audit_frequency": "annual"
        },
        "tier_3": {
            "name": "Standard Vendor",
            "acv_threshold": 10000,
            "requires_approval": ["Procurement"],
            "audit_frequency": "biennial"
        }
    },
    
    "financial_terms": {
        "annual_contract_value": {
            "min_threshold": 50000,  # EUR
            "billing_intervals": ["annual", "quarterly"],
            "preferred": "annual_with_termination_rights",
            "prohibited": ["monthly_without_exit_clause"]
        },
        "price_protection": {
            "cpi_adjustment_max": 0.03,  # 3% max annual increase
            "requires_approval": True,
            "lock_in_period": 24  # months
        },
        "payment_terms": {
            "standard": "Net 30",
            "preferred": "Net 45",
            "early_payment_discount": 0.02  # 2% for early payment
        }
    },
    
    "sla_requirements": {
        "uptime": {
            "minimum": 0.995,  # 99.5%
            "target": 0.999,   # 99.9%
            "measurement": "monthly_average",
            "credits": {
                "below_999": 0.10,  # 10% service credit
                "below_995": 0.25,  # 25% service credit
                "below_99": 0.50    # 50% service credit + termination right
            }
        },
        "support": {
            "response_time": {
                "critical": "1 hour",
                "high": "4 hours",
                "medium": "24 hours"
            },
            "availability": "24/7/365"
        },
        "performance": {
            "api_response_time_p99": 200,  # milliseconds
            "data_export_speed": "1GB/hour minimum"
        }
    },
    
    "data_protection": {
        "location": {
            "primary": "EU",
            "backup": "EU-only",
            "prohibited": ["US", "CN", "RU"]
        },
        "dp_addendum": {
            "required": True,
            "standard": "EU SCCs 2021",
            "subprocessors": {
                "notification_required": True,
                "approval_right": True,
                "max_count": 5
            }
        },
        "retention": {
            "data_deletion": "90 days after termination",
            "backup_deletion": "180 days",
            "audit_trail_retention": "7 years"
        }
    },
    
    "liability_and_indemnification": {
        "cap": {
            "multiple_of_acv": 1.0,  # 1x ACV
            "max_cap_eur": 1000000,
            "exceptions": ["IP infringement", "gross negligence", "data breach"]
        },
        "insurance": {
            "cyber_min": 5000000,  # EUR
            "general_liability_min": 10000000,
            "proof_required": True
        },
        "indemnification": {
            "third_party_claims": True,
            "intellectual_property": True,
            "cap_exceptions": ["willful misconduct"]
        }
    },
    
    "vendor_lock_in_prevention": {
        "data_portability": {
            "standard_format": ["CSV", "JSON", "XML"],
            "export_time": "30 days after request",
            "cost": "no_charge",
            "api_access": "read_only_during_notice_period"
        },
        "termination_rights": {
            "for_convenience": True,
            "notice_period_days": 90,
            "pro_rata_refund": True,
            "data_return": "30 days after termination"
        },
        "interoperability": {
            "open_apis": True,
            "documentation": "publicly_available",
            "change_notification": "90 days"
        }
    },
    
    "compliance": {
        "certifications": [
            "ISO 27001",
            "SOC 2 Type II",
            "GDPR compliant",
            "BDSG compliant"
        ],
        "audit_rights": {
            "frequency": "annual",
            "notice_period_days": 30,
            "cost_coverage": "vendor",
            "scope": "unlimited"
        },
        "penetration_testing": {
            "allowed": True,
            "notification_required": True,
            "frequency": "annual"
        }
    },
    
    "risk_flags": {
        "high_severity": [
            {
                "title": "Auto-Renewal ohne Kündigungsrecht",
                "description": "Vertrag verlängert sich automatisch ohne vorherige Kündigungsmöglichkeit – führt zu ungeplanten Kosten und Lock-in.",
                "policy_reference": "Vendor Management Policy §4.2"
            },
            {
                "title": "Haftungscap > 1x ACV",
                "description": "Haftungsobergrenze überschreitet 1-fachen Jahresvertragswert – erhöht finanzielles Risiko bei Schadensfällen.",
                "policy_reference": "Risk Management Framework §7.1"
            },
            {
                "title": "Datenlokation außerhalb EU",
                "description": "Verarbeitung oder Speicherung außerhalb der EU ohne ausreichende Garantien – DSGVO-Risiko.",
                "policy_reference": "Data Protection Policy §3.4"
            },
            {
                "title": "Kein Data-Export-Recht",
                "description": "Fehlende vertragliche Garantie für Datenrückgabe bei Kündigung – Vendor Lock-in Risiko.",
                "policy_reference": "Vendor Lock-in Prevention §2.1"
            }
        ],
        "medium_severity": [
            {
                "title": "Kündigungsfrist > 90 Tage",
                "description": "Kündigungsfrist überschreitet internes Limit von 90 Tagen – verlängert Exit-Horizont.",
                "policy_reference": "Contract Governance Policy §5.3"
            },
            {
                "title": "SLA < 99.9% ohne Credits",
                "description": "Verfügbarkeitsgarantie unter 99.9% ohne automatische Service Credits – erhöht Betriebsrisiko.",
                "policy_reference": "SLA Standards §2.2"
            },
            {
                "title": "Preisanpassung ohne Cap",
                "description": "Jährliche Preiserhöhung ohne festes Maximum – Budgetplanung unsicher.",
                "policy_reference": "Financial Risk Management §4.5"
            }
        ],
        "low_severity": [
            {
                "title": "Support nur Email",
                "description": "Kein telefonischer oder Chat-Support verfügbar – könnte bei Incidents zu Verzögerungen führen.",
                "policy_reference": "Support Standards §1.1"
            },
            {
                "title": "Dokumentation nur auf Englisch",
                "description": "Keine deutsche Dokumentation verfügbar – erhöht Onboarding-Aufwand für deutsche Teams.",
                "policy_reference": "Language Requirements §2.1"
            }
        ]
    }
}

# Compliance Matrix für verschiedene Vendor-Typen
VENDOR_COMPLIANCE_MATRIX = {
    "apple_standard": {
        "required": ["SOC 2 Type II", "ISO 27001", "Penetration Testing"],
        "data_location": "EU-only",
        "liability_cap": 1.0,
        "audit_rights": "annual_unlimited"
    },
    "nvidia_standard": {
        "required": ["SOC 2 Type II", "GDPR compliant", "Cyber Insurance 10M"],
        "data_location": "EU or US (with SCCs)",
        "liability_cap": 1.5,
        "audit_rights": "quarterly"
    },
    "sap_standard": {
        "required": ["ISO 27001", "BDSG compliant", "German data centers"],
        "data_location": "Germany-only",
        "liability_cap": 1.0,
        "audit_rights": "annual"
    }
}

