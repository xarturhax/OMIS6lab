from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    text: str


class EmotionResult(BaseModel):
    label: str
    score: float
    intensity: str


class ScenarioResult(BaseModel):
    for_support: str
    for_moderator: str
    for_marketer: str


class AnalyzeResponse(BaseModel):
    cleaned_text: str
    features: Dict[str, float]
    emotion: EmotionResult
    scenarios: ScenarioResult


class HistoryItem(BaseModel):
    timestamp: datetime
    text_short: str
    emotion_label: str
    intensity: str
    positive: int
    negative: int


class HistoryRepository:
    """Репозиторий для управления историей анализов."""

    def __init__(self, max_size: int = 20):
        self._items: List[HistoryItem] = []
        self._max_size = max_size

    def add(self, item: HistoryItem) -> None:
        """Добавить элемент в историю."""
        self._items.insert(0, item)
        if len(self._items) > self._max_size:
            self._items.pop()

    def list(self) -> List[HistoryItem]:
        """Получить список всех элементов истории."""
        return list(self._items)

    def clear(self) -> None:
        """Очистить историю."""
        self._items.clear()

    def size(self) -> int:
        """Получить текущий размер истории."""
        return len(self._items)