from typing import Optional


def validate_result(text: str) -> Optional[int]:
    try:
        result = int(text)
    except (TypeError, ValueError):
        return None

    if result < 1 or result > 24:
        return None
    return result
