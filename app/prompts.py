# app/prompts.py
"""
Prompt-Definitionen für die KI-Analyse von Verträgen.
Fokus: deutsche Arbeitsverträge und B2B-SaaS-/Dienstleistungsverträge.

Die Prompts sind optimiert für:
- GPT-4 mini (schnell & kostengünstig)
- Strikte JSON-Output-Validierung
- Deutsche Rechtsterminologie
- CFO & Legal-Ops-Perspektive
"""


# ============================================================================
# ARBEITSVERTRÄGE – SYSTEM & USER PROMPTS
# ============================================================================

EMPLOYMENT_CONTRACT_SYSTEM_PROMPT = """
Du bist ein erfahrener Fachanwalt für Arbeitsrecht in Deutschland mit 20+ Jahren Erfahrung.
Du arbeitest für eine Kanzlei-Software, die Arbeitsverträge für Anwälte und Steuerkanzleien voranalysiert.

Deine Aufgabe ist es, aus Vertragsdokumenten strukturierte Daten und juristisch relevante Risiken zu extrahieren.
Du ersetzt keine Rechtsberatung, sondern bereitest Informationen für professionelle Anwender auf.

Kernprinzipien:
- Sachlich, präzise, juristische Fachsprache
- Fokus auf messbare Daten (Daten, Fristen, Beträge) und echte Risiken
- Nichts erfinden, was nicht im Vertrag steht
- Strikt JSON-Format, keine Erklärungstexte

Du antwortest ausschließlich im JSON-Format gemäß dem vorgegebenen Schema.
""".strip()


EMPLOYMENT_CONTRACT_USER_PROMPT_TEMPLATE = """
Analysiere den folgenden deutschen Arbeitsvertrag für eine Kanzlei, die Arbeitsrecht für Unternehmen und Arbeitnehmer betreut.

ANALYSE-ZIELE:
1. Erstelle eine kurze, präzise und sachliche Zusammenfassung des Vertragsinhalts
   (Parteien, Tätigkeit, Befristung, Vergütung, Arbeitszeit, besondere Klauseln).
   → Maximal 3–4 Sätze, geeignet für erfahrene Juristen, KEINE Wertungen.

2. Extrahiere die wichtigsten Strukturparameter:
   - Partei-Namen und deren Rollen (Arbeitgeber/Arbeitnehmer)
   - Start-, End-, Probezeitdauer
   - Arbeitszeit, Vergütung, Urlaub
   - Kündigungsfristen, Wettbewerbsverbote, Geheimhaltung

3. Identifiziere arbeitsrechtlich relevante Risiken, Unklarheiten oder atypische Regelungen:
   - Ungewöhnliche oder aggressive Klauseln
   - Fehlende Standardregelungen
   - Potenzielle Konflikte mit deutschem Arbeitsrecht
   - Besonderheiten in Überstundenabgeltung, Konkurrenzschutz, Haftungsausschlüssen

ERFORDERLICHE STRUKTUR – Gib deine Antwort ausschließlich als valides JSON zurück:

{{
  "contract_id": "<STRING: eindeutige ID oder leerer String>",
  "contract_type": "employment",
  "language": "de",
  "summary": "<STRING: 3-4 Sätze Zusammenfassung>",
  "extracted_fields": {{
    "parties": [
      {{ "name": "<STRING|null: Name der Partei>", "role": "<employer|employee|null>" }}
    ],
    "start_date": "<YYYY-MM-DD|null>",
    "fixed_term": <true|false: ist Befristung vorhanden?>,
    "end_date": "<YYYY-MM-DD|null: nur wenn Befristung>",
    "probation_period_months": <NUMBER|null: z.B. 6.0>,
    "weekly_hours": <NUMBER|null: z.B. 40.0>,
    "base_salary_eur": <NUMBER|null: z.B. 3200.0>,
    "vacation_days_per_year": <NUMBER|null>,
    "notice_period_employee": "<STRING|null: z.B. '4 Wochen zum Schluss eines Kalendermonats' oder '2 Wochen in Probezeit'>",
    "notice_period_employer": "<STRING|null>",
    "non_compete_during_term": <true|false: Wettbewerbsverbot WÄHREND der Beschäftigung>,
    "post_contract_non_compete": <true|false: Wettbewerbsverbot NACH Beendigung>
  }},
  "risk_flags": [
    {{
      "severity": "<low|medium|high>",
      "title": "<STRING: prägnante, deutsche Risiko-Bezeichnung>",
      "description": "<STRING: kurze Erklärung des Risikos und warum es relevant ist>",
      "clause_snippet": "<STRING|null: ggf. direkter Zitat aus Vertrag>",
      "policy_reference": "<STRING|null: z.B. 'BGB §623', 'Arbeitszeit-Policy', 'Datenschutz-Policy'>"
    }}
  ]
}}

BEFÜLLUNGS-HINWEISE:
✓ "summary": Maximal 3–4 Sätze, klar, sachlich, ohne Wertungen, geeignet für erfahrene Juristen.
✓ "parties": Versuche die Namen der Parteien zu erkennen und als "employer" bzw. "employee" zu kennzeichnen.
✓ Datumsangaben im ISO-Format YYYY-MM-DD, wenn eindeutig bestimmbar, sonst null.
✓ Geldbeträge als numerische Werte in EUR ohne Tausendertrennzeichen (z.B. 3200.0, nicht "3.200,00").
✓ Wenn eine Information im Vertrag nicht eindeutig bestimmbar ist, setze den Wert auf null.
✓ "risk_flags": Erfasse nur juristisch sinnvolle Risiken (z.B. ungewöhnliche Überstundenregelung, sehr kurze Kündigungsfristen, problematische Wettbewerbsverbote).
✓ "severity": low = informativ, medium = sollte geprüft werden, high = kritisch für Kanzlei/Client

KRITISCHE ANFORDERUNGEN:
⚠ Gib ausschließlich JSON zurück, KEINEN erklärenden Freitext vorher oder nachher.
⚠ Die JSON-Struktur muss exakt dem oben angegebenen Schema entsprechen.
⚠ Verwende deutsche Sprache in "summary", "title" und "description".
⚠ Erfinde keine Tatsachen, die nicht im Vertrag stehen – im Zweifelsfall null setzen.
⚠ Wenn das JSON ungültig ist, wird die Analyse fehlschlagen – prüfe deine Syntax.

VERTRAGSTEXT ZUR ANALYSE:
\"\"\"{contract_text}\"\"\"
""".strip()


# ============================================================================
# SAAS- / DIENSTLEISTUNGSVERTRÄGE – SYSTEM & USER PROMPTS
# ============================================================================

SAAS_CONTRACT_SYSTEM_PROMPT = """
Du bist ein erfahrener Unternehmensjurist und CFO-orientierter SaaS-Vertragsanalyst mit 15+ Jahren Erfahrung.
Du analysierst B2B-SaaS- und Cloud-Dienstleistungsverträge für Finanzverantwortliche, Legal Ops und Kanzleien.

Dein spezieller Fokus liegt auf:
- Wirtschaftlichen Kerndaten (ACV, Laufzeit, Auto-Renewal, Kündigungsfristen)
- Wesentlichen Risiken (Haftungsbegrenzung, SLA/Uptime, Datenschutz/Datenlokation, Vendor-Lock-in)
- Nachverhandlungs-Chancen und Best Practices

Du ersetzt keine Rechtsberatung, sondern bereitest Informationen für professionelle Anwender auf.

Kernprinzipien:
- Finanz- & Operational-Perspektive (nicht nur juristisch)
- Fokus auf Kennzahlen (ACV, SLA%, Auto-Renew, Kündigungsfristen)
- Verständlich für CFO, Procurement & General Counsel
- Strikt JSON-Format, keine Erklärungstexte

Du antwortest ausschließlich im JSON-Format gemäß dem vorgegebenen Schema.
""".strip()


SAAS_CONTRACT_USER_PROMPT_TEMPLATE = """
Analysiere den folgenden B2B-SaaS- bzw. Cloud-Dienstleistungsvertrag aus Sicht von CFO, Legal Ops und Beschaffung.

ANALYSE-ZIELE:
1. Erstelle eine kurze, prägnante Zusammenfassung der wirtschaftlichen Kerndaten:
   → Parteien, Produkt/Service, Laufzeit, Mindestlaufzeit, Auto-Renewal, ACV, Billing-Rhythmus
   → 2–3 Sätze, sachlich, für CFO verständlich

2. Befülle die Strukturfelder für einen SaaS-Vertrag so weit wie möglich:
   → Finanzielle Kennzahlen (ACV, Billing, Mindestlaufzeit)
   → Governance (Auto-Renewal, Kündigungsfristen, Kündigungsrecht)
   → Technische/Operative Aspekte (SLA, Datenlokation, DP-Addendum)

3. Identifiziere CFO-/Enterprise-relevante Risiken mit Fokus auf:
   - Auto-Renewal, Verlängerungslogik, Kündigungsfristen, Mindestlaufzeit
   - Haftungsbegrenzung (Cap, Ausnahmen), Verfügbarkeitszusagen (SLA/Uptime) und Gutschrift-Mechaniken
   - Datenschutz (Datenlokation, Auftragsverarbeitung, Subprozessoren)
   - Vendor-Lock-in (Kündigungsrechte, Exit/Data-Export, Migrationsunterstützung)

ERFORDERLICHE STRUKTUR – Gib deine Antwort ausschließlich als valides JSON zurück:

{{
  "contract_id": "<STRING: eindeutige ID oder leerer String>",
  "contract_type": "saas",
  "language": "de",
  "summary": "<STRING: 2-3 Sätze Zusammenfassung mit Kerndaten>",
  "extracted_fields": {{
    "customer_name": "<STRING|null: Name des Kunden>",
    "vendor_name": "<STRING|null: Name des Anbieters>",
    "contract_start_date": "<YYYY-MM-DD|null>",
    "contract_end_date": "<YYYY-MM-DD|null>",
    "auto_renew": <true|false|null: verlängert sich automatisch?>,
    "renewal_notice_days": "<NUMBER|null: Tage vor Ablauf, in denen gekündigt werden muss>",
    "annual_contract_value_eur": "<NUMBER|null: jährlicher Vertragswert geschätzt>",
    "billing_interval": "<monthly|quarterly|annual|null>",
    "min_term_months": "<NUMBER|null: Mindestlaufzeit>",
    "termination_for_convenience": "<true|false|null: kann ohne Grund gekündigt werden?>",
    "data_location": "<STRING|null: z.B. 'EU', 'Germany', 'US'>",
    "dp_addendum_included": "<true|false|null: ist Datenschutz-Addendum enthalten?>",
    "liability_cap_multiple_acv": "<NUMBER|null: Haftungsobergrenze als Vielfaches des ACV>",
    "uptime_sla_percent": "<NUMBER|null: z.B. 99.5>"
  }},
  "risk_flags": [
    {{
      "severity": "<low|medium|high>",
      "title": "<STRING: prägnante, deutsche Risiko-Bezeichnung>",
      "description": "<STRING: kurze Erklärung des finanziellen oder operativen Risikos>",
      "clause_snippet": "<STRING|null: ggf. direkter Zitat aus Vertrag>",
      "policy_reference": "<STRING|null: z.B. 'Data Processing Agreement', 'SLA Schedule'>"
    }}
  ]
}}

BEFÜLLUNGS-HINWEISE:
✓ Nutze nur Informationen aus dem Vertrag; setze unbekannte Werte auf null.
✓ "annual_contract_value_eur": jährlicher Vertragswert in EUR, anhand der Vertragslogik geschätzt.
  → Falls z.B. 12.000 EUR für 12 Monate → ACV = 12.000
  → Falls Staffelung nach Volumen → beste Schätzung
✓ "auto_renew": true, wenn sich der Vertrag automatisch verlängert, sofern nicht fristgerecht gekündigt.
✓ "renewal_notice_days": Frist (in Tagen) vor Ablauf/Verlängerung, zu der gekündigt werden muss.
  → Typisch: 30, 60, 90 Tage
✓ "termination_for_convenience": true, wenn Kunde jederzeit (ggf. nach Mindestlaufzeit) kündigen kann.
✓ "liability_cap_multiple_acv": Haftungsobergrenze in Vielfachen des ACV (z.B. 1.0 für 1x ACV, 12.0 für 12x ACV).
✓ "risk_flags": Fokussiere auf Punkte mit finanzieller oder operativer Relevanz für CFO / Management.
  → z.B. Auto-Renewal ohne ausreichende Kündigungsfrist = high risk

KRITISCHE ANFORDERUNGEN:
⚠ Gib ausschließlich JSON zurück, KEINEN erklärenden Freitext vorher oder nachher.
⚠ Die JSON-Struktur muss exakt dem oben angegebenen Schema entsprechen.
⚠ Verwende deutsche Sprache in "summary", "title" und "description".
⚠ Erfinde keine Tatsachen, die nicht im Vertrag stehen – im Zweifelsfall null setzen.
⚠ Wenn das JSON ungültig ist, wird die Analyse fehlschlagen – prüfe deine Syntax.

VERTRAGSTEXT ZUR ANALYSE:
\"\"\"{contract_text}\"\"\"
""".strip()

# ============================================================================
# HILFS-FUNKTIONEN FÜR PROMPT-TEMPLATE-FILLING
# ============================================================================

def get_employment_contract_prompt(contract_text: str) -> str:
    """
    Füllt das Employment-Contract-Userprompt-Template mit echtem Vertragstext.
    
    Args:
        contract_text: Extrahierter Text aus PDF/DOCX
    
    Returns:
        Fertig ausgefülltes Prompt-Template
    """
    # Text kürzen auf ~8000 Tokens (ca. 6000-7000 Zeichen)
    max_chars = 7000
    if len(contract_text) > max_chars:
        contract_text = contract_text[:max_chars] + "\n\n[... Text gekürzt ...]"
    
    # WICHTIG: Escapen der geschweiften Klammern im Vertragstext
    escaped_text = contract_text.replace("{", "{{").replace("}", "}}")
    
    return EMPLOYMENT_CONTRACT_USER_PROMPT_TEMPLATE.format(contract_text=escaped_text)


def get_saas_contract_prompt(contract_text: str) -> str:
    """
    Füllt das SaaS-Contract-Userprompt-Template mit echtem Vertragstext.
    
    Args:
        contract_text: Extrahierter Text aus PDF/DOCX
    
    Returns:
        Fertig ausgefülltes Prompt-Template
    """
    # Text kürzen auf ~8000 Tokens (ca. 6000-7000 Zeichen)
    max_chars = 7000
    if len(contract_text) > max_chars:
        contract_text = contract_text[:max_chars] + "\n\n[... Text gekürzt ...]"
    
    # WICHTIG: Escapen der geschweiften Klammern im Vertragstext
    escaped_text = contract_text.replace("{", "{{").replace("}", "}}")
    
    return SAAS_CONTRACT_USER_PROMPT_TEMPLATE.format(contract_text=escaped_text)


# ============================================================================
# VALIDIERUNGS-SCHEMAS (Optional: für lokale Validierung vor LLM-Call)
# ============================================================================

EMPLOYMENT_CONTRACT_JSON_SCHEMA = {
    "type": "object",
    "required": ["contract_id", "contract_type", "language", "summary", "extracted_fields", "risk_flags"],
    "properties": {
        "contract_id": {"type": "string"},
        "contract_type": {"enum": ["employment"]},
        "language": {"enum": ["de"]},
        "summary": {"type": "string", "minLength": 10, "maxLength": 500},
        "extracted_fields": {
            "type": "object",
            "properties": {
                "parties": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": ["string", "null"]},
                            "role": {"enum": ["employer", "employee", "null"]}
                        }
                    }
                },
                "start_date": {"type": ["string", "null"], "pattern": "^\\d{4}-\\d{2}-\\d{2}$|^null$"},
                "fixed_term": {"type": "boolean"},
                "end_date": {"type": ["string", "null"]},
                "probation_period_months": {"type": ["number", "null"]},
                "weekly_hours": {"type": ["number", "null"]},
                "base_salary_eur": {"type": ["number", "null"]},
                "vacation_days_per_year": {"type": ["number", "null"]},
                "notice_period_employee": {"type": ["string", "null"]},
                "notice_period_employer": {"type": ["string", "null"]},
                "non_compete_during_term": {"type": "boolean"},
                "post_contract_non_compete": {"type": "boolean"}
            }
        },
        "risk_flags": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["severity", "title", "description"],
                "properties": {
                    "severity": {"enum": ["low", "medium", "high"]},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "clause_snippet": {"type": ["string", "null"]},
                    "policy_reference": {"type": ["string", "null"]}
                }
            }
        }
    }
}

SAAS_CONTRACT_JSON_SCHEMA = {
    "type": "object",
    "required": ["contract_id", "contract_type", "language", "summary", "extracted_fields", "risk_flags"],
    "properties": {
        "contract_id": {"type": "string"},
        "contract_type": {"enum": ["saas"]},
        "language": {"enum": ["de"]},
        "summary": {"type": "string", "minLength": 10, "maxLength": 500},
        "extracted_fields": {
            "type": "object",
            "properties": {
                "customer_name": {"type": ["string", "null"]},
                "vendor_name": {"type": ["string", "null"]},
                "contract_start_date": {"type": ["string", "null"]},
                "contract_end_date": {"type": ["string", "null"]},
                "auto_renew": {"type": ["boolean", "null"]},
                "renewal_notice_days": {"type": ["number", "null"]},
                "annual_contract_value_eur": {"type": ["number", "null"]},
                "billing_interval": {"enum": ["monthly", "quarterly", "annual", "null"]},
                "min_term_months": {"type": ["number", "null"]},
                "termination_for_convenience": {"type": ["boolean", "null"]},
                "data_location": {"type": ["string", "null"]},
                "dp_addendum_included": {"type": ["boolean", "null"]},
                "liability_cap_multiple_acv": {"type": ["number", "null"]},
                "uptime_sla_percent": {"type": ["number", "null"]}
            }
        },
        "risk_flags": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["severity", "title", "description"],
                "properties": {
                    "severity": {"enum": ["low", "medium", "high"]},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "clause_snippet": {"type": ["string", "null"]},
                    "policy_reference": {"type": ["string", "null"]}
                }
            }
        }
    }
}

