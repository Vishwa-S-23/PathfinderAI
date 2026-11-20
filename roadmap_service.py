from __future__ import annotations

from app.career_data import CAREERS_BY_TITLE
from app.schemas import RoadmapRequest, RoadmapResponse


RESOURCE_MAP: dict[str, list[str]] = {
    "python": ["Python official tutorial", "Kaggle micro-courses"],
    "sql": ["SQLBolt", "Mode SQL tutorial"],
    "statistics": ["Khan Academy statistics", "Seeing Theory"],
    "machine learning": ["scikit-learn user guide", "Google ML Crash Course"],
    "java": ["dev.java learning path", "Spring guides"],
    "figma": ["Figma Learn", "Material Design accessibility guidance"],
    "networking": ["Cisco Skills for All", "Wireshark documentation"],
}


def generate_roadmap(request: RoadmapRequest) -> RoadmapResponse:
    profile = CAREERS_BY_TITLE.get(request.career.lower())
    required = list(profile.required_skills) if profile else []
    gaps = request.skill_gaps or required[:4]
    focus = gaps[:4] or ["Career fundamentals", "Portfolio evidence"]
    resources: list[str] = []
    for skill in focus:
        resources.extend(RESOURCE_MAP.get(skill.lower(), [f"Official {skill} documentation"] ))
    milestones = [
        {
            "phase": 1,
            "title": "Establish the foundation",
            "duration": "Weeks 1-4",
            "objectives": focus[:2],
            "activities": ["Complete focused lessons", "Keep a weekly evidence log"],
            "resources": resources[:3],
            "completed": False,
        },
        {
            "phase": 2,
            "title": "Apply skills in small builds",
            "duration": "Weeks 5-8",
            "objectives": focus[1:3] or focus[:2],
            "activities": ["Build two scoped exercises", "Request peer feedback"],
            "resources": resources[2:5] or resources[:3],
            "completed": False,
        },
        {
            "phase": 3,
            "title": "Create a portfolio case study",
            "duration": "Weeks 9-12",
            "objectives": ["Solve a realistic problem", "Explain decisions and outcomes"],
            "activities": ["Publish one end-to-end project", "Document tradeoffs and results"],
            "resources": ["GitHub project documentation", "Role-specific portfolio examples"],
            "completed": False,
        },
        {
            "phase": 4,
            "title": "Prepare for opportunities",
            "duration": "Weeks 13-16",
            "objectives": ["Targeted resume", "Interview evidence"],
            "activities": ["Run three mock interviews", "Apply to five well-matched opportunities"],
            "resources": ["STAR story worksheet", "PathFinder resume analysis"],
            "completed": False,
        },
    ]
    return RoadmapResponse(
        title=f"{request.career} launch plan",
        summary="A 16-week evidence-driven roadmap focused on your current gaps and a portfolio-ready outcome.",
        milestones=milestones,
    )