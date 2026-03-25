"""
API v1 — Central router
All endpoint routers are registered HERE and only here.
main.py includes this single router at prefix /api/v1.

Final URL map:
  GET  /api/v1/questions/generate      → questions.py
  POST /api/v1/speech/analyze          → analysis.py
"""

from fastapi import APIRouter
from speechfix.api.v1.endpoints import analysis, questions

router = APIRouter()


router.include_router(questions.router, prefix="/questions", tags=["Questions"])

router.include_router(analysis.router, prefix="/speech", tags=["Speech Analysis"])
