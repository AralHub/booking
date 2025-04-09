from typing import Optional

from fastapi import status

from app.core.i18n.translations import ErrorCode, get_error_message


class CustomException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail or (
            get_error_message(error_code, "en")
            if error_code
            else "Something went wrong"
        )

    @classmethod
    def from_error_code(
        cls,
        error_code: ErrorCode,
        status_code: Optional[int] = None,
    ):
        """Создает исключение из кода ошибки, используя стандартный статус код для класса"""
        instance = cls.__new__(cls)
        instance.error_code = error_code
        instance.detail = get_error_message(error_code, "en")
        instance.status_code = status_code or cls._default_status_code
        return instance


class BadRequestException(CustomException):
    _default_status_code = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
        detail: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(
            status_code=self._default_status_code,
            detail=detail,
            error_code=error_code,
        )


class NotFoundException(CustomException):
    _default_status_code = status.HTTP_404_NOT_FOUND

    def __init__(
        self,
        detail: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(
            status_code=self._default_status_code,
            detail=detail,
            error_code=error_code,
        )


class ForbiddenException(CustomException):
    _default_status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, detail: Optional[str] = None, error_code: Optional[str] = None):
        super().__init__(
            status_code=self._default_status_code,
            detail=detail,
            error_code=error_code,
        )


class UnauthorizedException(CustomException):
    _default_status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(
        self,
        detail: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(
            status_code=self._default_status_code,
            detail=detail,
            error_code=error_code,
        )


class UnprocessableEntityException(CustomException):
    _default_status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(
        self,
        detail: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(
            status_code=self._default_status_code,
            detail=detail,
            error_code=error_code,
        )


class DuplicateValueException(CustomException):
    _default_status_code = status.HTTP_409_CONFLICT

    def __init__(
        self,
        detail: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(
            status_code=self._default_status_code,
            detail=detail,
            error_code=error_code,
        )


class TooManyRequestsException(CustomException):
    _default_status_code = status.HTTP_429_TOO_MANY_REQUESTS

    def __init__(
        self,
        detail: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(
            status_code=self._default_status_code,
            detail=detail,
            error_code=error_code,
        )


# Полезные фабричные функции для часто используемых исключений
def hotel_not_found():
    return NotFoundException.from_error_code(ErrorCode.HOTEL_NOT_FOUND)


def room_not_found():
    return NotFoundException.from_error_code(ErrorCode.ROOM_NOT_FOUND)


def invalid_credentials():
    return UnauthorizedException.from_error_code(ErrorCode.INVALID_CREDENTIALS)


def hotel_access_denied():
    return ForbiddenException.from_error_code(ErrorCode.HOTEL_ACCESS_DENIED)
