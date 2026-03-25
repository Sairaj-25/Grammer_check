"""
GET /api/v1/questions/generate?topic=X&difficulty=Y
Returns a JSON { question, hint, topic_label, difficulty_label }.
"""

import asyncio
import logging

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from speechfix.services.generate_question_service import generate_interview_question

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/generate")
async def get_question(
    topic: str = Query(default="technical", description="Interview topic"),
    difficulty: str = Query(
        default="easy", description="Difficulty level: easy | medium | hard"
    ),
):
    logger.info("Question request: topic=%s difficulty=%s", topic, difficulty)

    loop = asyncio.get_running_loop()
    result: dict = await loop.run_in_executor(
        None, generate_interview_question, topic, difficulty
    )

    if "error" in result:
        return JSONResponse(status_code=500, content=result)
    return JSONResponse(content=result)
