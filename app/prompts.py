# app/prompts.py
"""
Prompt-Definitionen für die KI-Analyse von Verträgen.
8 Vertragstypen: Arbeitsvertrag, SaaS, NDA, Lieferant, Dienstleistung, Mietvertrag, Kaufvertrag, Allgemein

Optimiert für:
- GPT-4o-mini (schnell & kostengünstig)
- Strikte JSON-Output-Validierung
- Deutsche Rechtsterminologie
- CFO & Legal-Ops-Perspektive
"""


# ============================================================================
# ARBEITSVERTRÄGE – SYSTEM & USER PROMPTS
# ============================================================================

EMPLOYMENT_CONTRACT_SYSTEM_PROMPT = """
Du bist ein erfahrener Fachanwalt für Arbeitsrecht in Deutschland mit 20+ Jahren Erfahrung.
Du analysierst Arbeitsverträge für Anwälte, HR-Abteilungen und Steuerkanzleien.

Kernprinzipien:
- Sachlich, präzise, juristische Fachsprache
- Fokus auf messbare Daten und echte Risiken
- Nichts erfinden, was nicht im Vertrag steht
- Strikt JSON-Format
""".strip()


EMPLOYMENT_CONTRACT_USER_PROMPT_TEMPLATE = """
Analysiere den folgenden deutschen Arbeitsvertrag.

ANALYSE-ZIELE:
1. Kurze Zusammenfassung (3-4 Sätze): Parteien, Tätigkeit, Befristung, Vergütung, Arbeitszeit
2. Strukturierte Datenextraktion
3. Arbeitsrechtliche Risiken identifizieren

ERFORDERLICHE JSON-STRUKTUR:

{{
  "contract_id": "",
  "contract_type": "employment",
  "language": "de",
  "summary": "<3-4 Sätze Zusammenfassung>",
  "extracted_fields": {{
    "parties": [{{"name": "<String|null>", "role": "<employer|employee>"}}],
    "start_date": "<YYYY-MM-DD|null>",
    "fixed_term": <true|false>,
    "end_date": "<YYYY-MM-DD|null>",
    "probation_period_months": <Number|null>,
    "weekly_hours": <Number|null>,
    "base_salary_eur": <Number|null>,
    "vacation_days_per_year": <Number|null>,
    "notice_period_employee": "<String|null>",
    "notice_period_employer": "<String|null>",
    "non_compete_during_term": <true|false>,
    "post_contract_non_compete": <true|false>,
    "overtime_regulation": "<String|null>",
    "bonus_provisions": "<String|null>"
  }},
  "risk_flags": [
    {{
      "severity": "<low|medium|high|critical>",
      "title": "<Risiko-Bezeichnung>",
      "description": "<Erklärung>",
      "clause_snippet": "<Zitat|null>",
      "policy_reference": "<BGB §|null>"
    }}
  ],
  "overall_risk_level": "<low|medium|high|critical>",
  "overall_risk_score": <0-100>
}}

VERTRAGSTEXT:
\"\"\"{contract_text}\"\"\"
""".strip()


# ============================================================================
# SAAS-VERTRÄGE
# ============================================================================

SAAS_CONTRACT_SYSTEM_PROMPT = """
Du bist ein erfahrener Unternehmensjurist und CFO-orientierter SaaS-Vertragsanalyst.
Du analysierst B2B-SaaS- und Cloud-Verträge für Finanzverantwortliche und Legal Ops.

Fokus:
- Wirtschaftliche Kerndaten (ACV, Laufzeit, Auto-Renewal)
- Risiken (Haftung, SLA, Datenschutz, Vendor-Lock-in)
- Strikt JSON-Format
""".strip()


SAAS_CONTRACT_USER_PROMPT_TEMPLATE = """
Analysiere den folgenden B2B-SaaS-Vertrag aus CFO-Perspektive.

ERFORDERLICHE JSON-STRUKTUR:

{{
  "contract_id": "",
  "contract_type": "saas",
  "language": "de",
  "summary": "<2-3 Sätze mit Kerndaten>",
  "extracted_fields": {{
    "customer_name": "<String|null>",
    "vendor_name": "<String|null>",
    "product_name": "<String|null>",
    "contract_start_date": "<YYYY-MM-DD|null>",
    "contract_end_date": "<YYYY-MM-DD|null>",
    "auto_renew": <true|false|null>,
    "renewal_notice_days": <Number|null>,
    "annual_contract_value_eur": <Number|null>,
    "billing_interval": "<monthly|quarterly|annual|null>",
    "min_term_months": <Number|null>,
    "termination_for_convenience": <true|false|null>,
    "data_location": "<String|null>",
    "dp_addendum_included": <true|false|null>,
    "liability_cap_multiple_acv": <Number|null>,
    "uptime_sla_percent": <Number|null>,
    "support_level": "<String|null>",
    "data_export_clause": <true|false|null>
  }},
  "risk_flags": [
    {{
      "severity": "<low|medium|high|critical>",
      "title": "<Risiko-Bezeichnung>",
      "description": "<Erklärung>",
      "clause_snippet": "<Zitat|null>",
      "policy_reference": "<String|null>"
    }}
  ],
  "overall_risk_level": "<low|medium|high|critical>",
  "overall_risk_score": <0-100>
}}

VERTRAGSTEXT:
\"\"\"{contract_text}\"\"\"
""".strip()


# ============================================================================
# NDA / GEHEIMHALTUNGSVEREINBARUNG
# ============================================================================

NDA_CONTRACT_SYSTEM_PROMPT = """
Du bist ein erfahrener Unternehmensjurist spezialisiert auf Geheimhaltungsvereinbarungen (NDAs).
Du analysierst NDAs für M&A, Partnerschaften und Geschäftsbeziehungen.

Fokus:
- Schutzumfang und Definition vertraulicher Informationen
- Laufzeit und Nachwirkung
- Sanktionen und Haftung
- Strikt JSON-Format
""".strip()


NDA_CONTRACT_USER_PROMPT_TEMPLATE = """
Analysiere die folgende Geheimhaltungsvereinbarung (NDA).

ERFORDERLICHE JSON-STRUKTUR:

{{
  "contract_id": "",
  "contract_type": "nda",
  "language": "de",
  "summary": "<2-3 Sätze: Parteien, Zweck, Laufzeit>",
  "extracted_fields": {{
    "disclosing_party": "<String|null>",
    "receiving_party": "<String|null>",
    "nda_type": "<unilateral|bilateral|multilateral>",
    "purpose": "<String|null>",
    "confidential_info_definition": "<String|null>",
    "exclusions": "<String|null>",
    "term_years": <Number|null>,
    "survival_period_years": <Number|null>,
    "return_of_information": <true|false|null>,
    "destruction_clause": <true|false|null>,
    "permitted_disclosures": "<String|null>",
    "penalty_clause": <true|false|null>,
    "penalty_amount_eur": <Number|null>,
    "jurisdiction": "<String|null>",
    "governing_law": "<String|null>"
  }},
  "risk_flags": [
    {{
      "severity": "<low|medium|high|critical>",
      "title": "<Risiko-Bezeichnung>",
      "description": "<Erklärung>",
      "clause_snippet": "<Zitat|null>",
      "policy_reference": "<String|null>"
    }}
  ],
  "overall_risk_level": "<low|medium|high|critical>",
  "overall_risk_score": <0-100>
}}

VERTRAGSTEXT:
\"\"\"{contract_text}\"\"\"
""".strip()


# ============================================================================
# LIEFERANTENVERTRAG / RAHMENVERTRAG
# ============================================================================

VENDOR_CONTRACT_SYSTEM_PROMPT = """
Du bist ein erfahrener Einkaufsjurist und Supply-Chain-Experte.
Du analysierst Lieferantenverträge und Rahmenvereinbarungen für Procurement und Legal.

Fokus:
- Lieferkonditionen (Preise, Mengen, Lieferzeiten)
- Qualitätsanforderungen und Gewährleistung
- Haftung und Pönalen
- Strikt JSON-Format
""".strip()


VENDOR_CONTRACT_USER_PROMPT_TEMPLATE = """
Analysiere den folgenden Lieferantenvertrag/Rahmenvertrag.

ERFORDERLICHE JSON-STRUKTUR:

{{
  "contract_id": "",
  "contract_type": "vendor",
  "language": "de",
  "summary": "<2-3 Sätze: Parteien, Liefergegenstand, Konditionen>",
  "extracted_fields": {{
    "buyer_name": "<String|null>",
    "supplier_name": "<String|null>",
    "goods_or_services": "<String|null>",
    "contract_start_date": "<YYYY-MM-DD|null>",
    "contract_end_date": "<YYYY-MM-DD|null>",
    "auto_renew": <true|false|null>,
    "min_order_value_eur": <Number|null>,
    "payment_terms_days": <Number|null>,
    "delivery_terms": "<String|null>",
    "incoterms": "<String|null>",
    "warranty_months": <Number|null>,
    "liability_cap_eur": <Number|null>,
    "penalty_for_delay": <true|false|null>,
    "penalty_percent_per_week": <Number|null>,
    "quality_requirements": "<String|null>",
    "audit_rights": <true|false|null>,
    "termination_notice_days": <Number|null>,
    "exclusivity": <true|false|null>
  }},
  "risk_flags": [
    {{
      "severity": "<low|medium|high|critical>",
      "title": "<Risiko-Bezeichnung>",
      "description": "<Erklärung>",
      "clause_snippet": "<Zitat|null>",
      "policy_reference": "<String|null>"
    }}
  ],
  "overall_risk_level": "<low|medium|high|critical>",
  "overall_risk_score": <0-100>
}}

VERTRAGSTEXT:
\"\"\"{contract_text}\"\"\"
""".strip()


# ============================================================================
# DIENSTLEISTUNGSVERTRAG
# ============================================================================

SERVICE_CONTRACT_SYSTEM_PROMPT = """
Du bist ein erfahrener Unternehmensjurist für Dienstleistungsverträge.
Du analysierst Beratungs-, IT-Service- und sonstige Dienstleistungsverträge.

Fokus:
- Leistungsbeschreibung und SLAs
- Vergütung und Abrechnungsmodell
- Haftung und Gewährleistung
- Strikt JSON-Format
""".strip()


SERVICE_CONTRACT_USER_PROMPT_TEMPLATE = """
Analysiere den folgenden Dienstleistungsvertrag.

ERFORDERLICHE JSON-STRUKTUR:

{{
  "contract_id": "",
  "contract_type": "service",
  "language": "de",
  "summary": "<2-3 Sätze: Parteien, Leistung, Vergütung>",
  "extracted_fields": {{
    "client_name": "<String|null>",
    "provider_name": "<String|null>",
    "service_description": "<String|null>",
    "contract_start_date": "<YYYY-MM-DD|null>",
    "contract_end_date": "<YYYY-MM-DD|null>",
    "contract_value_eur": <Number|null>,
    "billing_model": "<fixed_price|time_and_materials|retainer|null>",
    "hourly_rate_eur": <Number|null>,
    "payment_terms_days": <Number|null>,
    "sla_response_hours": <Number|null>,
    "sla_resolution_hours": <Number|null>,
    "liability_cap_eur": <Number|null>,
    "liability_cap_multiple": <Number|null>,
    "ip_ownership": "<client|provider|shared|null>",
    "confidentiality_clause": <true|false|null>,
    "termination_notice_days": <Number|null>,
    "termination_for_convenience": <true|false|null>,
    "subcontracting_allowed": <true|false|null>
  }},
  "risk_flags": [
    {{
      "severity": "<low|medium|high|critical>",
      "title": "<Risiko-Bezeichnung>",
      "description": "<Erklärung>",
      "clause_snippet": "<Zitat|null>",
      "policy_reference": "<String|null>"
    }}
  ],
  "overall_risk_level": "<low|medium|high|critical>",
  "overall_risk_score": <0-100>
}}

VERTRAGSTEXT:
\"\"\"{contract_text}\"\"\"
""".strip()


# ============================================================================
# MIETVERTRAG (GEWERBE)
# ============================================================================

RENTAL_CONTRACT_SYSTEM_PROMPT = """
Du bist ein erfahrener Immobilienjurist spezialisiert auf Gewerbemietrecht.
Du analysierst Mietverträge für Büros, Lager und Gewerbeflächen.

Fokus:
- Mietkonditionen (Kaltmiete, Nebenkosten, Staffelung)
- Laufzeit und Kündigungsfristen
- Instandhaltung und Schönheitsreparaturen
- Strikt JSON-Format
""".strip()


RENTAL_CONTRACT_USER_PROMPT_TEMPLATE = """
Analysiere den folgenden Mietvertrag (Gewerbe/Büro).

ERFORDERLICHE JSON-STRUKTUR:

{{
  "contract_id": "",
  "contract_type": "rental",
  "language": "de",
  "summary": "<2-3 Sätze: Parteien, Objekt, Miete, Laufzeit>",
  "extracted_fields": {{
    "landlord_name": "<String|null>",
    "tenant_name": "<String|null>",
    "property_address": "<String|null>",
    "property_type": "<office|warehouse|retail|mixed|null>",
    "area_sqm": <Number|null>,
    "contract_start_date": "<YYYY-MM-DD|null>",
    "contract_end_date": "<YYYY-MM-DD|null>",
    "fixed_term_years": <Number|null>,
    "monthly_rent_eur": <Number|null>,
    "monthly_utilities_eur": <Number|null>,
    "deposit_months": <Number|null>,
    "rent_escalation_clause": <true|false|null>,
    "escalation_percent_per_year": <Number|null>,
    "index_clause": <true|false|null>,
    "termination_notice_months": <Number|null>,
    "renewal_option": <true|false|null>,
    "maintenance_responsibility": "<landlord|tenant|shared|null>",
    "subletting_allowed": <true|false|null>,
    "fit_out_contribution_eur": <Number|null>
  }},
  "risk_flags": [
    {{
      "severity": "<low|medium|high|critical>",
      "title": "<Risiko-Bezeichnung>",
      "description": "<Erklärung>",
      "clause_snippet": "<Zitat|null>",
      "policy_reference": "<BGB §|null>"
    }}
  ],
  "overall_risk_level": "<low|medium|high|critical>",
  "overall_risk_score": <0-100>
}}

VERTRAGSTEXT:
\"\"\"{contract_text}\"\"\"
""".strip()


# ============================================================================
# KAUFVERTRAG
# ============================================================================

PURCHASE_CONTRACT_SYSTEM_PROMPT = """
Du bist ein erfahrener Wirtschaftsjurist für Kaufverträge.
Du analysierst Kaufverträge für Waren, Anlagen und Unternehmensbeteiligungen.

Fokus:
- Kaufgegenstand und Kaufpreis
- Gewährleistung und Garantien
- Zahlungskonditionen und Eigentumsübergang
- Strikt JSON-Format
""".strip()


PURCHASE_CONTRACT_USER_PROMPT_TEMPLATE = """
Analysiere den folgenden Kaufvertrag.

ERFORDERLICHE JSON-STRUKTUR:

{{
  "contract_id": "",
  "contract_type": "purchase",
  "language": "de",
  "summary": "<2-3 Sätze: Parteien, Kaufgegenstand, Preis>",
  "extracted_fields": {{
    "seller_name": "<String|null>",
    "buyer_name": "<String|null>",
    "purchase_object": "<String|null>",
    "purchase_price_eur": <Number|null>,
    "payment_terms": "<String|null>",
    "payment_due_date": "<YYYY-MM-DD|null>",
    "delivery_date": "<YYYY-MM-DD|null>",
    "delivery_terms": "<String|null>",
    "warranty_months": <Number|null>,
    "warranty_scope": "<String|null>",
    "liability_exclusions": "<String|null>",
    "retention_of_title": <true|false|null>,
    "acceptance_procedure": "<String|null>",
    "defect_notification_days": <Number|null>,
    "governing_law": "<String|null>",
    "jurisdiction": "<String|null>",
    "arbitration_clause": <true|false|null>
  }},
  "risk_flags": [
    {{
      "severity": "<low|medium|high|critical>",
      "title": "<Risiko-Bezeichnung>",
      "description": "<Erklärung>",
      "clause_snippet": "<Zitat|null>",
      "policy_reference": "<BGB §|null>"
    }}
  ],
  "overall_risk_level": "<low|medium|high|critical>",
  "overall_risk_score": <0-100>
}}

VERTRAGSTEXT:
\"\"\"{contract_text}\"\"\"
""".strip()


# ============================================================================
# ALLGEMEINER VERTRAG (FALLBACK)
# ============================================================================

GENERAL_CONTRACT_SYSTEM_PROMPT = """
Du bist ein erfahrener Unternehmensjurist mit breiter Expertise.
Du analysierst verschiedene Vertragstypen nach deutschem Recht.

Kernprinzipien:
- Identifiziere den Vertragstyp und die wesentlichen Regelungen
- Fokus auf Risiken und kritische Klauseln
- Strikt JSON-Format
""".strip()


GENERAL_CONTRACT_USER_PROMPT_TEMPLATE = """
Analysiere den folgenden Vertrag nach deutschem Recht.

ERFORDERLICHE JSON-STRUKTUR:

{{
  "contract_id": "",
  "contract_type": "general",
  "language": "de",
  "summary": "<2-3 Sätze: Parteien, Vertragsgegenstand, wesentliche Konditionen>",
  "extracted_fields": {{
    "party_a_name": "<String|null>",
    "party_a_role": "<String|null>",
    "party_b_name": "<String|null>",
    "party_b_role": "<String|null>",
    "contract_subject": "<String|null>",
    "contract_start_date": "<YYYY-MM-DD|null>",
    "contract_end_date": "<YYYY-MM-DD|null>",
    "contract_value_eur": <Number|null>,
    "payment_terms": "<String|null>",
    "termination_notice_days": <Number|null>,
    "liability_provisions": "<String|null>",
    "confidentiality_clause": <true|false|null>,
    "governing_law": "<String|null>",
    "jurisdiction": "<String|null>",
    "special_provisions": "<String|null>"
  }},
  "risk_flags": [
    {{
      "severity": "<low|medium|high|critical>",
      "title": "<Risiko-Bezeichnung>",
      "description": "<Erklärung>",
      "clause_snippet": "<Zitat|null>",
      "policy_reference": "<String|null>"
    }}
  ],
  "overall_risk_level": "<low|medium|high|critical>",
  "overall_risk_score": <0-100>
}}

VERTRAGSTEXT:
\"\"\"{contract_text}\"\"\"
""".strip()


# ============================================================================
# PROMPT-FUNKTIONEN
# ============================================================================

def _prepare_contract_text(contract_text: str, max_chars: int = 7000) -> str:
    """Bereitet Vertragstext für LLM vor (kürzen, escapen)."""
    if len(contract_text) > max_chars:
        contract_text = contract_text[:max_chars] + "\n\n[... Text gekürzt ...]"
    return contract_text.replace("{", "{{").replace("}", "}}")


def get_employment_contract_prompt(contract_text: str) -> str:
    """Prompt für Arbeitsverträge."""
    escaped_text = _prepare_contract_text(contract_text)
    return EMPLOYMENT_CONTRACT_USER_PROMPT_TEMPLATE.format(contract_text=escaped_text)


def get_saas_contract_prompt(contract_text: str) -> str:
    """Prompt für SaaS-Verträge."""
    escaped_text = _prepare_contract_text(contract_text)
    return SAAS_CONTRACT_USER_PROMPT_TEMPLATE.format(contract_text=escaped_text)


def get_nda_contract_prompt(contract_text: str) -> str:
    """Prompt für NDAs/Geheimhaltungsvereinbarungen."""
    escaped_text = _prepare_contract_text(contract_text)
    return NDA_CONTRACT_USER_PROMPT_TEMPLATE.format(contract_text=escaped_text)


def get_vendor_contract_prompt(contract_text: str) -> str:
    """Prompt für Lieferantenverträge."""
    escaped_text = _prepare_contract_text(contract_text)
    return VENDOR_CONTRACT_USER_PROMPT_TEMPLATE.format(contract_text=escaped_text)


def get_service_contract_prompt(contract_text: str) -> str:
    """Prompt für Dienstleistungsverträge."""
    escaped_text = _prepare_contract_text(contract_text)
    return SERVICE_CONTRACT_USER_PROMPT_TEMPLATE.format(contract_text=escaped_text)


def get_rental_contract_prompt(contract_text: str) -> str:
    """Prompt für Mietverträge."""
    escaped_text = _prepare_contract_text(contract_text)
    return RENTAL_CONTRACT_USER_PROMPT_TEMPLATE.format(contract_text=escaped_text)


def get_purchase_contract_prompt(contract_text: str) -> str:
    """Prompt für Kaufverträge."""
    escaped_text = _prepare_contract_text(contract_text)
    return PURCHASE_CONTRACT_USER_PROMPT_TEMPLATE.format(contract_text=escaped_text)


def get_general_contract_prompt(contract_text: str) -> str:
    """Prompt für allgemeine Verträge (Fallback)."""
    escaped_text = _prepare_contract_text(contract_text)
    return GENERAL_CONTRACT_USER_PROMPT_TEMPLATE.format(contract_text=escaped_text)


# Mapping für einfachen Zugriff
PROMPT_FUNCTIONS = {
    "employment": get_employment_contract_prompt,
    "saas": get_saas_contract_prompt,
    "nda": get_nda_contract_prompt,
    "vendor": get_vendor_contract_prompt,
    "service": get_service_contract_prompt,
    "rental": get_rental_contract_prompt,
    "purchase": get_purchase_contract_prompt,
    "general": get_general_contract_prompt,
}

SYSTEM_PROMPTS = {
    "employment": EMPLOYMENT_CONTRACT_SYSTEM_PROMPT,
    "saas": SAAS_CONTRACT_SYSTEM_PROMPT,
    "nda": NDA_CONTRACT_SYSTEM_PROMPT,
    "vendor": VENDOR_CONTRACT_SYSTEM_PROMPT,
    "service": SERVICE_CONTRACT_SYSTEM_PROMPT,
    "rental": RENTAL_CONTRACT_SYSTEM_PROMPT,
    "purchase": PURCHASE_CONTRACT_SYSTEM_PROMPT,
    "general": GENERAL_CONTRACT_SYSTEM_PROMPT,
}


def get_prompt_for_type(contract_type: str, contract_text: str) -> tuple:
    """
    Gibt (system_prompt, user_prompt) für den Vertragstyp zurück.
    
    Args:
        contract_type: employment, saas, nda, vendor, service, rental, purchase, general
        contract_text: Der zu analysierende Vertragstext
    
    Returns:
        Tuple (system_prompt, user_prompt)
    """
    # Fallback auf general wenn Typ unbekannt
    if contract_type not in PROMPT_FUNCTIONS:
        contract_type = "general"
    
    system_prompt = SYSTEM_PROMPTS[contract_type]
    user_prompt = PROMPT_FUNCTIONS[contract_type](contract_text)
    
    return system_prompt, user_prompt
