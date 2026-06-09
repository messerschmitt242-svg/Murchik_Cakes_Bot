from __future__ import annotations

import json
import os
import http.client
import secrets
from datetime import datetime
from urllib.parse import quote, urlencode, urlsplit, urlunsplit

from database.google_oauth_db import get_google_refresh_token, save_google_refresh_token, get_google_tasks_status

GOOGLE_TASKS_SCOPE = "https://www.googleapis.com/auth/tasks https://www.googleapis.com/auth/userinfo.email"
TASKS_HOME_URL = "https://tasks.google.com/"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"

# In-memory OAuth state is enough for a one-time admin connection flow.
# If the service restarts during authorization, just open /admin/google/connect again.
_PENDING_STATES: set[str] = set()


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def _clean_base_url(raw: str = "") -> str:
    raw = (raw or _env("WEBAPP_URL") or "").strip()
    if not raw:
        return ""
    parsed = urlsplit(raw)
    if parsed.scheme and parsed.netloc:
        return urlunsplit((parsed.scheme, parsed.netloc, "", "", "")).rstrip("/")
    return raw.split("?", 1)[0].rstrip("/")


def google_connect_url() -> str:
    base = _clean_base_url()
    return f"{base}/admin/google/connect" if base else ""


def google_redirect_uri() -> str:
    base = _clean_base_url()
    return f"{base}/admin/google/callback" if base else ""


def is_google_tasks_configured() -> bool:
    return bool(_env("GOOGLE_CLIENT_ID") and _env("GOOGLE_CLIENT_SECRET") and (_env("GOOGLE_REFRESH_TOKEN") or get_google_refresh_token()))


def google_tasks_status() -> dict:
    status = get_google_tasks_status()
    status["client_configured"] = bool(_env("GOOGLE_CLIENT_ID") and _env("GOOGLE_CLIENT_SECRET"))
    status["env_refresh_token"] = bool(_env("GOOGLE_REFRESH_TOKEN"))
    status["connect_url"] = google_connect_url()
    return status


def build_google_auth_url() -> str:
    client_id = _env("GOOGLE_CLIENT_ID")
    redirect_uri = google_redirect_uri()
    if not client_id or not _env("GOOGLE_CLIENT_SECRET"):
        raise RuntimeError("Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in Railway API service first")
    if not redirect_uri:
        raise RuntimeError("Set WEBAPP_URL in Railway API service first")
    state = secrets.token_urlsafe(24)
    _PENDING_STATES.add(state)
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": GOOGLE_TASKS_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return GOOGLE_AUTH_URL + "?" + urlencode(params)


def _request_json(method: str, host: str, path: str, body: dict | None = None, headers: dict | None = None, timeout: int = 15) -> dict:
    payload = None
    req_headers = headers or {}
    if body is not None:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req_headers = {"Content-Type": "application/json", **req_headers}
    conn = http.client.HTTPSConnection(host, timeout=timeout)
    conn.request(method, path, body=payload, headers=req_headers)
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8", errors="replace")
    conn.close()
    try:
        data = json.loads(raw or "{}")
    except Exception:
        data = {"raw": raw}
    if not (200 <= resp.status < 300):
        raise RuntimeError(f"Google API HTTP {resp.status}: {data}")
    return data


def exchange_code_for_refresh_token(code: str, state: str = "") -> dict:
    if state and state not in _PENDING_STATES:
        raise RuntimeError("OAuth state expired or invalid. Open /admin/google/connect again.")
    if state:
        _PENDING_STATES.discard(state)

    body = {
        "client_id": _env("GOOGLE_CLIENT_ID"),
        "client_secret": _env("GOOGLE_CLIENT_SECRET"),
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": google_redirect_uri(),
    }
    data = _request_json("POST", "oauth2.googleapis.com", "/token", body=body)
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        raise RuntimeError("Google did not return refresh_token. Try reconnecting and make sure prompt=consent is used.")

    account_email = ""
    access_token = data.get("access_token")
    if access_token:
        try:
            info = _request_json(
                "GET",
                "www.googleapis.com",
                "/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            account_email = info.get("email", "")
        except Exception:
            account_email = ""

    save_google_refresh_token(refresh_token, account_email)
    return {"ok": True, "account_email": account_email}


def refresh_access_token() -> str:
    client_id = _env("GOOGLE_CLIENT_ID")
    client_secret = _env("GOOGLE_CLIENT_SECRET")
    refresh_token = _env("GOOGLE_REFRESH_TOKEN") or get_google_refresh_token()
    if not (client_id and client_secret and refresh_token):
        raise RuntimeError("Google Tasks is not configured: connect Google Tasks in admin panel first")

    body = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    data = _request_json("POST", "oauth2.googleapis.com", "/token", body=body)
    token = data.get("access_token")
    if not token:
        raise RuntimeError(f"Google OAuth did not return access_token: {data}")
    return token


def _task_due(order_date: str = "") -> str | None:
    if not order_date:
        return None
    try:
        dt = datetime.strptime(order_date, "%Y-%m-%d")
    except Exception:
        return None
    return dt.strftime("%Y-%m-%dT00:00:00.000Z")


def build_order_task_payload(
    order_id: int,
    customer_name: str,
    phone: str,
    items_text: str,
    total: float,
    order_date: str = "",
    delivery_method: str = "",
    payment_method: str = "",
    comment: str = "",
) -> dict:
    notes = (
        f"Клієнт: {customer_name}\n"
        f"Телефон: {phone}\n"
        f"На коли: {order_date or '—'}\n"
        f"Доставка: {delivery_method or '—'}\n"
        f"Оплата: {payment_method or '—'}\n"
        f"Коментар: {comment or '—'}\n\n"
        f"Замовлення:\n{items_text}\n\n"
        f"Сума: {float(total or 0):.2f} zł"
    )
    payload = {
        "title": f"🍰 Замовлення #{int(order_id)} — {customer_name}",
        "notes": notes,
        "status": "needsAction",
    }
    due = _task_due(order_date)
    if due:
        payload["due"] = due
    return payload


def create_google_task_for_order(
    order_id: int,
    customer_name: str,
    phone: str,
    items_text: str,
    total: float,
    order_date: str = "",
    delivery_method: str = "",
    payment_method: str = "",
    comment: str = "",
) -> dict | None:
    if not is_google_tasks_configured():
        print("GOOGLE TASKS WARNING: integration is disabled. Connect Google Tasks in admin panel or set GOOGLE_REFRESH_TOKEN.")
        return None
    try:
        token = refresh_access_token()
        tasklist = _env("GOOGLE_TASKLIST_ID") or "@default"
        payload = build_order_task_payload(
            order_id=order_id,
            customer_name=customer_name,
            phone=phone,
            items_text=items_text,
            total=total,
            order_date=order_date,
            delivery_method=delivery_method,
            payment_method=payment_method,
            comment=comment,
        )
        return _request_json(
            "POST",
            "tasks.googleapis.com",
            f"/tasks/v1/lists/{quote(tasklist, safe='')}/tasks",
            body=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
    except Exception as exc:
        print(f"GOOGLE TASKS ERROR: {exc}")
        return None
