from datetime import datetime, timedelta
from urllib.parse import urlencode


def google_calendar_order_url(order_id: int, customer_name: str, phone: str, items_text: str, total: float) -> str:
    """Creates a prefilled Google Calendar event URL without OAuth."""
    start = datetime.now() + timedelta(hours=1)
    end = start + timedelta(minutes=30)
    dates = f"{start.strftime('%Y%m%dT%H%M%S')}/{end.strftime('%Y%m%dT%H%M%S')}"
    details = f"Клієнт: {customer_name}\nТелефон: {phone}\n\nЗамовлення:\n{items_text}\n\nСума: {total:.2f} zł"
    params = {
        "action": "TEMPLATE",
        "text": f"Murchik Cakes — замовлення #{order_id}",
        "dates": dates,
        "details": details,
    }
    return "https://calendar.google.com/calendar/render?" + urlencode(params)
