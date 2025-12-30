import os
import json
from typing import Any, Dict
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM = """
Eres un clasificador de intención para un bot de suscripciones.
Devuelve SOLO JSON válido (sin texto adicional).

Intenciones permitidas:
- LIST_PLANS
- SHOW_PLAN_DETAILS
- CHANGE_COUNTRY
- HELP
- UNKNOWN

Reglas:
- Si el usuario pregunta qué planes hay, opciones disponibles, precios, suscripciones,
  costos o similares -> LIST_PLANS
- Si el usuario elige un número o menciona un plan específico -> SHOW_PLAN_DETAILS
- Si el usuario menciona país, moneda, o códigos CO BR PE EC, o nombres (Colombia, Brasil, Perú, Ecuador),
  o monedas (COP, BRL, PEN, USD) -> CHANGE_COUNTRY
- Si pide ayuda, comandos o cómo usar el bot -> HELP
- Si no es claro -> UNKNOWN

Campos opcionales:
- plan_index (int)  # 1..N si aplica
- country (CO|BR|PE|EC)

Responde SIEMPRE con un objeto JSON que incluya al menos: {"intent": "..."}.
"""

def interpret(message: str, country: str = "CO") -> Dict[str, Any]:
    msg = (message or "").strip()
    country = (country or "CO").upper()

    r = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": json.dumps({"message": msg, "country": country}, ensure_ascii=False)},
        ],
        response_format={"type": "json_object"},
    )

    content = r.choices[0].message.content or "{}"
    try:
        obj = json.loads(content)
        if not isinstance(obj, dict):
            return {"intent": "UNKNOWN"}
        if "intent" not in obj:
            obj["intent"] = "UNKNOWN"
        return obj
    except json.JSONDecodeError:
        return {"intent": "UNKNOWN"}
