"""
Interview question generation service — Google Gemini Flash.
Returns a strict JSON object matching the InterviewQuestion schema.
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


class InterviewQuestion(BaseModel):
    question: str
    hint: str
    topic_label: str
    difficulty_label: str


# Service function


def generate_interview_question(topic: str, difficulty: str) -> dict:
    """
    Calls Gemini to generate one scenario-based interview question.
    Returns a dict matching InterviewQuestion, or a safe fallback on error.
    """
    prompt = f"""
                You are a highly experienced technical interviewer with 10+ years of hiring experience
                for roles such as Data Engineer, AI/ML Engineer, and Software Developer.

                Generate EXACTLY ONE interview question based on:
                - Topic: {topic}
                - Difficulty: {difficulty}

                The candidate has experience with:
                Python, Go, Django, FastAPI, SQL (PostgreSQL, MySQL),
                GitHub Actions, REST APIs, AI & AI APIs,
                Data Engineering (Pandas, ETL), Docker, Cloud basics.

                QUESTION RULES:
                1. One practical, real-world, scenario-based question.
                2. Difficulty adjustment:
                   - Easy   → basic conceptual understanding
                   - Medium → real-world task or design decision
                   - Hard   → system design, edge cases, or optimization
                3. Style per topic:
                   - Technical       → code logic, API design, SQL, pipelines, Docker
                   - Situational     → "What would you do if…" production scenarios
                   - Leadership      → team conflicts, mentoring, ownership
                   - Communication   → explain concepts clearly, stakeholder updates
                   - Problem Solving → fix broken logic, optimise slow queries or APIs

                OUTPUT FORMAT — strict JSON, no markdown, no extra text:
                {{
                  "question":         "<one interview question>",
                  "hint":             "<one-sentence practical hint>",
                  "topic_label":      "<human-readable topic, e.g. 'Technical'>",
                  "difficulty_label": "<human-readable difficulty, e.g. 'Easy'>"
                }}
            """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InterviewQuestion,
                temperature=0.7,
            ),
        )
        data = json.loads(response.text)
        logger.info("Question generated: topic=%s difficulty=%s", topic, difficulty)
        return data

    except Exception as exc:
        logger.error("Question generation error: %s", exc, exc_info=True)
        # Safe fallback — the app continues without Gemini
        return {
            "question": (
                f"Tell me about a time you had to handle a {difficulty} situation "
                f"related to {topic}."
            ),
            "hint": "Use the STAR method: Situation, Task, Action, Result.",
            "topic_label": topic.replace("_", " ").title(),
            "difficulty_label": difficulty.capitalize(),
        }
