from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StudentSnapshot(BaseModel):
    academic_performance: float = Field(default=0, ge=0, le=100)
    goals: str = ""
    strengths: str = ""
    weaknesses: str = ""
    interests: list[str] = Field(default_factory=list)
    preferred_environment: str = ""
    technical_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    skill_scores: dict[str, float] = Field(default_factory=dict)
    personality: dict[str, Any] = Field(default_factory=dict)
    aptitude: dict[str, float] = Field(default_factory=dict)


class CareerRecommendation(BaseModel):
    career: str
    score: float = Field(ge=0, le=100)
    reasoning: str
    skill_gaps: list[str]
    model_used: str


class PredictionResponse(BaseModel):
    recommendations: list[CareerRecommendation]
    model_used: str
    model_metrics: dict[str, float]


class RoadmapRequest(BaseModel):
    career: str = Field(min_length=2, max_length=140)
    skill_gaps: list[str] = Field(default_factory=list)
    student: dict[str, Any] = Field(default_factory=dict)


class RoadmapResponse(BaseModel):
    title: str
    summary: str
    milestones: list[dict[str, Any]]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    student_name: str = "Student"
    recommended_careers: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    intent: str


class PersonalityTextRequest(BaseModel):
    text: str = Field(min_length=10, max_length=10000)


class PersonalityTextResponse(BaseModel):
    personality_type: str
    traits: dict[str, float]
    explanation: str