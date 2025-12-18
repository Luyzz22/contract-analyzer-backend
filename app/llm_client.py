# app/llm_client.py
"""
LLM-Client für Contract Analyzer.
Unterstützt alle 8 Vertragstypen mit spezifischen Prompts.
"""

import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Custom Exception für LLM-Fehler."""
    pass


def call_llm_analysis(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Ruft das LLM für Vertragsanalyse auf.
    
    Args:
        system_prompt: Der System-Prompt für den Vertragstyp
        user_prompt: Der User-Prompt mit dem Vertragstext
    
    Returns:
        Dict mit Analyse-Ergebnis
    
    Raises:
        LLMError: Bei Fehlern in der API-Kommunikation
    """
    dummy_mode = os.getenv("CONTRACT_ANALYZER_DUMMY", "true").lower() == "true"
    
    if dummy_mode:
        logger.info("Dummy mode: Returning mock analysis")
        return _get_dummy_response()
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=4000,
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # JSON extrahieren
        result = _parse_llm_response(result_text)
        
        logger.info(f"LLM analysis completed: {len(result.get('risk_flags', []))} risks found")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        raise LLMError(f"Invalid JSON response from LLM: {e}")
    except Exception as e:
        logger.error(f"LLM API error: {e}")
        raise LLMError(f"LLM API call failed: {e}")


def _parse_llm_response(response_text: str) -> Dict[str, Any]:
    """Parst die LLM-Antwort und extrahiert JSON."""
    # Entferne Markdown-Backticks falls vorhanden
    if "```" in response_text:
        parts = response_text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{") and part.endswith("}"):
                response_text = part
                break
    
    return json.loads(response_text)


def _get_dummy_response() -> Dict[str, Any]:
    """Gibt eine Dummy-Antwort für Test-Modus zurück."""
    return {
        "summary": "Dummy-Analyse: Vertrag wurde im Test-Modus verarbeitet.",
        "extracted_fields": {},
        "risk_flags": [],
        "overall_risk_level": "low",
        "overall_risk_score": 25
    }


# ============================================================================
# TYPEN-SPEZIFISCHE WRAPPER (Kompatibilität mit bestehendem Code)
# ============================================================================

def call_employment_contract_model(user_prompt: str) -> Dict[str, Any]:
    """Analysiert Arbeitsvertrag."""
    from .prompts import EMPLOYMENT_CONTRACT_SYSTEM_PROMPT
    return call_llm_analysis(EMPLOYMENT_CONTRACT_SYSTEM_PROMPT, user_prompt)


def call_saas_contract_model(user_prompt: str) -> Dict[str, Any]:
    """Analysiert SaaS-Vertrag."""
    from .prompts import SAAS_CONTRACT_SYSTEM_PROMPT
    return call_llm_analysis(SAAS_CONTRACT_SYSTEM_PROMPT, user_prompt)


def call_nda_contract_model(user_prompt: str) -> Dict[str, Any]:
    """Analysiert NDA."""
    from .prompts import NDA_CONTRACT_SYSTEM_PROMPT
    return call_llm_analysis(NDA_CONTRACT_SYSTEM_PROMPT, user_prompt)


def call_vendor_contract_model(user_prompt: str) -> Dict[str, Any]:
    """Analysiert Lieferantenvertrag."""
    from .prompts import VENDOR_CONTRACT_SYSTEM_PROMPT
    return call_llm_analysis(VENDOR_CONTRACT_SYSTEM_PROMPT, user_prompt)


def call_service_contract_model(user_prompt: str) -> Dict[str, Any]:
    """Analysiert Dienstleistungsvertrag."""
    from .prompts import SERVICE_CONTRACT_SYSTEM_PROMPT
    return call_llm_analysis(SERVICE_CONTRACT_SYSTEM_PROMPT, user_prompt)


def call_rental_contract_model(user_prompt: str) -> Dict[str, Any]:
    """Analysiert Mietvertrag."""
    from .prompts import RENTAL_CONTRACT_SYSTEM_PROMPT
    return call_llm_analysis(RENTAL_CONTRACT_SYSTEM_PROMPT, user_prompt)


def call_purchase_contract_model(user_prompt: str) -> Dict[str, Any]:
    """Analysiert Kaufvertrag."""
    from .prompts import PURCHASE_CONTRACT_SYSTEM_PROMPT
    return call_llm_analysis(PURCHASE_CONTRACT_SYSTEM_PROMPT, user_prompt)


def call_general_contract_model(user_prompt: str) -> Dict[str, Any]:
    """Analysiert allgemeinen Vertrag."""
    from .prompts import GENERAL_CONTRACT_SYSTEM_PROMPT
    return call_llm_analysis(GENERAL_CONTRACT_SYSTEM_PROMPT, user_prompt)


# Mapping für einfachen Zugriff
MODEL_FUNCTIONS = {
    "employment": call_employment_contract_model,
    "saas": call_saas_contract_model,
    "nda": call_nda_contract_model,
    "vendor": call_vendor_contract_model,
    "service": call_service_contract_model,
    "rental": call_rental_contract_model,
    "purchase": call_purchase_contract_model,
    "general": call_general_contract_model,
}


def analyze_contract(contract_type: str, contract_text: str) -> Dict[str, Any]:
    """
    Universelle Analyse-Funktion für alle Vertragstypen.
    
    Args:
        contract_type: employment, saas, nda, vendor, service, rental, purchase, general
        contract_text: Der zu analysierende Vertragstext
    
    Returns:
        Dict mit Analyse-Ergebnis
    """
    from .prompts import get_prompt_for_type
    
    # Fallback auf general
    if contract_type not in MODEL_FUNCTIONS:
        contract_type = "general"
    
    system_prompt, user_prompt = get_prompt_for_type(contract_type, contract_text)
    return call_llm_analysis(system_prompt, user_prompt)
