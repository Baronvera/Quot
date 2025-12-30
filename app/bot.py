def normalize(text: str) -> str:
    return (text or "").strip().lower()

def bot_reply(message: str) -> str:
    msg = normalize(message)

    if msg in ("hola", "buenas", "hello"):
        return "Hola. Escribe PLANES para ver opciones o AYUDA para comandos."

    if msg in ("ayuda", "help", "?"):
        return "Comandos: HOLA, PLANES, INFO"

    if msg in ("planes", "plan", "suscripciones"):
        return (
            "Planes (demo MVP):\n"
            "1) Basic Starter\n"
            "2) Standard\n"
            "3) Premium\n"
            "Responde con el número (1/2/3)."
        )

    if msg in ("1", "basic", "basic starter"):
        return "Basic Starter: acceso esencial + soporte email. (Demo)"

    if msg in ("2", "standard"):
        return "Standard: incluye Basic + soporte prioritario + reportes básicos. (Demo)"

    if msg in ("3", "premium"):
        return "Premium: incluye Standard + dashboard + soporte WhatsApp. (Demo)"

    if msg in ("info", "quienes son", "qué es esto"):
        return "Soy un bot MVP en FastAPI con interfaz web. Próximo paso: conectar WhatsApp."

    return "No entendí. Escribe AYUDA para ver comandos."
