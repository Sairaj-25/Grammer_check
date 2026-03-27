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


class TechnicalError(BaseModel):
    original: str
    corrected: str
    explanation: str


class AnalysisResult(BaseModel):
    score: int
    score_label: str
    errors: list[GrammarError]
    technical_errors: list[TechnicalError]
    corrected_text: str


def analyze_grammar(transcript: str, topic: str, difficulty: str) -> dict:
    """
    Sends the transcript to Gemini Flash and returns a structured dict
    matching AnalysisResult.  Falls back to a safe default on any error.
    """
    prompt = f"""
                You are an expert English teacher and senior technical interviewer with deep expertise in software engineering and backend development. You are evaluating a candidate's spoken response in a structured technical interview.
                
                ═══════════════════════════════════════════════════════
                INTERVIEW CONTEXT
                ═══════════════════════════════════════════════════════
                - Topic Category : {topic}

                - Difficulty Level: {difficulty}

                
                ═══════════════════════════════════════════════════════
                CANDIDATE'S TRANSCRIBED SPOKEN ANSWER
                ═══════════════════════════════════════════════════════
                "{transcript}"
                
                Note: This answer was captured via speech-to-text. Ignore punctuation
                errors (commas, periods, capitalisation) as these are transcription
                artefacts, not candidate mistakes.
                
                ═══════════════════════════════════════════════════════
                EVALUATION INSTRUCTIONS
                ═══════════════════════════════════════════════════════
                
                Evaluate the answer across the four dimensions below. Be precise,
                constructive, and technically accurate. Cite the candidate's exact
                words when pointing out errors.
                
                ────────────────────────────────────────────────────────
                1. GRAMMAR & LANGUAGE
                ────────────────────────────────────────────────────────
                - Identify grammatical errors (tense, subject-verb agreement, article
                  usage, prepositions, word choice).
                - IGNORE all punctuation mistakes — these are transcription artefacts.
                - For each error:
                    • Quote the incorrect phrase from the transcript.
                    • Explain WHY it is grammatically wrong.
                    • Provide the corrected version.
                - Assess fluency, coherence, and professional vocabulary usage.
                
                ────────────────────────────────────────────────────────
                2. TECHNICAL ACCURACY
                ────────────────────────────────────────────────────────
                Evaluate based on the specific topic domain:
                
                  PYTHON       → OOP, decorators, generators, async/await, typing,
                                 standard library, performance, Pythonic idioms.
                  GO           → Goroutines, channels, interfaces, error handling,
                                 Go modules, concurrency patterns.
                  DJANGO       → ORM, views, middleware, signals, migrations,
                                 authentication, REST with DRF.
                  FASTAPI      → Pydantic models, dependency injection, async
                                 endpoints, OpenAPI docs, background tasks.
                  SQL          → Joins, indexing, transactions, ACID, window
                  (PG/MySQL)     functions, query optimisation, constraints.
                  GITHUB       → Workflow YAML syntax, triggers, jobs, steps,
                  ACTIONS        runners, secrets, matrix builds, caching, artefacts.
                  REST APIs    → HTTP methods, status codes, idempotency, versioning,
                                 authentication (JWT/OAuth), pagination, rate limiting.
                  AI & AI APIs → Prompt engineering, tokens, embeddings, RAG,
                                 OpenAI/Anthropic SDK usage, streaming, tool calling.
                  DATA ENG.    → Pandas (DataFrames, groupby, merge, vectorisation),
                  (Pandas/ETL)   ETL pipeline design, data cleaning, transformations.
                  DOCKER       → Dockerfile best practices, layering, multi-stage
                                 builds, Compose, volumes, networking, registries.
                  CLOUD BASICS → IaaS/PaaS/SaaS, compute/storage/networking
                                 primitives, IAM, scalability, managed services.
                
                For each technical mistake:
                  • Quote the incorrect statement.
                  • Explain the correct concept with a brief example if needed.
                  • Rate severity: [Minor | Moderate | Critical]
                
                ────────────────────────────────────────────────────────
                3. RELEVANCE & COMPLETENESS
                ────────────────────────────────────────────────────────
                Evaluate based on question category:
                
                  TECHNICAL     → Did the candidate answer the core concept correctly?
                                  Were edge cases, trade-offs, or alternatives mentioned?
                  SITUATIONAL   → Did the candidate describe a real/plausible scenario?
                                  Was the STAR method (Situation-Task-Action-Result) used?
                  COMMUNICATION → Was the explanation clear for the target audience?
                                  Was jargon defined? Was structure logical?
                  PROBLEM       → Did the candidate show a structured thinking approach?
                  SOLVING         Were assumptions stated? Was complexity considered?
                
                - State whether the answer is: Fully Relevant | Partially Relevant | Off-Topic
                - Identify any critical missing points the candidate should have covered.
                
                ────────────────────────────────────────────────────────
                4. CLARITY & DELIVERY
                ────────────────────────────────────────────────────────
                - Was the answer well-structured (intro → explanation → conclusion)?
                - Was it concise or unnecessarily verbose?
                - Did the candidate use examples or analogies effectively?
                - Was the tone professional and confident?
                
                ═══════════════════════════════════════════════════════
                OUTPUT FORMAT
                ═══════════════════════════════════════════════════════
                Return your evaluation in EXACTLY this structure:
                
                ---

                
                ## ⚙️ TECHNICAL ERRORS
                
                For each error:
                - **Candidate said:** "…"
                - **Issue:** [Technical explanation]
                - **Severity:** Minor | Moderate | Critical
                - **Correct Explanation:** "…" *(+ code snippet if helpful)*
                
                *If no technical errors:* "Technically accurate answer."
                
                ---
                
                ## RELEVANCE ASSESSMENT
                
                - **Verdict:** Fully Relevant | Partially Relevant | Off-Topic
                - **What was covered well:** …
                - **What was missing or incomplete:** …
                - **Category-specific note (STAR / structure / trade-offs):** …
                
                ---
                
                ## CLARITY & DELIVERY NOTES
                
                …
                
                ---
                
                ## MODEL ANSWER
                
                *A fully corrected, professional, and complete answer a strong
                candidate would give — in natural spoken English suitable for
                an interview, covering all key points at the {difficulty} level.*
                
                "…"
                
                ---
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
            "technical_errors": [],
            "corrected_text": "Unable to connect to AI for evaluation. Please try again.",
        }
