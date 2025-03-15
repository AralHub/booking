from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.background import BackgroundTask

from app.core.logger import logging
from app.core.i18n.translations import get_error_message, ErrorCode
from app.core.exceptions.http_exceptions import CustomException
import json

logger = logging.getLogger(__name__)


class LanguageMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ):
        # Определить язык из заголовка Accept-Language или параметра запроса
        language = self._get_language(request)

        # Устанавливаем язык в request.state, чтобы он был доступен в обработчиках
        request.state.language = language

        try:
            response = await call_next(request)
            return response

        except CustomException as e:
            # Для пользовательских исключений переводим сообщение об ошибке
            if hasattr(e, "error_code"):
                translated_detail = get_error_message(e.error_code, language)
            else:
                translated_detail = e.detail

            return self._create_error_response(e.status_code, translated_detail)

        except Exception as e:
            logging.error(f"Server error: {str(e)}", exc_info=True)
            # Для непредвиденных исключений используем стандартное сообщение
            generic_error = get_error_message(ErrorCode.INTERNAL_SERVER_ERROR, language)
            return self._create_error_response(500, generic_error)

    def _get_language(self, request: Request) -> str:
        # Получаем язык из query параметров, если указан
        lang_param = request.query_params.get("lang")
        if lang_param:
            return lang_param

        # Получаем язык из заголовка Accept-Language
        accept_language = request.headers.get("Accept-Language", "")

        # Парсинг Accept-Language
        if accept_language:
            # Простая обработка Accept-Language
            # Можно улучшить для обработки q-факторов и подтипов (en-US)
            languages = [
                lang.strip().split(";")[0].lower()
                for lang in accept_language.split(",")
            ]
            for lang in languages:
                # Для упрощения берем только первые 2 символа, чтобы не различать en-US и en-GB
                lang_code = lang[:2]
                if lang_code in ["ru", "en"]:  # Поддерживаемые языки
                    return lang_code

        # Язык по умолчанию
        return "ru"

    def _create_error_response(self, status_code: int, detail: str) -> Response:
        """Создает стандартный формат ответа для ошибок"""
        content = {"status": "error", "detail": detail}

        return Response(
            content=json.dumps(content),
            status_code=status_code,
            media_type="application/json",
        )
