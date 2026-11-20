from __future__ import annotations

import hmac
import os
from threading import RLock

from fastapi import FastAPI, File, Header, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from app.model_service import CareerModelService
from app.nlp_service import NlpService
from app.resume_service import ResumeService
from app.roadmap_service import generate_roadmap
from app.schemas import (
    ChatRequest,
    ChatResponse,
    PersonalityTextRequest,
    PersonalityTextResponse,
    PredictionResponse,
    RoadmapRequest,
    RoadmapResponse,
    StudentSnapshot,
)


app = FastAPI(
    title="PathFinder AI Service",
    version="1.0.0",
    description="Career prediction, resume NLP, personality signals, roadmaps, and student guidance.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("BACKEND_ORIGIN", "http://localhost:8080")],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)

model_service = CareerModelService()
nlp_service = NlpService()
resume_service = ResumeService()
model_lock = RLock()


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "PathFinder AI", "status": "ready", "docs": "/docs"}


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "healthy",
        "model": model_service.model_name,
        "tensorflow_enabled": model_service.neural is not None,
        "metrics": model_service.metrics,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(snapshot: StudentSnapshot) -> PredictionResponse:
    with model_lock:
        recommendations = model_service.predict(snapshot)
        return PredictionResponse(
            recommendations=recommendations,
            model_used=model_service.model_name,
            model_metrics=model_service.metrics,
        )


@app.post("/roadmap", response_model=RoadmapResponse)
def roadmap(request: RoadmapRequest) -> RoadmapResponse:
    return generate_roadmap(request)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    reply, intent = nlp_service.chat_reply(
        request.message,
        request.student_name,
        request.recommended_careers,
    )
    return ChatResponse(reply=reply, intent=intent)


@app.post("/personality/analyze", response_model=PersonalityTextResponse)
def personality(request: PersonalityTextRequest) -> PersonalityTextResponse:
    return PersonalityTextResponse.model_validate(nlp_service.analyze_personality(request.text))


@app.post("/resume/analyze")
async def analyze_resume(file: UploadFile = File(...)) -> dict[str, object]:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resume is empty")
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Resume exceeds 10 MB")
    try:
        return resume_service.analyze(file.filename or "resume.txt", content)
    except ValueError as exception:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(exception)) from exception
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Resume could not be parsed") from exception


@app.post("/datasets/retrain")
async def retrain(
    file: UploadFile = File(...),
    x_ai_key: str | None = Header(default=None),
) -> dict[str, object]:
    expected_key = os.getenv("AI_ADMIN_KEY")
    if not expected_key or not x_ai_key or not hmac.compare_digest(expected_key, x_ai_key):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="A valid AI admin key is required")
    content = await file.read()
    try:
        with model_lock:
            rows = model_service.retrain_from_csv(content)
        return {"status": "retrained", "rows": rows, "metrics": model_service.metrics}
    except ValueError as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception)) from exception