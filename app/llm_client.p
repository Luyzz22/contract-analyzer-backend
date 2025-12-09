import json
import os
from typing import Any, Dict

from .prompts import EMPLOYMENT_CONTRACT_SYSTEM_PROMPT


class LLMError(Exception):
    pass


def _dummy_response() -> Dict[str, Any]:
    dummy_json = """
    {
      "contract_id": "",
      "contract_type": "employment",
      "language": "de",
      "summary": "Dummy-Zusammenfassung aus dem LLM-Client.",
      "extracted_fields": {
        "parties": [],
        "start_date": null,
        "fixed_term": false,
        "end_date": null,
        "probation_period_months": null,
        "weekly_hours": null,
        "base_salary_eur": null,
        "vacation_days_per_year": null,
        "notice_period_employee": null,
        "notice_period_employer": null,
        "non_compete_during_term": false,
        "post_contract_non_compete": false
      },
      "risk_flags": []
    }
    """
    return json.loads(dummy_json)


def call_employment_contract_model(prompt: str) -> Dict[str, Any]:
    use_dummy = os.getenv("CONTRACT_ANALYZER_DUMMY", "true").lower() == "true"
    if use_dummy:
        return _dummy_response()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMError("OPENAI_API_KEY ist nicht gesetzt.")

    try:
        from openai import OpenAI
    except ImportError as e:
        raise LLMError(f"openai-Paket nicht installiert: {e}") from e

    client = OpenAI(api_key=api_key)

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": EMPLOYMENT_CONTRACT_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
        )

        # Text-Content aus der ersten Antwort nehmen
        content = response.output[0].content[0].text
        data = json.loads(content)
    except Exception as e:
        raise LLMError(f"LLM-Fehler: {e}") from e

    return data

