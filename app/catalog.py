import json
from pathlib import Path
from typing import List, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "db.json"

ALLOWED_COUNTRIES = {"CO", "BR", "PE", "EC"}

def list_plans(country: str = "CO") -> List[Dict[str, Any]]:
    country = (country or "CO").upper()
    if country not in ALLOWED_COUNTRIES:
        country = "CO"

    try:
        raw = DB_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

    plans = [p for p in data.get("plans", []) if p.get("activo", True)]
    plans.sort(key=lambda x: x.get("orden", 999))

    out: List[Dict[str, Any]] = []
    for p in plans:
        precios = p.get("precios") or {}
        monedas = p.get("moneda") or {}

        out.append({
            "plan_id": p.get("plan_id"),
            "nombre": p.get("nombre"),
            "tier": p.get("tier"),
            "beneficios": p.get("beneficios", []) or [],
            "precio": precios.get(country),
            "moneda": monedas.get(country),
        })

    return out
