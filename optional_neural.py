from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray


@dataclass
class NeuralPredictor:
    model: Any
    classes: NDArray[np.str_]

    def predict_proba(self, features: NDArray[np.float64]) -> NDArray[np.float64]:
        return np.asarray(self.model.predict(features, verbose=0), dtype=np.float64)


def train_optional_neural(
    features: NDArray[np.float64],
    labels: NDArray[np.str_],
) -> NeuralPredictor | None:
    try:
        import tensorflow as tf
    except ImportError:
        return None

    classes = np.unique(labels)
    class_indexes = {label: index for index, label in enumerate(classes)}
    encoded = np.asarray([class_indexes[label] for label in labels], dtype=np.int64)
    tf.keras.utils.set_random_seed(42)
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(features.shape[1],)),
            tf.keras.layers.Dense(48, activation="relu"),
            tf.keras.layers.Dropout(0.12),
            tf.keras.layers.Dense(24, activation="relu"),
            tf.keras.layers.Dense(len(classes), activation="softmax"),
        ]
    )
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    model.fit(features, encoded, epochs=18, batch_size=32, verbose=0)
    return NeuralPredictor(model=model, classes=classes)