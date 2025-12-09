# app/llm_client.py
"""LLM-Client für Contract Analyzer."""

import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LLMError(Exception):
    """Custom Exception für LLM-Fehler."""
    pass

def call_employment_contract_model(user_prompt: str) -> Dict[str, Any]:
    """Ruft LLM für Employment-Analyse auf."""
    dummy_mode = os.getenv("CONTRACT_ANALYZER_DUMMY", "true").lower() == "true"
    
    if dummy_mode:
        logger.info("Dummy mode: Returning mock employment analysis")
        return {
            "summary": "Befristeter Arbeitsvertrag für Junior Legal Assistant mit 6 Monaten Probezeit, 40 Wochenstunden und 3.200 EUR Gehalt.",
            "extracted_fields": {
                "parties": [{"name": "Musterfirma GmbH", "role": "employer"}, {"name": "Max Mustermann", "role": "employee"}],
                "start_date": "2026-02-01", "fixed_term": True, "end_date": "2027-01-31",
                "probation_period_months": 6.0, "weekly_hours": 40.0, "base_salary_eur": 3200.0,
                "vacation_days_per_year": 28,
                "notice_period_employee": "2 Wochen in der Probezeit, danach gesetzlich",
                "notice_period_employer": "2 Wochen in der Probezeit, danach gesetzlich",
                "non_compete_during_term": True, "post_contract_non_compete": False
            },
            "risk_flags": [{
                "severity": "medium", "title": "Überstundenabgeltung",
                "description": "Pauschale Überstundenabgeltung kann arbeitsrechtliche Risiken bergen.",
                "clause_snippet": "Mit der vorstehenden Vergütung sind etwaige Überstunden grundsätzlich abgegolten.",
                "policy_reference": "Arbeitszeit/Überstunden-Policy"
            }]
        }
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Du bist ein Arbeitsrechtsexperte. Antworte nur mit validem JSON."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
        )
        content = response.choices[0].message.content.strip()
        for marker in ["```json", "```"]:
            if content.startswith(marker):
                content = content[len(marker):]
                break
        if content.endswith("```"):
            content = content[:-3]
        return json.loads(content.strip())
    except Exception as e:
        logger.error(f"OpenAI call failed: {e}")
        raise LLMError(f"LLM call failed: {e}")

def call_saas_contract_model(user_prompt: str) -> Dict[str, Any]:
    """Ruft LLM für SaaS-Analyse auf."""
    dummy_mode = os.getenv("CONTRACT_ANALYZER_DUMMY", "true").lower() == "true"
    
    if dummy_mode:
        logger.info("Dummy mode: Returning mock SaaS analysis")
        return {
            "summary": "B2B-SaaS-Vertrag mit 12 Monaten Mindestlaufzeit, Auto-Renewal und 10.000 EUR ACV.",
            "extracted_fields": {
                "customer_name": "Beispiel GmbH", "vendor_name": "SaaS Provider AG",
                "contract_start_date": "2026-01-01", "contract_end_date": "2026-12-31",
                "auto_renew": True, "renewal_notice_days": 30.0,
                "annual_contract_value_eur": 10000.0, "billing_interval": "monthly",
                "min_term_months": 12.0, "termination_for_convenience": False,
                "data_location": "EU", "dp_addendum_included": True,
                "liability_cap_multiple_acv": 1.0, "uptime_sla_percent": 99.5
            },
            "risk_flags": []
        }
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Du bist ein SaaS-Vertragsexperte. Antworte nur mit validem JSON."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
        )
        content = response.choices[0].message.content.strip()
        for marker in ["```json", "```"]:
            if content.startswith(marker):
                content = content[len(marker):]
                break
        if content.endswith("```"):
            content = content[:-3]
        return json.loads(content.strip())
    except Exception as e:
        logger.error(f"OpenAI call failed: {e}")
        raise LLMError(f"LLM call failed: {e}")
