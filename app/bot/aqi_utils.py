"""
Утилиты для получения цвета и описания по значению AQI (1-5).
Шкала: 1 (зелёный, очень хорошее) → 5 (красный, очень плохое).
"""


def get_aqi_info(aqi_value: int) -> dict:
    """
    Возвращает словарь с цветом (эмодзи) и текстовым описанием для AQI.

    :param aqi_value: значение AQI от 1 до 5
    :return: {"emoji": str, "description": str}
    """
    aqi_map = {
        1: {"emoji": "🟢", "description": "очень хорошее"},
        2: {"emoji": "🟡", "description": "хорошее"},
        3: {"emoji": "🟠", "description": "умеренное"},
        4: {"emoji": "🔴", "description": "плохое"},
        5: {"emoji": "🟣", "description": "очень плохое"},
    }

    if aqi_value not in aqi_map:
        return {"emoji": "⚪", "description": "неизвестное"}

    return aqi_map[aqi_value]


def format_aqi_message(aqi_value: int, city: str | None = None) -> str:
    """
    Форматирует строку с AQI, цветом и пояснением.

    :param aqi_value: значение AQI от 1 до 5
    :param city: (опционально) название города
    :return: отформатированная строка, например:
             "AQI 1 🟢 (очень хорошее)"
    """
    info = get_aqi_info(aqi_value)
    base = f"AQI {aqi_value} {info['emoji']} ({info['description']})"
    if city:
        return f"{base} — {city}"
    return base
