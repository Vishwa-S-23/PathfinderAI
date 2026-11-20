from __future__ import annotations

from collections.abc import Iterable
from io import BytesIO
import logging
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.base import ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from app.career_data import (
    CAREER_PROFILES,
    CAREERS_BY_TITLE,
    DOMAIN_FEATURES,
    DOMAIN_KEYWORDS,
    FEATURE_NAMES,
    CareerProfile,
)
from app.optional_neural import NeuralPredictor, train_optional_neural
from app.schemas import CareerRecommendation, StudentSnapshot

logger = logging.getLogger(__name__)


class CareerModelService:
    """Trains and serves an explainable ensemble over normalized student features."""

    def __init__(self, dataset_path: str | Path | None = None) -> None:
        self.models: dict[str, ClassifierMixin] = {}
        self.metrics: dict[str, float] = {}
        self.neural: NeuralPredictor | None = None
        self.class_centers: dict[str, dict[str, float]] = {}
        configured_path = dataset_path if dataset_path is not None else os.getenv("MODEL_DATASET_PATH")
        self.dataset_path = Path(configured_path) if configured_path else None
        features, labels = self._synthetic_training_data()
        self._fit(features, labels)
        if self.dataset_path and self.dataset_path.is_file():
            try:
                self.retrain_from_csv(self.dataset_path.read_bytes(), persist=False)
            except (OSError, ValueError):
                logger.exception("Persisted training data is invalid; using the baseline model")

    @property
    def model_name(self) -> str:
        names = "Random Forest + Decision Tree + Naive Bayes + KNN"
        return names + (" + TensorFlow MLP" if self.neural is not None else "")

    def predict(self, snapshot: StudentSnapshot, limit: int = 5) -> list[CareerRecommendation]:
        feature_vector = self.extract_features(snapshot)
        probabilities = self._ensemble_probabilities(feature_vector.reshape(1, -1))[0]
        classes = self._classes()
        ranked = sorted(zip(classes, probabilities, strict=True), key=lambda item: item[1], reverse=True)
        known_skills = {self._normalize(skill) for skill in snapshot.technical_skills + snapshot.soft_skills}
        highest_probability = max(probabilities) if probabilities.size else 1.0

        recommendations: list[CareerRecommendation] = []
        for career_name, probability in ranked[:limit]:
            profile = CAREERS_BY_TITLE.get(career_name.lower())
            if profile is None:
                profile = CareerProfile(
                    title=career_name,
                    category="custom",
                    required_skills=(),
                    centers=self.class_centers.get(career_name, {}),
                )
            required = list(profile.required_skills)
            matched = [skill for skill in required if self._normalize(skill) in known_skills]
            gaps = [skill for skill in required if self._normalize(skill) not in known_skills]
            skill_ratio = len(matched) / len(required) if required else 0
            relative_probability = probability / highest_probability if highest_probability else 0
            score = min(98.0, 58 + relative_probability * 30 + skill_ratio * 10)
            recommendations.append(
                CareerRecommendation(
                    career=career_name,
                    score=round(float(score), 1),
                    reasoning=self._reasoning(profile, feature_vector, matched),
                    skill_gaps=gaps,
                    model_used=self.model_name,
                )
            )
        return recommendations

    def extract_features(self, snapshot: StudentSnapshot) -> NDArray[np.float64]:
        text = " ".join(
            snapshot.interests
            + snapshot.technical_skills
            + snapshot.soft_skills
            + [snapshot.goals, snapshot.strengths, snapshot.preferred_environment]
        ).lower()
        values: dict[str, float] = {}
        for domain, keywords in DOMAIN_KEYWORDS.items():
            hits = sum(1 for keyword in keywords if keyword in text)
            values[domain] = min(1.0, hits / 3)

        aptitude = snapshot.aptitude
        values.update(
            {
                "numerical": self._ratio(aptitude.get("numerical", 50)),
                "verbal": self._ratio(aptitude.get("verbal", 50)),
                "logical": self._ratio(aptitude.get("logical", 50)),
                "spatial": self._ratio(aptitude.get("spatial", 50)),
                "openness": self._ratio(snapshot.personality.get("openness", 50)),
                "conscientiousness": self._ratio(snapshot.personality.get("conscientiousness", 50)),
                "extraversion": self._ratio(snapshot.personality.get("extraversion", 50)),
                "agreeableness": self._ratio(snapshot.personality.get("agreeableness", 50)),
                "emotional_stability": self._ratio(snapshot.personality.get("emotional_stability", 50)),
                "academic": self._ratio(snapshot.academic_performance or 50),
            }
        )
        return np.asarray([values.get(name, 0.5) for name in FEATURE_NAMES], dtype=np.float64)

    def retrain_from_csv(self, content: bytes, persist: bool = True) -> int:
        frame = pd.read_csv(BytesIO(content))
        required_columns = set(FEATURE_NAMES) | {"career"}
        missing = sorted(required_columns.difference(frame.columns))
        if missing:
            raise ValueError("Missing dataset columns: " + ", ".join(missing))
        features = frame.loc[:, FEATURE_NAMES].astype(float).to_numpy(dtype=np.float64)
        if not np.isfinite(features).all():
            raise ValueError("Dataset features must contain only finite numeric values")
        if features.size and (features.min() < 0 or features.max() > 100):
            raise ValueError("Dataset features must use a consistent 0-1 or 0-100 scale")
        if features.size and features.max() > 1:
            features = features / 100
        labels = frame["career"].astype(str).str.strip().to_numpy(dtype=str)
        if any(not label for label in labels):
            raise ValueError("Every dataset row must include a career label")
        if len(np.unique(labels)) < 2 or len(labels) < 20:
            raise ValueError("Dataset must contain at least 20 rows and two career classes")
        _, class_counts = np.unique(labels, return_counts=True)
        if class_counts.min() < 2:
            raise ValueError("Every career class must contain at least two rows")
        state = self._train(features, labels)
        if persist and self.dataset_path:
            self._persist_dataset(content)
        self._activate_state(*state)
        return len(labels)

    def _fit(self, features: NDArray[np.float64], labels: NDArray[np.str_]) -> None:
        self._activate_state(*self._train(features, labels))

    def _train(
        self,
        features: NDArray[np.float64],
        labels: NDArray[np.str_],
    ) -> tuple[
        dict[str, ClassifierMixin],
        dict[str, float],
        NeuralPredictor | None,
        dict[str, dict[str, float]],
    ]:
        class_count = len(np.unique(labels))
        test_rows = max(round(len(labels) * 0.25), class_count)
        train_x, test_x, train_y, test_y = train_test_split(
            features,
            labels,
            test_size=test_rows,
            random_state=42,
            stratify=labels,
        )
        candidates: dict[str, ClassifierMixin] = {
            "random_forest": RandomForestClassifier(n_estimators=240, max_depth=10, random_state=42),
            "decision_tree": DecisionTreeClassifier(max_depth=8, min_samples_leaf=3, random_state=42),
            "naive_bayes": GaussianNB(var_smoothing=0.025),
            "knn": Pipeline(
                [
                    ("scale", StandardScaler()),
                    ("model", KNeighborsClassifier(n_neighbors=7, weights="distance")),
                ]
            ),
        }
        metrics: dict[str, float] = {}
        for name, model in candidates.items():
            model.fit(train_x, train_y)
            metrics[name] = round(float(accuracy_score(test_y, model.predict(test_x))), 4)
            model.fit(features, labels)
        centers = {
            label: dict(zip(FEATURE_NAMES, features[labels == label].mean(axis=0), strict=True))
            for label in np.unique(labels)
        }
        return candidates, metrics, train_optional_neural(features, labels), centers

    def _activate_state(
        self,
        models: dict[str, ClassifierMixin],
        metrics: dict[str, float],
        neural: NeuralPredictor | None,
        centers: dict[str, dict[str, float]],
    ) -> None:
        self.models = models
        self.metrics = metrics
        self.neural = neural
        self.class_centers = centers

    def _persist_dataset(self, content: bytes) -> None:
        if self.dataset_path is None:
            return
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.dataset_path.with_suffix(self.dataset_path.suffix + ".tmp")
        temporary_path.write_bytes(content)
        os.replace(temporary_path, self.dataset_path)

    def _ensemble_probabilities(self, features: NDArray[np.float64]) -> NDArray[np.float64]:
        classes = self._classes()
        weights = {"random_forest": 0.35, "decision_tree": 0.15, "naive_bayes": 0.2, "knn": 0.3}
        combined = np.zeros((features.shape[0], len(classes)), dtype=np.float64)
        for name, model in self.models.items():
            model_classes = np.asarray(model.classes_, dtype=str)
            probabilities = np.asarray(model.predict_proba(features), dtype=np.float64)
            positions = {label: index for index, label in enumerate(model_classes)}
            aligned = np.asarray(
                [[row[positions[label]] for label in classes] for row in probabilities],
                dtype=np.float64,
            )
            combined += aligned * weights[name]
        if self.neural is not None:
            neural_probabilities = self.neural.predict_proba(features)
            positions = {label: index for index, label in enumerate(self.neural.classes)}
            aligned = np.asarray(
                [[row[positions[label]] for label in classes] for row in neural_probabilities],
                dtype=np.float64,
            )
            combined = combined * 0.9 + aligned * 0.1
        return combined

    def _classes(self) -> NDArray[np.str_]:
        return np.asarray(self.models["random_forest"].classes_, dtype=str)

    def _synthetic_training_data(self) -> tuple[NDArray[np.float64], NDArray[np.str_]]:
        random = np.random.default_rng(42)
        rows: list[NDArray[np.float64]] = []
        labels: list[str] = []
        for profile in CAREER_PROFILES:
            center = np.asarray(
                [profile.centers.get(name, 0.12 if name in DOMAIN_FEATURES else 0.55) for name in FEATURE_NAMES],
                dtype=np.float64,
            )
            for _ in range(48):
                rows.append(np.clip(center + random.normal(0, 0.085, len(FEATURE_NAMES)), 0, 1))
                labels.append(profile.title)
        return np.vstack(rows), np.asarray(labels, dtype=str)

    def _reasoning(
        self,
        profile: CareerProfile,
        features: NDArray[np.float64],
        matched_skills: Iterable[str],
    ) -> str:
        feature_values = dict(zip(FEATURE_NAMES, features, strict=True))
        strongest = sorted(profile.centers, key=lambda name: feature_values.get(name, 0), reverse=True)[:2]
        signal_text = " and ".join(name.replace("_", " ") for name in strongest)
        skills = list(matched_skills)
        skill_text = f" Existing evidence in {', '.join(skills[:3])} strengthens the match." if skills else ""
        return f"Your {signal_text} signals align with the typical {profile.title} profile.{skill_text}"

    def _ratio(self, value: Any) -> float:
        try:
            return min(1.0, max(0.0, float(value) / 100))
        except (TypeError, ValueError):
            return 0.5

    def _normalize(self, value: str) -> str:
        return " ".join(value.lower().replace("-", " ").split())