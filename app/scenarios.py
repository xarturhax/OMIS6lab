from typing import Dict


class ScenarioEngine:
    """Класс для обработки различных сценариев анализа текста и вычисления полярности."""

    def __init__(self) -> None:
        """Инициализация словарей с ключевыми словами и метками эмоций."""
        self.bad_words = {
            "дурак",
            "дура",
            "идиот",
            "идиотка",
            "глупый",
            "глупая",
            "тупой",
            "тупая",
            "некомпетентный",
            "бездарный",
            "бездарная",
            "бестолковый",
            "бестолковая",
            "плохой специалист",
            "ужасный сервис",
            "отвратительный сервис",
        }

        self.negative_tone_words = {
            "грустно",
            "печально",
            "грусть",
            "одиночество",
            "одиноко",
            "страшно",
            "страх",
            "ужасно",
            "отвратительно",
            "плохо",
            "хуже",
            "ужасный",
            "отвратительный",
            "устал",
            "устала",
            "утомил",
            "утомила",
            "надоел",
            "надоела",
            "надоели",
            "раздражает",
            "раздражение",
            "осадок",
            "неприятное чувство",
            "разочарование",
            "разочарован",
            "разочарована",
            "ненавижу",
            "ненависть",
            "боюсь",
            "тревога",
            "тревожно"
        }

        self.positive_tone_words = {
            "рад",
            "рада",
            "счастлив",
            "счастлива",
            "доволен",
            "довольна",
            "замечательный",
            "замечательная",
            "отличный",
            "отличная",
            "отлично",
            "прекрасный",
            "прекрасная",
            "лучший",
            "теплый день",
            "хорошая погода",
            "подарок",
            "успех",
            "повышение",
            "похвала",
            "благодарен",
            "благодарна",
            "люблю",
            "нравится",
            "спасибо",
            "большое спасибо",
            "огромное спасибо",
            "выручили"
        }

        self.positive_labels = {"joy", "admiration", "JOY", "HAPPINESS"}
        self.negative_labels = {
            "anger",
            "sadness",
            "fear",
            "disgust",
            "annoyance",
            "disappointment",
            "grief",
            "ANGER",
            "SADNESS",
            "FEAR",
            "DISGUST"
        }

    def support_scenario(self, emotion_label: str, intensity: str, text: str) -> str:
        """
        Определяет рекомендацию для сценария поддержки клиентов.

        Args:
            emotion_label: Метка эмоции
            intensity: Интенсивность ("низкая", "средняя", "высокая")
            text: Исходный текст

        Returns:
            Строка с рекомендацией для оператора поддержки
        """
        negative_emotions = {"anger", "sadness", "fear", "disgust", "annoyance",
    "disappointment", "grief", "remorse", "nervousness",
    "ANGER", "SADNESS", "FEAR", "DISGUST"}
        positive_emotions = {"joy", "admiration", "JOY", "HAPPINESS", "gratitude", "love", "optimism"}

        lowered = text.lower()
        has_bad_words = any(bad in lowered for bad in self.bad_words)

        if has_bad_words:
            return (
                "Критичное обращение: клиент использует оскорбления. "
                "Рекомендуется максимально вежливый ответ и при необходимости эскалация на старшего специалиста."
            )

        if emotion_label in negative_emotions and intensity in {"средняя", "высокая"}:
            return "Негативное обращение высокой важности: ответ с сочувствием, уточняющими вопросами и предложением решения."

        if emotion_label in negative_emotions:
            return "Негативное обращение: стоит ответить с сочувствием и предложить возможные варианты решения."

        if emotion_label in positive_emotions:
            return "Положительное обращение: можно усилить позитивное впечатление и поблагодарить клиента."



    def moderator_scenario(self, emotion_label: str, intensity: str, text: str) -> str:
        """
        Определяет рекомендацию для сценария модерации чата.

        Args:
            emotion_label: Метка эмоции
            intensity: Интенсивность эмоции
            text: Исходный текст

        Returns:
            Строка с рекомендацией для модератора
        """
        toxic_emotions = {"ANGER", "DISGUST", "IRRITATION", "ANGER/hostility", "anger"}
        lowered = text.lower()

        if any(bad in lowered for bad in self.bad_words):
            return "Сообщение содержит оскорбления/ненормативную лексику: скрыть из чата и отправить модератору."

        if emotion_label in toxic_emotions and intensity in {"средняя", "высокая"}:
            return "Сообщение потенциально токсично: скрыть из чата и отправить на проверку модератору."

        if emotion_label in toxic_emotions:
            return "Сообщение может содержать негатив: отметить для выборочной проверки."

        return "Сообщение допустимо: оставить в чате."

    def marketer_scenario(self, distribution: Dict[str, float]) -> str:
        """
        Определяет анализ эмоционального фона для маркетинга.

        Args:
            distribution: Словарь с распределением эмоций {"positive": %, "negative": %}

        Returns:
            Строка с рекомендацией для маркетолога
        """
        positive = distribution.get("positive", 0.0)
        negative = distribution.get("negative", 0.0)

        if positive >= 60 and negative <= 20:
            return "Преобладают положительные эмоции: отклик аудитории в целом позитивный."

        if negative >= 60 and positive <= 20:
            return "Преобладают негативные эмоции: стоит подробнее изучить причины недовольства."

        return "Эмоциональный фон смешанный: нужны дополнительные исследования и сегментация отзывов."

    def polarity_with_lexicon(self, label: str, text: str) -> Dict[str, int]:
        """
        Вычисляет позитив/негатив используя метку эмоции и лексический анализ.

        Args:
            label: Метка эмоции из модели
            text: Исходный текст

        Returns:
            Словарь {"positive": %, "negative": %}
        """
        lowered = text.lower()
        pos_votes = 0
        neg_votes = 0

        if label in self.positive_labels:
            pos_votes += 3
        elif label in self.negative_labels:
            neg_votes += 3

        pos_hits = sum(1 for w in self.positive_tone_words if w in lowered)
        neg_hits = sum(1 for w in self.negative_tone_words if w in lowered)

        pos_votes += 2 * pos_hits
        neg_votes += 1 * neg_hits

        total_votes = pos_votes + neg_votes
        if total_votes == 0:
            return {"positive": 0, "negative": 0}

        pos_share = int(round(pos_votes / total_votes * 100))
        neg_share = 100 - pos_share
        return {"positive": pos_share, "negative": neg_share}

    def build_scenarios_single(self, emotion_label: str, intensity: str, text: str) -> Dict[str, str]:
        """
        Собирает все три сценария для одного анализа.

        Args:
            emotion_label: Метка эмоции
            intensity: Интенсивность
            text: Исходный текст

        Returns:
            Словарь с тремя сценариями: for_support, for_moderator, for_marketer
        """
        for_support = self.support_scenario(emotion_label, intensity, text)
        for_moderator = self.moderator_scenario(emotion_label, intensity, text)
        # Используем polarity_with_lexicon для маркетер-сценария
        polarity = self.polarity_with_lexicon(emotion_label, text)
        for_marketer = self.marketer_scenario(polarity)
        return {
            "for_support": for_support,
            "for_moderator": for_moderator,
            "for_marketer": for_marketer,
        }