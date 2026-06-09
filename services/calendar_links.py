from datetime import datetime, timedelta
from urllib.parse import urlencode


def _calendar_dates(order_date: str = "") -> str:
    try:
        if order_date:
            start = datetime.strptime(order_date, "%Y-%m-%d").replace(hour=10, minute=0, second=0)
        else:
            start = datetime.now() + timedelta(hours=1)
    except Exception:
        start = datetime.now() + timedelta(hours=1)
    end = start + timedelta(minutes=30)
    return f"{start.strftime('%Y%m%dT%H%M%S')}/{end.strftime('%Y%m%dT%H%M%S')}"


def google_calendar_order_url(
    order_id: int,
    customer_name: str,
    phone: str,
    items_text: str,
    total: float,
    order_date: str = "",
    delivery_method: str = "",
    payment_method: str = "",
    comment: str = "",
) -> str:
    details = (
        f"Клієнт: {customer_name}\n"
        f"Телефон: {phone}\n"
        f"На коли: {order_date or '—'}\n"
        f"Доставка: {delivery_method or '—'}\n"
        f"Оплата: {payment_method or '—'}\n"
        f"Коментар: {comment or '—'}\n\n"
        f"Замовлення:\n{items_text}\n\n"
        f"Сума: {total:.2f} zł"
    )
    params = {
        "action": "TEMPLATE",
        "text": f"Murchik Cakes — замовлення #{order_id}",
        "dates": _calendar_dates(order_date),
        "details": details,
    }
    return "https://calendar.google.com/calendar/render?" + urlencode(params)
