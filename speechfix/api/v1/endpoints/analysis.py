"""
POST /api/v1/speech/analyze
Receives a multipart audio upload, transcribes with Faster-Whisper,
analyses grammar with Gemini, returns the result_partial.html fragment.
"""

import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from speechfix.services.audio_transcribe_service import transcribe_audio_whisper
from speechfix.services.grammar_service import analyze_grammar

logger = logging.getLogger(__name__)
router = APIRouter()


# analysis.py is at speechfix/api/v1/endpoints/analysis.py ( parent x4 = speechfix/)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.post("/analyze", response_class=HTMLResponse)
async def process_audio(
    request: Request,
    topic: str = Form(...),
    difficulty: str = Form(...),
    audio_file: UploadFile = File(...),
):
    audio_bytes = await audio_file.read()
    logger.info(
        "Received audio upload: %s bytes, topic=%s difficulty=%s",
        len(audio_bytes),
        topic,
        difficulty,
    )

    loop = asyncio.get_running_loop()

    # Step 1 — Transcribe (CPU-bound → thread pool)
    transcript: str = await loop.run_in_executor(
        None, transcribe_audio_whisper, audio_bytes
    )

    if not transcript.strip() or transcript.startswith("Transcription Failed"):
        logger.warning("Transcription empty or failed: %s", transcript)
        return templates.TemplateResponse(
            "result_partial.html",
            {
                "request": request,
                "transcript": "No speech detected or transcription failed.",
                "score": 0,
                "score_label": "N/A",
                "errors": [],
                "technical_errors": [],
                "corrected_text": "Please try recording again and speak clearly.",
            },
        )

    logger.info("Transcript (%d chars): %s…", len(transcript), transcript[:80])

    # Step 2 — Gemini grammar analysis (network-bound → thread pool)
    analysis_data: dict = await loop.run_in_executor(
        None, analyze_grammar, transcript, topic, difficulty
    )

    # Step 3 — Merge and render partial
    analysis_data["transcript"] = transcript
    analysis_data["request"] = request

    return templates.TemplateResponse("result_partial.html", analysis_data)
