import re
from typing import Dict


class LinguisticAnalyzer:
    """Класс для лингвистического анализа текста и извлечения признаков."""

    def extract_features(self, text: str) -> Dict[str, float]:
        """
        Извлекает лингвистические признаки из текста.

        Возвращает:
            Dict с признаками:
            - length: длина текста
            - exclamations: количество восклицательных знаков
            - questions: количество вопросительных знаков
            - caps_ratio: доля заглавных букв (от 0 до 1)
            - emoticons: количество смайликов
        """
        length = len(text)
        exclamations = text.count("!")
        questions = text.count("?")

        # Доля заглавных букв (для детектирования CapsLock/крика)
        caps = sum(1 for ch in text if ch.isalpha() and ch.isupper())
        letters = sum(1 for ch in text if ch.isalpha())
        caps_ratio = caps / letters if letters > 0 else 0.0

        # Количество смайликов по простому паттерну
        emoticons = len(re.findall(r"[:;]-?[()DP]", text))

        return {
            "length": length,
            "exclamations": exclamations,
            "questions": questions,
            "caps_ratio": round(caps_ratio, 3),
            "emoticons": emoticons,
        }