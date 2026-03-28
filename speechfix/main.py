"""
SpeechFix — Entry point
Registers middleware, static files, templates, and the v1 API router.
"""

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from sqlalchemy.orm import Session
from speechfix.core.database import engine, Base, get_db
from speechfix.models.db_models import User, Question

from speechfix.api.v1.router import router as api_v1_router

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("speechfix")

# App
app = FastAPI(
    title="SpeechFix API",
    description="AI-powered interview practice: Faster-Whisper + Gemini Flash",
    version="1.2.1",
)

# Paths

# main.py lives at speechfix/main.py  →  parent == speechfix/
BASE_DIR = Path(__file__).resolve().parent

# Static files
app.mount(
    "/speechfix/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)

# Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# API v1 router (analysis + questions)

app.include_router(api_v1_router, prefix="/api/v1")

# Create Database Tables
Base.methods.create_all(bind=engine)

# Frontend route
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "service": "SpeechFix"}
