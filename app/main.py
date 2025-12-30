from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

from app.catalog import list_plans
from app.bot import bot_reply

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
INDEX_FILE = STATIC_DIR / "index.html"

app = FastAPI(title="Bot MVP Web UI")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class ChatIn(BaseModel):
    message: str
    country: str = "CO"

@app.get("/debug/plans")
async def debug_plans(country: str = "CO"):
    return {"country": country, "plans": list_plans(country)}

@app.get("/")
async def home():
    return FileResponse(str(INDEX_FILE))

@app.post("/chat")
async def chat_endpoint(payload: ChatIn):
    reply = bot_reply(payload.message, payload.country)
    return {"reply": reply}

@app.get("/health")
async def health():
    return {"status": "ok"}
