from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, PendingRollbackError, ProgrammingError
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.logger import logging

logger = logging.getLogger(__name__)


class ErrorHandleMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> JSONResponse:
        try:
            return await call_next(request)
        except (PendingRollbackError, ProgrammingError) as e:
            original_error = getattr(
                e, "orig", e
            )  # Если это ProgrammingError, используем саму ошибку

            # Обработка ошибок SQL
            if isinstance(
                original_error, ProgrammingError
            ) or "UndefinedColumnError" in str(original_error):
                error_message = str(original_error)

                # Обработка отсутствующей колонки
                if "column" in error_message and "does not exist" in error_message:
                    column_name = (
                        error_message.split("column")[1]
                        .split("does not exist")[0]
                        .strip()
                    )
                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content={
                            "detail": [
                                {
                                    "type": "database_schema_error",
                                    "loc": ["database"],
                                    "msg": f"Database column {column_name} is missing. Please run migrations.",
                                    "input": None,
                                }
                            ]
                        },
                    )

            # Обработка IntegrityError
            if isinstance(original_error, IntegrityError):
                error_message = str(original_error.orig)

                if "violates foreign key constraint" in error_message:
                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content={
                            "detail": [
                                {
                                    "type": "foreign_key_violation",
                                    "loc": ["body"],
                                    "msg": "Referenced record does not exist",
                                    "input": None,
                                }
                            ]
                        },
                    )

                if "unique constraint" in error_message:
                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content={
                            "detail": [
                                {
                                    "type": "unique_violation",
                                    "loc": ["body"],
                                    "msg": "Record with this value already exists",
                                    "input": None,
                                }
                            ]
                        },
                    )

            # Общая ошибка для необработанных случаев
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "detail": [
                        {
                            "type": "database_error",
                            "loc": ["database"],
                            "msg": "Database operation failed",
                            "input": None,
                        }
                    ]
                },
            )

        except Exception as e:
            # Логируем оригинальную ошибку для отладки
            print(f"Original error: {str(e)}")
            logger.error(f"Original error: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "detail": [
                        {
                            "type": "database_error",
                            "loc": ["database"],
                            "msg": "Database operation failed",
                            "input": None,
                        }
                    ]
                },
            )


# from collections.abc import Callable

# from fastapi import Request
# from starlette.middleware.base import BaseHTTPMiddleware

# from app.core.logger import logging

# logger = logging.getLogger(__name__)


# class ErrorHandleMiddleware(BaseHTTPMiddleware):
#     async def dispatch(
#         self,
#         request: Request,
#         call_next: Callable,
#     ):
#         try:
#             return await call_next(request)

#         except Exception as e:
#             logging.error(f"Server error: {str(e)}", exc_info=True)
#             raise
