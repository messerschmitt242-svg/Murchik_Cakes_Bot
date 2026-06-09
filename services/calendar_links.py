from __future__ import annotations

from datetime import datetime, timedelta
from urllib.parse import urlencode


def _calendar_start(order_date: str = "") -> datetime:
    try:
        if order_date:
            return datetime.strptime(order_date, "%Y-%m-%d").replace(hour=10, minute=0, second=0)
    except Exception:
        pass
    return datetime.now() + timedelta(hours=1)


def _calendar_dates(order_date: str = "") -> str:
    start = _calendar_start(order_date)
    end = start + timedelta(minutes=30)
    return f"{start.strftime('%Y%m%dT%H%M%S')}/{end.strftime('%Y%m%dT%H%M%S')}"


def calendar_order_url(order_id: int, webapp_url: str = "") -> str:
    """Universal calendar URL. On iPhone this opens an .ics file in Apple Calendar."""
    base = (webapp_url or "").strip().rstrip("/")
    if base:
        return f"{base}/api/orders/{int(order_id)}/calendar.ics"
    return ""


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
    """Legacy fallback for old code paths. Prefer calendar_order_url for iPhone/Apple Calendar."""
    details = (
        f"Клієнт: {customer_name}\n"
        f"Телефон: {phone}\n"
        f"На коли: {order_date or '—'}\n"
        f"Доставка: {delivery_method or '—'}\n"
        f"Оплата: {payment_method or '—'}\n"
        f"Коментар: {comment or '—'}\n\n"
        f"Замовлення:\n{items_text}\n\n"
        f"Сума: {float(total or 0):.2f} zł"
    )
    params = {
        "action": "TEMPLATE",
        "text": f"Murchik Cakes — замовлення #{order_id}",
        "dates": _calendar_dates(order_date),
        "details": details,
    }
    return "https://calendar.google.com/calendar/render?" + urlencode(params)


def _ics_escape(value: object) -> str:
    text = "" if value is None else str(value)
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\n", "\\n")
    )


def build_order_ics(
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
    """Build an RFC5545 .ics event that iOS opens in Apple Calendar."""
    start = _calendar_start(order_date)
    end = start + timedelta(minutes=30)
    now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    uid = f"murchik-cakes-order-{int(order_id)}@murchik-cakes"
    description = (
        f"Клієнт: {customer_name}\n"
        f"Телефон: {phone}\n"
        f"На коли: {order_date or '—'}\n"
        f"Доставка: {delivery_method or '—'}\n"
        f"Оплата: {payment_method or '—'}\n"
        f"Коментар: {comment or '—'}\n\n"
        f"Замовлення:\n{items_text}\n\n"
        f"Сума: {float(total or 0):.2f} zł"
    )
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Murchik Cakes//Orders//UK",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{_ics_escape(uid)}",
        f"DTSTAMP:{now}",
        f"DTSTART:{start.strftime('%Y%m%dT%H%M%S')}",
        f"DTEND:{end.strftime('%Y%m%dT%H%M%S')}",
        f"SUMMARY:{_ics_escape(f'Murchik Cakes — замовлення #{order_id}')}",
        f"DESCRIPTION:{_ics_escape(description)}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(lines) + "\r\n"
