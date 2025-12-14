from typing import Tuple

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

EMOTION_RU = {
    "admiration": "восхищение",
    "amusement": "веселье",
    "anger": "злость",
    "annoyance": "раздражение",
    "approval": "одобрение",
    "caring": "забота",
    "confusion": "непонимание",
    "curiosity": "любопытство",
    "desire": "желание",
    "disappointment": "разочарование",
    "disapproval": "неодобрение",
    "disgust": "отвращение",
    "embarrassment": "смущение",
    "excitement": "возбуждение",
    "fear": "страх",
    "gratitude": "признательность",
    "grief": "горе",
    "joy": "радость",
    "love": "любовь",
    "nervousness": "нервозность",
    "optimism": "оптимизм",
    "pride": "гордость",
    "realization": "осознание",
    "relief": "облегчение",
    "remorse": "раскаяние",
    "sadness": "грусть",
    "surprise": "удивление",
    "neutral": "нейтральность",
}

MODEL_NAME = "seara/rubert-base-cased-russian-emotion-detection-ru-go-emotions"


class EmotionModelService:
    """Сервис для классификации эмоций в тексте используя трансформер модель."""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        """
        Инициализация сервиса.

        Args:
            model_name: Название модели из HuggingFace Hub
        """
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model = AutoModelForSequenceClassification.from_pretrained(model_name)

    @staticmethod
    def _softmax(logits: torch.Tensor) -> torch.Tensor:
        """Численно стабильная реализация softmax."""
        exps = torch.exp(logits - logits.max())
        return exps / exps.sum(-1, keepdim=True)

    def classify(self, text: str) -> Tuple[str, float]:
        """
        Классифицирует эмоцию в тексте.

        Args:
            text: Входной текст для анализа

        Returns:
            Кортеж (метка эмоции, вероятность)
        """
        inputs = self._tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self._model(**inputs)
        probs = self._softmax(outputs.logits)[0]
        score, idx = torch.max(probs, dim=0)
        label = self._model.config.id2label[int(idx)]
        return label, float(score)

    @staticmethod
    def map_score_to_intensity(score: float) -> str:
        """
        Преобразует вероятность в категорию интенсивности.

        Args:
            score: Вероятность (от 0 до 1)

        Returns:
            Строка: "высокая", "средняя" или "низкая"
        """
        if score >= 0.5:
            return "высокая"
        if score >= 0.3:
            return "средняя"
        return "низкая"

    @staticmethod
    def to_ru(label: str) -> str:
        """
        Переводит метку эмоции с английского на русский.

        Args:
            label: Метка эмоции на английском

        Returns:
            Метка на русском или исходная метка, если перевода нет
        """
        return EMOTION_RU.get(label, label)
