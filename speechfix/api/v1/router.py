import asyncio
from fastapi import APIRouter, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from speechfix.services.audio_transcribe_service import transcribe_audio_vosk
from speechfix.services.grammar_service import analyze_grammar

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.post("/analyze", response_class=HTMLResponse)
async def process_audio(
    request: Request,
    topic: str = Form(...),
    difficulty: str = Form(...),
    audio_file: UploadFile = File(...)
):
    # Read the audio bytes into memory
    audio_bytes = await audio_file.read()
    
    loop = asyncio.get_event_loop()
    
    # Step 1: Transcribe with local Vosk (Run in thread pool to prevent blocking)
    transcript = await loop.run_in_executor(
        None, transcribe_audio_vosk, audio_bytes
    )
    
    # If the user submitted silence or transcription failed completely
    if not transcript.strip() or "Transcription Failed" in transcript:
     context = {
         "request": request,
         "transcript": "No speech detected or transcription failed.",
         "score": 0,
         "score_label": "N/A",
         "errors": [],
         "corrected_text": "Please try recording again and speak clearly."
     }
     return templates.TemplateResponse("result_partial.html", context)

    # Step 2: Analyze with Gemini (Run in thread pool)
    analysis_data = await loop.run_in_executor(
        None, analyze_grammar, transcript, topic, difficulty
    )
    
    # Step 3: Combine data and return the HTML template
    analysis_data["transcript"] = transcript 
    analysis_data["request"] = request
    
    return templates.TemplateResponse("result_partial.html", analysis_data)