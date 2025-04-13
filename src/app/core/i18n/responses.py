from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


def format_message(
    ru: str,
    en: str,
    kk: str,
    uz: str,
) -> str:
    """Форматирует сообщение для всех языков

    Args:
        ru (str): Текст на русском языке
        en (str): Текст на английском языке
        kk (str): Текст на казахском языке

    Returns:
        str: Отформатированная строка с переводами
    """
    return f"ru: {ru}, en: {en}, kk: {kk}, uz: {uz}"


class BaseResponse(BaseModel):
    """Базовый класс для всех ответов API"""

    success: bool = Field(default=True, description="Статус выполнения запроса")
    message: str = Field(description="Сообщение о результате операции на разных языках")


class ErrorResponse(BaseResponse):
    """Формат ответа для ошибок"""

    success: bool = False
    message: str
    error_code: str | None = None


class DataResponse(BaseModel, Generic[T]):
    """Ответ с данными

    Generic Parameters:
        T: Тип данных в ответе
    """

    data: T = Field(description="Данные ответа")


class ListResponse(BaseModel, Generic[T]):
    """Ответ со списком данных

    Generic Parameters:
        T: Тип элементов в списке
    """

    data: list[T] = Field(default_factory=list, description="Список данных")
    total: int = Field(description="Общее количество элементов")


class PaginatedResponse(BaseModel, Generic[T]):
    """Ответ с пагинацией

    Generic Parameters:
        T: Тип элементов в списке
    """

    data: list[T] = Field(default_factory=list, description="Список данных")
    pagination: dict


# Стандартизированные сообщения об успешных операциях
RESPONSE_MESSAGES = {
    "DATA_FOUND": format_message(
        ru="Данные найдены",
        en="Data found",
        kk="",
        uz="",
    ),
    "DATA_CREATED": format_message(
        ru="Данные созданы",
        en="Data created",
        kk="",
        uz="",
    ),
    "DATA_UPDATED": format_message(
        ru="Данные обновлены",
        en="Data updated",
        kk="",
        uz="",
    ),
    "DATA_DELETED": format_message(
        ru="Данные удалены",
        en="Data deleted",
        kk="",
        uz="",
    ),
    "DATA_NOT_FOUND": format_message(
        ru="Данные не найдены",
        en="Data not found",
        kk="",
        uz="",
    ),
    "AUTH_CODE_SENT": format_message(
        ru="Код верификации успешно отправлен",
        en="Verification code sent successfully",
        kk="",
        uz="",
    ),
    "PHONE_VERIFIED": format_message(
        ru="Номер телефона успешно подтвержден",
        en="Phone number verified successfully",
        kk="",
        uz="",
    ),
    "LOGOUT_SUCCESS": format_message(
        ru="Выход выполнен успешно",
        en="Successfully logged out",
        kk="",
        uz="",
    ),
}
