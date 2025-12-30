import os
import re
from typing import Any, Dict, Optional, Tuple

from app.catalog import list_plans
from app.ai import interpret


ALLOWED_COUNTRIES = {"CO", "BR", "PE", "EC"}


def format_money(value, currency: str) -> str:
    if value is None or not currency:
        return "N/D"

    currency = currency.upper()

    if currency in ("USD", "BRL"):
        s = f"{float(value):,.2f} {currency}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    s = f"{int(round(float(value))):,} {currency}"
    return s.replace(",", ".")


def _extract_plan_index(text: str) -> Optional[int]:
    t = (text or "").strip().lower()

    if t.isdigit():
        return int(t)

    # "plan 3"
    m = re.search(r"\bplan\s*(\d{1,2})\b", t)
    if m:
        return int(m.group(1))

    # "quiero el 2"
    m = re.search(r"\b(\d{1,2})\b", t)
    if m:
        return int(m.group(1))

    return None


def _reply_list(country: str) -> str:
    plans = list_plans(country)
    if not plans:
        return "No hay planes activos o no se pudo leer db.json."

    lines = [f"Planes ({country}):"]
    for i, p in enumerate(plans, start=1):
        lines.append(f"{i}) {p.get('nombre','(sin nombre)')} – {format_money(p.get('precio'), p.get('moneda'))}")
    lines.append("Dime el número del plan para ver detalles.")
    return "\n".join(lines)


def _reply_details(country: str, idx: int) -> str:
    plans = list_plans(country)
    if not (1 <= idx <= len(plans)):
        return "Dime el número del plan (por ejemplo: 1, 2, 3) o escribe 'planes'."

    p = plans[idx - 1]
    beneficios_list = p.get("beneficios") or []
    beneficios = ("\n- " + "\n- ".join(beneficios_list)) if beneficios_list else ""
    return (
        f"{p.get('nombre','(sin nombre)')} ({p.get('tier','')})\n"
        f"Precio: {format_money(p.get('precio'), p.get('moneda'))}\n"
        f"Beneficios:{beneficios}"
    )


def bot_reply(message: str, country: str = "CO") -> str:
    country = (country or "CO").upper()
    if country not in ALLOWED_COUNTRIES:
        country = "CO"

    msg = (message or "").strip()
    low = msg.lower()

    # Fallback mínimo sin IA: listar y detalle por número
    if not os.getenv("OPENAI_API_KEY") or interpret is None:
        if any(k in low for k in ("planes", "plan", "precio", "suscrip", "costo")):
            return _reply_list(country) + " [AI OFF]"

        idx = _extract_plan_index(msg)
        if isinstance(idx, int):
            return _reply_details(country, idx) + " [AI OFF]"

        return "Escribe 'planes' o un número (por ejemplo: 1..10). [AI OFF]"

    # Con IA: intención + datos reales
    try:
        intent_obj: Dict[str, Any] = interpret(msg, country)
        intent = (intent_obj.get("intent") or "UNKNOWN").upper()
        new_country = (intent_obj.get("country") or country).upper()
        if new_country not in ALLOWED_COUNTRIES:
            new_country = country

        if intent == "HELP":
            return (
                "Comandos:\n"
                "- 'planes' / 'precios'\n"
                "- 'plan 3' (ver detalles)\n"
                "- 'cambia a Brasil' o 'BR' (cambiar país)\n"
                "[AI ON]"
            )

        if intent == "CHANGE_COUNTRY":
            return f"Listo. País cambiado a {new_country}. Escribe 'planes' para ver opciones. [AI ON]"

        if intent == "LIST_PLANS":
            return _reply_list(new_country) + " [AI ON]"

        if intent == "SHOW_PLAN_DETAILS":
            idx = intent_obj.get("plan_index")
            if isinstance(idx, str) and idx.isdigit():
                idx = int(idx)
            if not isinstance(idx, int):
                # Fallback local si la IA no devolvió índice
                idx = _extract_plan_index(msg)
            if isinstance(idx, int):
                return _reply_details(new_country, idx) + " [AI ON]"
            return "Dime el número del plan (por ejemplo: 1, 2, 3) o escribe 'planes'. [AI ON]"

        return "No estoy seguro. Escribe 'planes' o 'ayuda'. [AI ON]"

    except Exception:
        return "Tuve un problema interpretando el mensaje. Escribe 'planes' o un número (1..10). [AI ERROR]"
