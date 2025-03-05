from datetime import date


def parse_date(date_str: str) -> date:
    # Replace dot with hyphen for parsing
    if "." in date_str:
        date_str = date_str.replace(".", "-")
    return date.fromisoformat(date_str)
