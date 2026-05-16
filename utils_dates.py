from __future__ import annotations

from datetime import date, datetime, timedelta

MIN_ORDER_LEAD_DAYS = 4
_ALLOWED_DATE_FORMATS = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y")


def min_order_date(today: date | None = None) -> date:
    """Earliest allowed pickup/order fulfillment date."""
    return (today or date.today()) + timedelta(days=MIN_ORDER_LEAD_DAYS)


def min_order_date_text(today: date | None = None) -> str:
    return min_order_date(today).strftime("%Y-%m-%d")


def parse_order_date(value: str) -> date | None:
    raw = (value or "").strip()
    if not raw:
        return None
    for fmt in _ALLOWED_DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    return None


def validate_order_date(value: str, *, required: bool = True) -> tuple[bool, str, date | None]:
    raw = (value or "").strip()
    if not raw:
        if required:
            return False, f"Вкажіть дату у форматі YYYY-MM-DD. Найраніша доступна дата: {min_order_date_text()}", None
        return True, "", None

    parsed = parse_order_date(raw)
    if parsed is None:
        return False, f"Невірний формат дати. Використайте YYYY-MM-DD, наприклад {min_order_date_text()}", None

    earliest = min_order_date()
    if parsed < earliest:
        return False, f"Замовлення можна оформити мінімум за {MIN_ORDER_LEAD_DAYS} дні. Найраніша доступна дата: {earliest.strftime('%Y-%m-%d')}", parsed

    return True, "", parsed
