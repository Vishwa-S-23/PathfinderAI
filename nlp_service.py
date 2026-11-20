from __future__ import annotations

from collections import Counter

from nltk.stem import SnowballStemmer
from nltk.tokenize import RegexpTokenizer


class NlpService:
    def __init__(self) -> None:
        self.tokenizer = RegexpTokenizer(r"[A-Za-z][A-Za-z+#.-]*")
        self.stemmer = SnowballStemmer("english")

    def intent(self, text: str) -> str:
        tokens = set(self._tokens(text))
        intents = {
            "resume": {"resume", "cv", "application", "bullet"},
            "skills": {"skill", "learn", "course", "gap", "improve"},
            "roadmap": {"roadmap", "plan", "step", "start", "month"},
            "recommendation": {"career", "recommend", "match", "choose", "path"},
            "interview": {"interview", "question", "prepare", "hiring"},
        }
        stemmed = {self.stemmer.stem(token) for token in tokens}
        for name, keywords in intents.items():
            keyword_stems = {self.stemmer.stem(keyword) for keyword in keywords}
            if stemmed.intersection(keyword_stems):
                return name
        return "general"

    def chat_reply(self, message: str, student_name: str, careers: list[str]) -> tuple[str, str]:
        intent = self.intent(message)
        first_name = student_name.strip().split()[0] if student_name.strip() else "there"
        lead = f"{first_name}, "
        if intent == "skills":
            reply = lead + "choose one high-impact skill gap, learn the foundation, and prove it with a small project. Update your assessment when the project is complete."
        elif intent == "resume":
            reply = lead + "write experience bullets as action, context, and measurable result. Keep the strongest role-relevant skills near the top, then upload the revision for another analysis."
        elif intent == "roadmap":
            reply = lead + "select one recommended path and generate its roadmap. Treat each phase as an experiment: complete the work, collect evidence, and reassess before committing further."
        elif intent == "interview":
            reply = lead + "prepare three project stories that show a challenge, your decision, and the result. Pair them with role fundamentals and one thoughtful question about the team."
        elif intent == "recommendation" and careers:
            reply = lead + "your current leading paths are " + ", ".join(careers[:3]) + ". Compare their skill gaps and test the top two with short projects before deciding."
        elif careers:
            reply = lead + "use your recommendations as hypotheses, not labels. A short real-world project in " + careers[0] + " will give you better evidence for the next decision."
        else:
            reply = lead + "complete all four assessments so I can connect your interests, aptitude, personality, and skills to specific career evidence."
        return reply, intent

    def analyze_personality(self, text: str) -> dict[str, object]:
        tokens = self._tokens(text)
        counts = Counter(tokens)
        lexicons = {
            "openness": {"creative", "curious", "explore", "idea", "learn", "novel", "research"},
            "conscientiousness": {"plan", "organize", "finish", "detail", "reliable", "schedule", "goal"},
            "extraversion": {"team", "lead", "present", "social", "discuss", "network", "speak"},
            "agreeableness": {"help", "support", "listen", "empathy", "cooperate", "care", "mentor"},
            "emotional_stability": {"calm", "adapt", "patient", "resilient", "steady", "reflect", "balance"},
        }
        traits: dict[str, float] = {}
        for trait, words in lexicons.items():
            hits = sum(counts[word] for word in words)
            traits[trait] = round(min(95.0, 48 + hits * 7.5), 1)
        strongest = sorted(traits, key=traits.get, reverse=True)[:2]
        labels = {
            "openness": "Explorer",
            "conscientiousness": "Planner",
            "extraversion": "Connector",
            "agreeableness": "Supporter",
            "emotional_stability": "Steady problem-solver",
        }
        personality_type = " / ".join(labels[trait] for trait in strongest)
        return {
            "personality_type": personality_type,
            "traits": traits,
            "explanation": "Language signals suggest strongest tendencies in "
            + " and ".join(trait.replace("_", " ") for trait in strongest)
            + ". This is guidance, not a clinical assessment.",
        }

    def _tokens(self, text: str) -> list[str]:
        return [token.lower() for token in self.tokenizer.tokenize(text)]