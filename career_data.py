from __future__ import annotations

from dataclasses import dataclass


DOMAIN_FEATURES = (
    "technology",
    "data",
    "design",
    "business",
    "healthcare",
    "engineering",
    "finance",
    "cybersecurity",
)

FEATURE_NAMES = DOMAIN_FEATURES + (
    "numerical",
    "verbal",
    "logical",
    "spatial",
    "openness",
    "conscientiousness",
    "extraversion",
    "agreeableness",
    "emotional_stability",
    "academic",
)

DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "technology": ("software", "code", "coding", "java", "javascript", "git", "web", "app", "technology"),
    "data": ("data", "python", "sql", "statistics", "machine learning", "research", "analysis", "ai"),
    "design": ("design", "creative", "figma", "prototype", "user research", "visual", "accessibility"),
    "business": ("business", "product", "strategy", "leadership", "customer", "market", "prioritize"),
    "healthcare": ("health", "psychology", "people", "counsel", "empathy", "biology", "wellbeing"),
    "engineering": ("engineering", "physics", "energy", "cad", "build", "systems", "mathematics"),
    "finance": ("finance", "accounting", "investment", "excel", "economics", "financial", "risk"),
    "cybersecurity": ("security", "cyber", "network", "linux", "threat", "privacy", "risk"),
}


@dataclass(frozen=True)
class CareerProfile:
    title: str
    category: str
    required_skills: tuple[str, ...]
    centers: dict[str, float]


CAREER_PROFILES = (
    CareerProfile(
        "Data Scientist",
        "data",
        ("Python", "SQL", "Statistics", "Machine Learning", "Data Visualization"),
        {"data": 0.95, "technology": 0.72, "numerical": 0.92, "logical": 0.88, "openness": 0.82, "academic": 0.78},
    ),
    CareerProfile(
        "Software Engineer",
        "technology",
        ("Java", "JavaScript", "Git", "Databases", "Problem Solving"),
        {"technology": 0.96, "data": 0.52, "logical": 0.92, "numerical": 0.74, "conscientiousness": 0.78, "academic": 0.72},
    ),
    CareerProfile(
        "UX Designer",
        "design",
        ("User Research", "Figma", "Prototyping", "Accessibility", "Communication"),
        {"design": 0.96, "verbal": 0.79, "spatial": 0.84, "openness": 0.92, "agreeableness": 0.74, "extraversion": 0.66},
    ),
    CareerProfile(
        "Cybersecurity Analyst",
        "cybersecurity",
        ("Networking", "Linux", "Security Operations", "Python", "Risk Analysis"),
        {"cybersecurity": 0.96, "technology": 0.82, "logical": 0.91, "conscientiousness": 0.88, "numerical": 0.68, "academic": 0.7},
    ),
    CareerProfile(
        "Product Manager",
        "business",
        ("Product Strategy", "Analytics", "Communication", "Research", "Prioritization"),
        {"business": 0.95, "technology": 0.55, "verbal": 0.9, "extraversion": 0.8, "conscientiousness": 0.84, "openness": 0.76},
    ),
    CareerProfile(
        "Clinical Psychologist",
        "healthcare",
        ("Psychology", "Active Listening", "Research", "Ethics", "Communication"),
        {"healthcare": 0.96, "verbal": 0.88, "agreeableness": 0.94, "emotional_stability": 0.82, "openness": 0.74, "academic": 0.84},
    ),
    CareerProfile(
        "Renewable Energy Engineer",
        "engineering",
        ("Mathematics", "Physics", "CAD", "Energy Systems", "Project Management"),
        {"engineering": 0.96, "numerical": 0.92, "spatial": 0.88, "logical": 0.84, "conscientiousness": 0.8, "academic": 0.82},
    ),
    CareerProfile(
        "Financial Analyst",
        "finance",
        ("Excel", "Accounting", "Statistics", "Financial Modeling", "Communication"),
        {"finance": 0.96, "numerical": 0.92, "logical": 0.8, "conscientiousness": 0.9, "verbal": 0.68, "academic": 0.76},
    ),
)

CAREERS_BY_TITLE = {profile.title.lower(): profile for profile in CAREER_PROFILES}