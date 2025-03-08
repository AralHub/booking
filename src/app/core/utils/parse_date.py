from datetime import date, datetime, time


def parse_date(date_str: str) -> date:
    # Replace dot with hyphen for parsing
    if "." in date_str:
        date_str = date_str.replace(".", "-")
    return date.fromisoformat(date_str)


def parse_time(time_str: str) -> time:
    return datetime.strptime(time_str, "%H:%M").time()
