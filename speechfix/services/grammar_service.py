import json
import logging
import textwrap

from google import genai
from google.genai import types
from pydantic import BaseModel

from speechfix.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
client = genai.Client(api_key=settings.GEMINI_API_KEY)


# Response schema
class GrammarError(BaseModel):
    original: str
    corrected: str
    explanation: str


class TechnicalError(BaseModel):
    original: str
    corrected: str
    explanation: str
    severity: str


class AnalysisResult(BaseModel):
    score: int
    score_label: str
    errors: list[GrammarError]
    technical_errors: list[TechnicalError]
    corrected_text: str


def analyze_grammar(transcript: str, topic: str, difficulty: str) -> dict:
    """
    Sends the transcript to Gemini Flash and returns a structured dict
    matching AnalysisResult. Falls back to a safe default on any error.
    """
    prompt = textwrap.dedent(f"""
        You are an expert English teacher and senior technical interviewer with deep expertise in software engineering. 
        Evaluate the candidate's spoken response in a structured technical interview.

        - Topic Category: {topic}
        - Difficulty Level: {difficulty}
        - Candidate Transcript: "{transcript}"

        EVALUATION GUIDELINES:
        1. Grammar & Fluency: Identify grammatical errors (tense, agreement, word choice). 
           IGNORE all punctuation mistakes (commas, periods, capitalization) as these are transcription artifacts.
        2. Technical Accuracy: Evaluate based on the specific topic domain (e.g., Python, Go, SQL, System Design). 
           Identify any factual inaccuracies, missing edge cases, or poor architectural choices.
        3. Correction: Provide a fully corrected, professional, and complete version of the candidate's answer. 
           It should sound natural for a spoken interview while covering all key points at the {difficulty} level.
        4. Scoring: Assign an overall score out of 100 and a brief score_label (e.g., "Excellent", "Needs Improvement").

        Populate the provided JSON schema strictly based on these findings.
    """)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AnalysisResult,
                temperature=0.2,  # Lowered temperature for more analytical/consistent output
            ),
        )

        # Parse the JSON string returned by the model
        data = json.loads(response.text)
        logger.info("Grammar analysis complete: score=%s", data.get("score"))
        return data

    except Exception as exc:
        logger.error("Grammar analysis error: %s", exc, exc_info=True)
        return {
            "score": 0,
            "score_label": "Analysis Failed",
            "errors": [],
            "technical_errors": [],
            "corrected_text": "Unable to connect to AI for evaluation. Please try again.",
        }
