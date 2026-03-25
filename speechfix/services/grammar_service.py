"""
Grammar & communication analysis service — Google Gemini Flash.

"""

import json
import logging

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


class AnalysisResult(BaseModel):
    score: int
    score_label: str
    errors: list[GrammarError]
    corrected_text: str


def analyze_grammar(transcript: str, topic: str, difficulty: str) -> dict:
    """
    Sends the transcript to Gemini Flash and returns a structured dict
    matching AnalysisResult.  Falls back to a safe default on any error.
    """
    prompt = f"""
                You are an expert English teacher and technical interviewer evaluating a candidate's spoken response.
                
                Interview Context:
                - Topic: {topic}
                - Difficulty: {difficulty}
                
                Candidate's Spoken Answer (transcribed by AI):
                "{transcript}"
                
                Evaluate the answer for grammar, clarity, and relevance to the topic.
                - Give a score from 0 to 100.
                - Identify specific grammatical errors or technical mistakes.
                - Identify the answer is correct and related to the topic or question.
                - Explain why each error is wrong.
                - Provide a fully corrected, professional version of the answer.
                """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AnalysisResult,
                temperature=0.7,
            ),
        )
        data = json.loads(response.text)
        logger.info("Grammar analysis complete: score=%s", data.get("score"))
        return data

    except Exception as exc:
        logger.error("Grammar analysis error: %s", exc, exc_info=True)
        return {
            "score": 0,
            "score_label": "Analysis Failed",
            "errors": [],
            "corrected_text": "Unable to connect to AI for evaluation. Please try again.",
        }
