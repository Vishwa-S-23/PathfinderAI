from __future__ import annotations

from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader


SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "Python": ("python",),
    "Java": ("java", "spring boot"),
    "JavaScript": ("javascript", "react", "node.js"),
    "SQL": ("sql", "mysql", "postgresql"),
    "Machine Learning": ("machine learning", "scikit-learn", "tensorflow"),
    "Data Visualization": ("tableau", "power bi", "matplotlib", "data visualization"),
    "Cloud": ("aws", "azure", "google cloud", "gcp"),
    "Cybersecurity": ("cybersecurity", "security operations", "penetration testing"),
    "Figma": ("figma", "prototyping"),
    "Communication": ("communication", "presented", "stakeholder"),
    "Leadership": ("leadership", "led a", "managed a", "mentored"),
    "Git": ("git", "github", "gitlab"),
}


class ResumeService:
    def analyze(self, filename: str, content: bytes) -> dict[str, object]:
        text = self._extract(filename, content)
        normalized = " ".join(text.lower().split())
        skills = [
            skill
            for skill, aliases in SKILL_ALIASES.items()
            if any(alias in normalized for alias in aliases)
        ]
        strength_signals = {
            "Outcome focused": ("improved", "increased", "reduced", "saved", "%"),
            "Leadership evidence": ("led", "managed", "mentored", "coordinated"),
            "Project experience": ("project", "built", "developed", "implemented"),
            "Collaboration": ("team", "stakeholder", "cross-functional", "collaborated"),
        }
        strengths = [
            name
            for name, signals in strength_signals.items()
            if any(signal in normalized for signal in signals)
        ]
        baseline = ["Communication", "Git", "SQL"]
        missing = [skill for skill in baseline if skill not in skills]
        words = len(normalized.split())
        if words < 80:
            summary = "The resume is concise; add project context and measurable outcomes where evidence is thin."
        elif words > 1200:
            summary = "The resume is detailed; tighten it around the target role and keep the strongest evidence first."
        else:
            summary = "The resume has a workable evidence base. Tailor the skills and outcomes to each target career."
        return {
            "summary": summary,
            "skills": skills,
            "strengths": strengths or ["Resume structure available for review"],
            "missing_skills": missing,
            "word_count": words,
        }

    def _extract(self, filename: str, content: bytes) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix == ".pdf":
            reader = PdfReader(BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)[:200_000]
        if suffix == ".docx":
            document = Document(BytesIO(content))
            return "\n".join(paragraph.text for paragraph in document.paragraphs)[:200_000]
        if suffix == ".txt":
            return content.decode("utf-8", errors="replace")[:200_000]
        raise ValueError("Only PDF, DOCX, and TXT resumes are supported")