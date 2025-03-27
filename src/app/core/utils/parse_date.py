from datetime import date, datetime, time

from app.core.exceptions.http_exceptions import BadRequestException
from app.core.i18n.translations import ErrorCode


def parse_date(date_str: str) -> date:
    # Replace dot with hyphen for parsing
    try:
        if "." in date_str:
            date_str = date_str.replace(".", "-")
        return date.fromisoformat(date_str)
    except ValueError:
        raise BadRequestException(
            error_code=ErrorCode.INVALID_DATE_FORMAT,
        )


def parse_time(time_str: str) -> time:
    return datetime.strptime(time_str, "%H:%M").time()
