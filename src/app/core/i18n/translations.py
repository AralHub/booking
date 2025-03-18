from enum import Enum


class ErrorCode(str, Enum):
    """Коды ошибок для стандартизации сообщений об ошибках"""

    # Общие ошибки
    INTERNAL_SERVER_ERROR = "internal_server_error"
    BAD_REQUEST = "bad_request"
    NOT_FOUND = "not_found"
    FORBIDDEN = "forbidden"
    UNAUTHORIZED = "unauthorized"
    UNPROCESSABLE_ENTITY = "unprocessable_entity"
    DUPLICATE_VALUE = "duplicate_value"
    TOO_MANY_REQUESTS = "too_many_requests"

    # Специфичные ошибки для отеля
    HOTEL_NOT_FOUND = "hotel_not_found"
    AMENITY_NOT_FOUND = "amenity_not_found"
    HOTEL_ACCESS_DENIED = "hotel_access_denied"

    # Специфичные ошибки для пользователя
    USER_NOT_FOUND = "user_not_found"
    INVALID_CREDENTIALS = "invalid_credentials"

    # Специфичные ошибки для номера
    ROOM_NOT_FOUND = "room_not_found"


# Словарь переводов по языкам
ERROR_MESSAGES = {
    "en": {
        ErrorCode.INTERNAL_SERVER_ERROR: "Internal server error",
        ErrorCode.BAD_REQUEST: "Bad request",
        ErrorCode.NOT_FOUND: "Resource not found",
        ErrorCode.FORBIDDEN: "Access forbidden",
        ErrorCode.UNAUTHORIZED: "Unauthorized access",
        ErrorCode.UNPROCESSABLE_ENTITY: "Unprocessable entity",
        ErrorCode.DUPLICATE_VALUE: "Duplicate value",
        ErrorCode.TOO_MANY_REQUESTS: "Too many requests",
        ErrorCode.HOTEL_NOT_FOUND: "Hotel not found",
        ErrorCode.AMENITY_NOT_FOUND: "Amenity not found",
        ErrorCode.HOTEL_ACCESS_DENIED: "You don't have access to this hotel",
        ErrorCode.USER_NOT_FOUND: "User not found",
        ErrorCode.INVALID_CREDENTIALS: "Invalid username or password",
        ErrorCode.ROOM_NOT_FOUND: "Room not found",
    },
    "ru": {
        ErrorCode.INTERNAL_SERVER_ERROR: "Внутренняя ошибка сервера",
        ErrorCode.BAD_REQUEST: "Некорректный запрос",
        ErrorCode.NOT_FOUND: "Ресурс не найден",
        ErrorCode.FORBIDDEN: "Доступ запрещен",
        ErrorCode.UNAUTHORIZED: "Неавторизованный доступ",
        ErrorCode.UNPROCESSABLE_ENTITY: "Невозможно обработать сущность",
        ErrorCode.DUPLICATE_VALUE: "Дублирующееся значение",
        ErrorCode.TOO_MANY_REQUESTS: "Слишком много запросов",
        ErrorCode.HOTEL_NOT_FOUND: "Отель не найден",
        ErrorCode.AMENITY_NOT_FOUND: "Удобство не найдено",
        ErrorCode.HOTEL_ACCESS_DENIED: "У вас нет доступа к этому отелю",
        ErrorCode.USER_NOT_FOUND: "Пользователь не найден",
        ErrorCode.INVALID_CREDENTIALS: "Неверное имя пользователя или пароль",
        ErrorCode.ROOM_NOT_FOUND: "Номер не найден",
    },
    # Можно добавить другие языки
}


def get_error_message(error_code: ErrorCode, language: str = "en") -> str:
    """Получить переведенное сообщение об ошибке по коду ошибки и языку."""
    if language not in ERROR_MESSAGES:
        language = "en"  # Fallback на английский

    return ERROR_MESSAGES[language].get(
        error_code, ERROR_MESSAGES["en"][ErrorCode.INTERNAL_SERVER_ERROR]
    )
