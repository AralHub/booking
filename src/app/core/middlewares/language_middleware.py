import json
from collections.abc import Callable
from typing import Any, Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions.http_exceptions import CustomException
from app.core.i18n.translations import ErrorCode, get_error_message
from app.core.logger import logging

logger = logging.getLogger(__name__)


class LanguageMiddleware(BaseHTTPMiddleware):
    """
    Middleware для обработки многоязычности в API.
    - Определяет язык запроса
    - Переводит сообщения об ошибках
    - Позволяет переводить ответы API
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        # Определяем язык из запроса
        language = self._get_language(request)

        # Сохраняем язык в state для доступа из обработчиков
        request.state.language = language
        logger.info(f"Request language: {language}")

        try:
            # Вызываем следующий обработчик
            response = await call_next(request)

            # Обрабатываем успешный ответ (например, для перевода)
            if response.headers.get("content-type") == "application/json":
                content = await self._get_response_content(response)
                if content:
                    return await self._create_localized_response(
                        response, content, language
                    )

            return response

        except CustomException as e:
            # Явно перехватываем наши кастомные исключения
            logger.info(
                f"Processing CustomException: {type(e).__name__}, error_code={getattr(e, 'error_code', None)}"
            )
            return self._handle_custom_exception(e, language)

        except Exception as e:
            # Обрабатываем любые другие исключения
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            return self._handle_unexpected_exception(e, language)

    def _get_language(self, request: Request) -> str:
        """Определяет язык запроса на основе query параметров и заголовков."""
        # Сначала проверяем query параметр
        lang_param = request.query_params.get("lang")
        if lang_param and lang_param in ["ru", "en"]:
            return lang_param

        # Затем проверяем заголовок Accept-Language
        accept_language = request.headers.get("Accept-Language", "")
        if accept_language:
            # Простая обработка Accept-Language
            languages = [
                lang.strip().split(";")[0].lower()
                for lang in accept_language.split(",")
            ]
            for lang in languages:
                lang_code = lang[:2]
                if lang_code in ["ru", "en"]:
                    return lang_code

        # Язык по умолчанию
        return "ru"

    async def _get_response_content(
        self, response: Response
    ) -> Optional[dict[str, Any]]:
        """Извлекает JSON-содержимое из ответа."""
        if not hasattr(response, "body_iterator"):
            return None

        # Собираем тело ответа
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        if not body:
            return None

        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    async def _create_localized_response(
        self, original_response: Response, content: dict[str, Any], language: str
    ) -> Response:
        """Создает локализованный ответ на основе контента и языка."""

        # Фильтруем многоязычные поля
        def filter_multilingual_fields(obj):
            if isinstance(obj, dict):
                for key, value in list(obj.items()):
                    if key in ["name", "description"] and isinstance(value, dict):
                        obj[key] = value.get(
                            language,
                            value.get("en", next(iter(value.values()), "")),
                        )
                    elif isinstance(value, (dict | list)):
                        filter_multilingual_fields(value)
            elif isinstance(obj, list):
                for item in obj:
                    filter_multilingual_fields(item)

        # Копируем контент перед изменением
        filtered_content = content.copy() if content else {}
        filter_multilingual_fields(filtered_content)

        # Создаем полностью новый ответ
        return JSONResponse(
            content=filtered_content,
            status_code=original_response.status_code,
            headers={
                k: v
                for k, v in original_response.headers.items()
                if k.lower() not in ["content-length", "content-encoding"]
            },
        )

    def _handle_custom_exception(
        self, exception: CustomException, language: str
    ) -> JSONResponse:
        """Обрабатывает пользовательские исключения с переводом."""
        # Получаем код ошибки из исключения
        error_code = getattr(exception, "error_code", None)

        # Определяем текст сообщения об ошибке
        if error_code:
            # Если есть код ошибки, используем перевод
            detail = get_error_message(error_code, language)
            logger.info(
                f"Translated error: {detail} (code={error_code}, lang={language})"
            )
        else:
            # Иначе используем исходное сообщение
            detail = exception.detail

        # Создаем и возвращаем JSON-ответ
        content = {"status": "error", "detail": detail}
        if error_code:
            content["error_code"] = error_code

        return JSONResponse(
            status_code=exception.status_code,
            content=content,
        )

    def _handle_unexpected_exception(
        self, exception: Exception, language: str
    ) -> JSONResponse:
        """Обрабатывает неожиданные исключения."""
        # Для безопасности используем общее сообщение об ошибке сервера
        detail = get_error_message(ErrorCode.INTERNAL_SERVER_ERROR, language)

        # В продакшене можно скрыть реальную ошибку,
        # а в разработке - добавить больше информации
        content = {
            "status": "error",
            "detail": detail,
            "error_code": ErrorCode.INTERNAL_SERVER_ERROR,
        }

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
        )
