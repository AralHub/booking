from http import HTTPStatus
from typing import Union, Optional

from fastapi import HTTPException, status
from app.core.i18n.translations import ErrorCode


class CustomException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Union[str, None] = None,
        error_code: Optional[ErrorCode] = None,
    ):
        if not detail:  # pragma: no cover
            detail = HTTPStatus(status_code).description
        self.error_code = error_code
        super().__init__(status_code=status_code, detail=detail)


class BadRequestException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        error_code: ErrorCode = ErrorCode.BAD_REQUEST,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code,
        )  # pragma: no cover


class NotFoundException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        error_code: ErrorCode = ErrorCode.NOT_FOUND,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail, error_code=error_code
        )  # pragma: no cover


class ForbiddenException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        error_code: ErrorCode = ErrorCode.FORBIDDEN,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail=detail, error_code=error_code
        )  # pragma: no cover


class UnauthorizedException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        error_code: ErrorCode = ErrorCode.UNAUTHORIZED,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
        )  # pragma: no cover


class UnprocessableEntityException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        error_code: ErrorCode = ErrorCode.UNPROCESSABLE_ENTITY,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code,
        )  # pragma: no cover


class DuplicateValueException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        error_code: ErrorCode = ErrorCode.DUPLICATE_VALUE,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code,
        )


class TooManyRequestsException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        error_code: ErrorCode = ErrorCode.TOO_MANY_REQUESTS,
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code=error_code,
        )  # pragma: no cover
