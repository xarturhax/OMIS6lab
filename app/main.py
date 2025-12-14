from datetime import datetime
from typing import List, Optional, Tuple

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .emotion_model import EmotionModelService
from .linguistics import LinguisticAnalyzer
from .models import (
    AnalyzeResponse,
    EmotionResult,
    HistoryItem,
    HistoryRepository,
    ScenarioResult,
)
from .preprocessing import TextPreprocessor
from .scenarios import ScenarioEngine

app = FastAPI(title="Система анализа эмоций")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class AuthService:
    """Сервис аутентификации и работы с сессиями пользователя."""

    def __init__(self, session_cookie_name: str = "emo_user") -> None:
        """
        Инициализация сервиса.

        Args:
            session_cookie_name: Имя куки для сохранения сессии
        """
        self._cookie_name = session_cookie_name

    @property
    def cookie_name(self) -> str:
        """Получить имя куки."""
        return self._cookie_name

    def get_current_user(self, request: Request) -> Optional[str]:
        """
        Получить текущего пользователя из куки.

        Args:
            request: FastAPI Request объект

        Returns:
            Имя пользователя или None
        """
        return request.cookies.get(self._cookie_name)

    def login(self, username: str, password: str) -> Optional[str]:
        """
        Проверить учётные данные пользователя.

        Args:
            username: Имя пользователя
            password: Пароль

        Returns:
            Имя пользователя если успешно, иначе None
        """
        if username == "admin" and password == "admin":
            return username
        return None

    def set_user_cookie(self, response: RedirectResponse, username: str) -> None:
        """
        Установить куки пользователя.

        Args:
            response: FastAPI Response объект
            username: Имя пользователя
        """
        response.set_cookie(self._cookie_name, username)

    def clear_user_cookie(self, response: RedirectResponse) -> None:
        """
        Удалить куки пользователя.

        Args:
            response: FastAPI Response объект
        """
        response.delete_cookie(self._cookie_name)


class EmotionAnalysisService:
    """Фасад, объединяющий все компоненты для анализа эмоций в тексте."""

    def __init__(
            self,
            preprocessor: TextPreprocessor,
            linguistics: LinguisticAnalyzer,
            emotion_model: EmotionModelService,
            scenarios: ScenarioEngine,
    ) -> None:
        """
        Инициализация сервиса.

        Args:
            preprocessor: Сервис предобработки текста
            linguistics: Сервис лингвистического анализа
            emotion_model: Сервис классификации эмоций
            scenarios: Сервис обработки сценариев
        """
        self._preprocessor = preprocessor
        self._linguistics = linguistics
        self._emotion_model = emotion_model
        self._scenarios = scenarios

    def analyze_text(self, raw_text: str) -> Tuple[AnalyzeResponse, dict, str]:
        """
        Полный анализ текста от предобработки до генерации сценариев.

        Args:
            raw_text: Исходный текст для анализа

        Returns:
            Кортеж (AnalyzeResponse, shares, intensity)
        """
        # Предобработка
        cleaned = self._preprocessor.preprocess(raw_text)

        # Лингвистический анализ
        features = self._linguistics.extract_features(cleaned)

        # Классификация эмоций
        label, score = self._emotion_model.classify(cleaned)
        label_ru = self._emotion_model.to_ru(label)
        intensity = self._emotion_model.map_score_to_intensity(score)

        # Анализ полярности
        shares = self._scenarios.polarity_with_lexicon(label, cleaned)

        # Генерация сценариев
        scenario_dict = self._scenarios.build_scenarios_single(label, intensity, cleaned)

        emotion_result = EmotionResult(label=label_ru, score=score, intensity=intensity)
        scenario_result = ScenarioResult(
            for_support=scenario_dict["for_support"],
            for_moderator=scenario_dict["for_moderator"],
            for_marketer=scenario_dict["for_marketer"],
        )

        analyze_response = AnalyzeResponse(
            cleaned_text=cleaned,
            features=features,
            emotion=emotion_result,
            scenarios=scenario_result,
        )

        return analyze_response, shares, intensity


# ==================== Инициализация сервисов ====================

auth_service = AuthService()
preprocessor = TextPreprocessor()
linguistics = LinguisticAnalyzer()
emotion_model_service = EmotionModelService()
scenario_engine = ScenarioEngine()
analysis_service = EmotionAnalysisService(
    preprocessor=preprocessor,
    linguistics=linguistics,
    emotion_model=emotion_model_service,
    scenarios=scenario_engine,
)
history_repo = HistoryRepository(max_size=20)


# ==================== Маршруты ====================


@app.get("/", response_class=HTMLResponse)
async def root() -> RedirectResponse:
    """Главная страница перенаправляет на логин."""
    return RedirectResponse("/login")


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request) -> HTMLResponse:
    """Отображение формы логина."""
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "user": None, "error": None},
    )


@app.post("/login", response_class=HTMLResponse)
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
) -> HTMLResponse:
    """Обработка логина."""
    user = auth_service.login(username, password)
    if user:
        resp = RedirectResponse(url="/analyze-form", status_code=302)
        auth_service.set_user_cookie(resp, user)
        return resp

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "user": None, "error": "Неверный логин или пароль"},
    )


@app.get("/logout")
async def logout() -> RedirectResponse:
    """Выход из системы."""
    resp = RedirectResponse(url="/login", status_code=302)
    auth_service.clear_user_cookie(resp)
    return resp


@app.get("/analyze-form", response_class=HTMLResponse)
async def analyze_form(request: Request) -> HTMLResponse:
    """Отображение формы анализа."""
    user = auth_service.get_current_user(request)
    if not user:
        return RedirectResponse("/login")

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user},
    )


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, text: str = Form(...)) -> HTMLResponse:
    """Обработка анализа текста."""
    user = auth_service.get_current_user(request)
    if not user:
        return RedirectResponse("/login")

    try:
        analyze_response, shares, intensity = analysis_service.analyze_text(text)

        # Добавление в историю
        item = HistoryItem(
            timestamp=datetime.now(),
            text_short=analyze_response.cleaned_text[:80]
                       + ("..." if len(analyze_response.cleaned_text) > 80 else ""),
            emotion_label=analyze_response.emotion.label,
            intensity=intensity,
            positive=shares["positive"],
            negative=shares["negative"],
        )
        history_repo.add(item)

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "user": user,
                "result": analyze_response,
                "shares": shares,
                "history": history_repo.list(),
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "user": user},
            status_code=500,
        )


@app.get("/history", response_class=HTMLResponse)
async def history_view(request: Request) -> HTMLResponse:
    """Отображение истории анализов."""
    user = auth_service.get_current_user(request)
    if not user:
        return RedirectResponse("/login")

    return templates.TemplateResponse(
        "history.html",
        {"request": request, "user": user, "history": history_repo.list()},
    )