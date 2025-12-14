import re


class TextPreprocessor:
    """Класс для предобработки и нормализации текста."""

    def normalize_text(self, text: str) -> str:
        """Очистка и базовая нормализация текста."""
        if not text:
            return ""

        # Убираем лишние пробелы
        text = text.strip()
        # Нормализуем переносы строк и множественные пробелы
        text = re.sub(r"\s+", " ", text)
        return text

    def to_lower(self, text: str) -> str:
        """Преобразование текста в нижний регистр."""
        return text.lower()

    def preprocess(self, raw_text: str) -> str:
        """Конвейер предобработки: очистка -> нормализация -> приведение к нижнему регистру."""
        text = self.normalize_text(raw_text)
        text = self.to_lower(text)
        return text