from pathlib import Path
import http.client
import json
import time
from urllib.parse import quote
from typing import Optional
import re
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, RedirectResponse, HTMLResponse
from pydantic import BaseModel

from config import BOT_TOKEN, ADMIN_IDS, ADMIN_CHAT_IDS
from database.db import init_db
from database.products_db import get_all_products, get_product, get_categories
from database.cart_db import (
    add_to_cart_db,
    get_cart_items_db,
    change_cart_qty_db,
    remove_from_cart_db,
    clear_cart_db,
    apply_promo_to_cart,
    apply_promo_to_cart_item,
)
from database.orders_db import create_order, get_user_orders, get_order, format_items
from database.custom_orders_db import create_custom_order_db, get_user_custom_orders
from database.favorites_db import toggle_favorite_db, get_favorites_db, is_favorite_db
from database.reviews_db import (
    add_review_db,
    get_product_reviews_db,
    get_product_rating_db,
    get_reviews_db,
    get_bakery_reviews_db,
)
from database.user_settings_db import get_user_language, set_user_language
from utils_translation import translate_product_name, translate_description, translate_product_name_raw
from utils_dates import min_order_date_text, validate_order_date
from services.calendar_links import build_order_ics, google_calendar_order_url
from services.google_tasks import create_google_task_for_order, TASKS_HOME_URL, build_google_auth_url, exchange_code_for_refresh_token, google_tasks_status, google_redirect_uri

app = FastAPI(title="Murchik Cakes API", version="3.6.1-hotfix")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parent.parent
WEBAPP_DIR = ROOT / "webapp"
TELEGRAM_FILE_PATH_CACHE = {}
TELEGRAM_IMAGE_CACHE = {}
TELEGRAM_CACHE_TTL_SECONDS = 60 * 60 * 12


class CartAddRequest(BaseModel):
    user_id: int
    product_id: int


class CartQtyRequest(BaseModel):
    user_id: int
    product_id: int
    delta: int


class CartPromoRequest(BaseModel):
    user_id: int
    product_id: Optional[int] = None
    code: str


class OrderRequest(BaseModel):
    user_id: int
    name: str
    phone: str
    date: str = ""
    delivery_method: str = ""
    payment_method: str = ""
    comment: str = ""


class CustomOrderRequest(BaseModel):
    user_id: int
    name: str
    phone: str
    product_id: Optional[int] = None
    product_name: str = ""
    description: str
    date: str
    photo: str = ""


class ReviewRequest(BaseModel):
    user_id: int
    name: str
    text: str
    rating: int
    review_type: str = "bakery"
    product_id: Optional[int] = None
    product_name: str = ""
    order_id: Optional[int] = None


class LanguageRequest(BaseModel):
    user_id: int
    language: str


@app.on_event("startup")
def startup():
    init_db()


def _rating(product_id: int):
    avg, count = get_product_rating_db(product_id)
    return {"average": avg, "count": count}


def _miniapp_image_url(src: str) -> str:
    if not src:
        return ""
    if src.startswith("http://") or src.startswith("https://") or src.startswith("/"):
        return src
    return f"/api/telegram-photo?file_id={quote(src)}"


def _localized_product(product: dict, user_id: int):
    if not product:
        return None
    photos = product.get("photos") or []
    label_image = product.get("label_image") or ""
    return {
        **product,
        "label_image_url": _miniapp_image_url(label_image),
        "photo_urls": [_miniapp_image_url(photo) for photo in photos if photo],
        "display_name": translate_product_name(product["name"], user_id, product.get("translations")),
        "display_description": translate_description(product["description"], user_id, product.get("translations")),
        "is_favorite": is_favorite_db(user_id, product["id"]) if user_id else False,
        "rating": _rating(product["id"]),
    }


def _localized_order_items(raw_items: str, user_id: int):
    try:
        items = json.loads(raw_items or "[]")
    except Exception:
        return []
    lang = get_user_language(user_id)
    result = []
    for item in items:
        item = dict(item)
        item["display_name"] = translate_product_name_raw(item.get("name", "Товар"), lang)
        result.append(item)
    return result


def _order_contains_product(order, product_id: int) -> bool:
    try:
        items = json.loads(order["items"] or "[]")
    except Exception:
        return False
    return any(int(item.get("product_id") or 0) == int(product_id) for item in items)


def _completed_status(status: str) -> bool:
    return status in ("Завершено", "Завершений", "Completed", "done", "completed")




@app.get("/admin/google/status")
def admin_google_status():
    return google_tasks_status()


@app.get("/admin/google/connect")
def admin_google_connect():
    try:
        return RedirectResponse(build_google_auth_url(), status_code=302)
    except Exception as exc:
        return HTMLResponse(
            f"""
            <html><body style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; padding: 24px;">
            <h2>Google Tasks не налаштовано</h2>
            <p>{str(exc)}</p>
            <p>У Google Cloud створи OAuth client типу <b>Web application</b> і додай redirect URI:</p>
            <pre>{google_redirect_uri() or 'WEBAPP_URL is empty'}</pre>
            <p>Потім додай у Railway API-сервіс тільки GOOGLE_CLIENT_ID і GOOGLE_CLIENT_SECRET.</p>
            </body></html>
            """,
            status_code=500,
        )


@app.get("/admin/google/callback")
def admin_google_callback(code: str = "", state: str = "", error: str = ""):
    if error:
        return HTMLResponse(f"<h2>Google OAuth error</h2><p>{error}</p>", status_code=400)
    if not code:
        return HTMLResponse("<h2>Google OAuth error</h2><p>No authorization code received.</p>", status_code=400)
    try:
        result = exchange_code_for_refresh_token(code, state)
        account = result.get("account_email") or "Google account"
        return HTMLResponse(
            f"""
            <html><body style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; padding: 24px;">
            <h2>✅ Google Tasks підключено</h2>
            <p>Акаунт: <b>{account}</b></p>
            <p>Тепер нові замовлення Murchik Cakes будуть автоматично створюватися як задачі Google Tasks.</p>
            <p>Цю вкладку можна закрити.</p>
            </body></html>
            """
        )
    except Exception as exc:
        return HTMLResponse(
            f"""
            <html><body style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; padding: 24px;">
            <h2>❌ Не вдалося підключити Google Tasks</h2>
            <p>{str(exc)}</p>
            <p>Перевір, що в Google Cloud в OAuth client додано redirect URI:</p>
            <pre>{google_redirect_uri() or 'WEBAPP_URL is empty'}</pre>
            </body></html>
            """,
            status_code=500,
        )


@app.get("/api/health")
def health():
    return {"ok": True, "version": "3.6.1-hotfix", "telegram_photo_proxy": bool(BOT_TOKEN)}


@app.get("/api/order-rules")
def order_rules():
    return {"min_lead_days": 4, "min_date": min_order_date_text()}


@app.get("/api/bootstrap/{user_id}")
def bootstrap(user_id: int):
    return {
        "language": get_user_language(user_id),
        "categories": get_categories(),
        "cart": cart(user_id),
        "favorites_count": len(get_favorites_db(user_id)),
    }


@app.get("/api/categories")
def categories():
    return get_categories()


@app.get("/api/products")
def products(user_id: int = Query(0), category: Optional[str] = None, q: str = ""):
    data = [_localized_product(p, user_id) for p in get_all_products(category)]
    if q:
        q_lower = q.lower().strip()
        data = [
            p for p in data
            if q_lower in (p.get("display_name") or p.get("name") or "").lower()
            or q_lower in (p.get("display_description") or p.get("description") or "").lower()
        ]
    data.sort(key=lambda p: (p.get("display_name") or p.get("name") or "").casefold())
    return data


@app.get("/api/products/{product_id}")
def product(product_id: int, user_id: int = Query(0)):
    item = get_product(product_id)
    if not item:
        raise HTTPException(404, "Product not found")
    return _localized_product(item, user_id)


@app.get("/api/telegram-photo")
def telegram_photo(file_id: str):
    if not BOT_TOKEN:
        raise HTTPException(500, "BOT_TOKEN is not configured")
    now = time.time()
    cached_image = TELEGRAM_IMAGE_CACHE.get(file_id)
    if cached_image and now - cached_image["time"] < TELEGRAM_CACHE_TTL_SECONDS:
        return Response(
            content=cached_image["content"],
            media_type=cached_image["content_type"],
            headers={"Cache-Control": "public, max-age=604800, immutable", "X-Murchik-Cache": "image-hit"},
        )
    try:
        cached_path = TELEGRAM_FILE_PATH_CACHE.get(file_id)
        if cached_path and now - cached_path["time"] < TELEGRAM_CACHE_TTL_SECONDS:
            file_path = cached_path["file_path"]
        else:
            conn = http.client.HTTPSConnection("api.telegram.org", timeout=15)
            conn.request("GET", f"/bot{BOT_TOKEN}/getFile?file_id={quote(file_id, safe='')}")
            resp = conn.getresponse()
            payload = resp.read()
            conn.close()
            data = json.loads(payload.decode("utf-8"))
            if not data.get("ok"):
                raise HTTPException(404, "Telegram file not found")
            file_path = data["result"]["file_path"]
            TELEGRAM_FILE_PATH_CACHE[file_id] = {"file_path": file_path, "time": now}

        file_conn = http.client.HTTPSConnection("api.telegram.org", timeout=30)
        file_conn.request("GET", f"/file/bot{BOT_TOKEN}/{file_path}")
        file_resp = file_conn.getresponse()
        content = file_resp.read()
        content_type = file_resp.getheader("Content-Type") or "image/jpeg"
        file_conn.close()
        TELEGRAM_IMAGE_CACHE[file_id] = {"content": content, "content_type": content_type, "time": now}
        return Response(
            content=content,
            media_type=content_type,
            headers={"Cache-Control": "public, max-age=604800, immutable", "X-Murchik-Cache": "miss"},
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Telegram photo proxy error: {exc}")


@app.get("/api/cart/{user_id}")
def cart(user_id: int):
    items, total, before, discount = get_cart_items_db(user_id)
    lang = get_user_language(user_id)
    for item in items:
        item["display_name"] = translate_product_name_raw(item.get("name", "Товар"), lang)
    return {"items": items, "total": total, "total_before_discount": before, "total_discount": discount}


@app.post("/api/cart/add")
def cart_add(req: CartAddRequest):
    if not get_product(req.product_id):
        raise HTTPException(404, "Product not found")
    add_to_cart_db(req.user_id, req.product_id)
    return cart(req.user_id)


@app.post("/api/cart/qty")
def cart_qty(req: CartQtyRequest):
    change_cart_qty_db(req.user_id, req.product_id, req.delta)
    return cart(req.user_id)


@app.delete("/api/cart/{user_id}/{product_id}")
def cart_delete(user_id: int, product_id: int):
    remove_from_cart_db(user_id, product_id)
    return cart(user_id)


@app.post("/api/cart/promo")
def cart_promo(req: CartPromoRequest):
    if req.product_id:
        success, discount = apply_promo_to_cart_item(req.user_id, req.product_id, req.code)
        applied = 1 if success else 0
    else:
        success, applied, discount = apply_promo_to_cart(req.user_id, req.code)
    return {"success": success, "discount": discount, "applied": applied, "cart": cart(req.user_id)}


def _normalize_phone(phone: str) -> str:
    return re.sub(r"\D", "", phone or "")


def _validate_customer_payload(name: str, phone: str, delivery_method: str | None = "", payment_method: str | None = ""):
    if not (name or "").strip():
        raise HTTPException(400, "Name is required")
    normalized_phone = _normalize_phone(phone)
    if len(normalized_phone) != 9:
        raise HTTPException(400, "Phone must contain exactly 9 digits, for example 504 123 456")
    if delivery_method is not None and not str(delivery_method).strip():
        raise HTTPException(400, "Choose delivery method")
    if payment_method is not None and not str(payment_method).strip():
        raise HTTPException(400, "Choose payment method")
    return normalized_phone


def _format_order_items_for_admin(items: list[dict]) -> str:
    lines = []
    for item in items:
        line = (
            f"• {item.get('name', 'Товар')} ×{item.get('qty', 1)} — "
            f"{float(item.get('final_subtotal', item.get('subtotal', 0)) or 0):.2f} zł"
        )
        if item.get("promo_code"):
            line += f" ({item.get('promo_code')} -{item.get('discount_percent', 0)}%)"
        lines.append(line)
    return "\n".join(lines) or "—"


def _admin_targets() -> list[int]:
    seen = set()
    result = []
    for chat_id in [*(ADMIN_IDS or []), *(ADMIN_CHAT_IDS or [])]:
        if chat_id not in seen:
            seen.add(chat_id)
            result.append(chat_id)
    return result


def _telegram_send_message(chat_id: int, text: str, reply_markup: dict | None = None) -> bool:
    body = {"chat_id": chat_id, "text": text}
    if reply_markup:
        body["reply_markup"] = reply_markup
    conn = http.client.HTTPSConnection("api.telegram.org", timeout=12)
    conn.request(
        "POST",
        f"/bot{BOT_TOKEN}/sendMessage",
        body=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    resp = conn.getresponse()
    response_body = resp.read().decode("utf-8", errors="replace")
    ok = 200 <= resp.status < 300
    if not ok:
        print(f"ADMIN NOTIFY ERROR {chat_id}: HTTP {resp.status} {response_body}")
    conn.close()
    return ok


def _notify_customer_order_created(user_id: int, order_id: int) -> None:
    if not BOT_TOKEN or not user_id:
        return
    try:
        _telegram_send_message(
            int(user_id),
            f"🍰 Ваше замовлення №{order_id} створено та очікує підтвердження.",
        )
    except Exception as exc:
        print(f"CUSTOMER CREATED NOTIFY ERROR order #{order_id}: {exc}")


def _notify_admins_new_order(order_id: int, req: OrderRequest, items: list[dict], total: float, before: float, discount: float, google_task: dict | None = None) -> int:
    if not BOT_TOKEN:
        print("ADMIN NOTIFY WARNING: BOT_TOKEN is empty")
        return 0
    targets = _admin_targets()
    if not targets:
        print("ADMIN NOTIFY WARNING: ADMIN_IDS/ADMIN_CHAT_IDS are empty")
        return 0

    promo_parts = []
    for item in items:
        if item.get("promo_code"):
            promo_parts.append(f"{item.get('name')} — {item.get('promo_code')} (-{item.get('discount_percent', 0)}%)")
    discount_text = ""
    if discount > 0:
        discount_text = f"\n🎁 Промокоди:\n" + "\n".join(promo_parts) + f"\n💸 Знижка: {discount:.2f} zł\nДо знижки: {before:.2f} zł"

    items_text = _format_order_items_for_admin(items)
    created_date = datetime.utcnow().date().isoformat()
    text = f"""🧁 Нове замовлення #{order_id}

Ім'я: {req.name.strip()}
Телефон: {_normalize_phone(req.phone)}
Статус: Створено
Дата замовлення: {created_date}
На коли: {req.date}
Спосіб доставки: {req.delivery_method}
Оплата: {req.payment_method}
Разом: {total:.2f} zł
Коментар: {req.comment.strip() or '—'}
Google Tasks: {'✅ задачу створено' if google_task else '⚠️ задачу не створено'}
{discount_text}
────────────
{items_text}"""
    calendar_url = google_calendar_order_url(
        order_id=order_id,
        customer_name=req.name.strip(),
        phone=_normalize_phone(req.phone),
        items_text=items_text,
        total=total,
        order_date=req.date,
        delivery_method=req.delivery_method,
        payment_method=req.payment_method,
        comment=req.comment.strip(),
    )
    inline_keyboard = [[{"text": "📋 Відкрити замовлення", "callback_data": f"admin_order_{order_id}"}]]
    if google_task:
        inline_keyboard.append([{"text": "✅ Відкрити Google Tasks", "url": TASKS_HOME_URL}])
    else:
        inline_keyboard.append([{"text": "📅 Додати в календар", "url": calendar_url}])
    reply_markup = {"inline_keyboard": inline_keyboard}

    success = 0
    for chat_id in targets:
        try:
            if _telegram_send_message(chat_id, text, reply_markup=reply_markup):
                success += 1
        except Exception as exc:
            print(f"ADMIN NOTIFY ERROR {chat_id}: {exc}")
    if success == 0:
        print("ADMIN NOTIFY WARNING: no admin received the order notification. Check ADMIN_IDS/ADMIN_CHAT_IDS and make sure admin opened the bot.")
    return success


@app.post("/api/orders")
def create_order_api(req: OrderRequest):
    ok, message, _ = validate_order_date(req.date, required=True)
    if not ok:
        raise HTTPException(400, message)
    normalized_phone = _validate_customer_payload(req.name, req.phone, req.delivery_method, req.payment_method)
    items, total, before, discount = get_cart_items_db(req.user_id)
    if not items:
        raise HTTPException(400, "Cart is empty")
    allowed_delivery = {
        "Самовивіз", "Кур'єр Glovo (дорого)",
        "Самовывоз", "Курьер Glovo (дорого)",
        "Odbiór osobisty", "Kurier Glovo (drogo)",
        "Pickup", "Glovo courier (expensive)",
    }
    allowed_payment = {"Готівкою", "Переказ BLIK", "Наличкой", "Перевод BLIK", "Gotówką", "Przelew BLIK", "Cash", "BLIK transfer"}
    if req.delivery_method not in allowed_delivery:
        raise HTTPException(400, "Choose delivery method")
    if req.payment_method not in allowed_payment:
        raise HTTPException(400, "Choose payment method")

    order_id = create_order(
        user_id=req.user_id,
        name=req.name.strip(),
        phone=normalized_phone,
        items=items,
        total=total,
        order_date=req.date,
        delivery_method=req.delivery_method,
        payment_method=req.payment_method,
        comment=req.comment,
    )
    clear_cart_db(req.user_id)
    _notify_customer_order_created(req.user_id, order_id)
    items_text = _format_order_items_for_admin(items)
    google_task = create_google_task_for_order(
        order_id=order_id,
        customer_name=req.name.strip(),
        phone=normalized_phone,
        items_text=items_text,
        total=total,
        order_date=req.date,
        delivery_method=req.delivery_method,
        payment_method=req.payment_method,
        comment=req.comment.strip(),
    )
    admin_notified = _notify_admins_new_order(order_id, req, items, total, before, discount, google_task=google_task)
    return {"id": order_id, "status": "Створено", "total": total, "admin_notified": admin_notified, "google_task_created": bool(google_task)}


@app.get("/api/orders/{order_id}/calendar.ics")
def order_calendar_ics(order_id: int):
    order = get_order(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    items_text = format_items(order["items"])
    ics = build_order_ics(
        order_id=order["id"],
        customer_name=order["name"],
        phone=order["phone"],
        items_text=items_text,
        total=float(order["total"] or 0),
        order_date=order["order_date"] if "order_date" in order.keys() else "",
        delivery_method=order["delivery_method"] if "delivery_method" in order.keys() else "",
        payment_method=order["payment_method"] if "payment_method" in order.keys() else "",
        comment=order["comment"] if "comment" in order.keys() else "",
    )
    headers = {"Content-Disposition": f'attachment; filename="murchik-order-{order_id}.ics"'}
    return Response(content=ics, media_type="text/calendar; charset=utf-8", headers=headers)


@app.get("/api/orders/{user_id}")
def orders(user_id: int):
    regular = []
    for o in get_user_orders(user_id):
        regular.append({
            "id": o["id"],
            "name": o["name"],
            "phone": o["phone"],
            "items": _localized_order_items(o["items"], user_id),
            "total": float(o["total"] or 0),
            "status": o["status"],
            "order_date": o["order_date"] if "order_date" in o.keys() else "",
            "delivery_method": o["delivery_method"] if "delivery_method" in o.keys() else "",
            "payment_method": o["payment_method"] if "payment_method" in o.keys() else "",
            "comment": o["comment"] if "comment" in o.keys() else "",
            "created_at": str(o["created_at"]),
            "type": "regular",
        })
    custom = []
    for o in get_user_custom_orders(user_id):
        custom.append({
            "id": o["id"],
            "product_name": o["product_name"],
            "description": o["description"],
            "date": o["date"],
            "status": o["status"],
            "order_date": o["order_date"] if "order_date" in o.keys() else o["date"],
            "delivery_method": o["delivery_method"] if "delivery_method" in o.keys() else "",
            "payment_method": o["payment_method"] if "payment_method" in o.keys() else "",
            "comment": o["comment"] if "comment" in o.keys() else "",
            "created_at": str(o["created_at"]),
            "type": "custom",
        })
    return {"orders": regular, "custom_orders": custom}


@app.post("/api/custom-orders")
def create_custom_order_api(req: CustomOrderRequest):
    ok, message, _ = validate_order_date(req.date, required=True)
    if not ok:
        raise HTTPException(400, message)
    normalized_phone = _validate_customer_payload(req.name, req.phone, None, None)
    order_id = create_custom_order_db(
        user_id=req.user_id,
        name=req.name.strip(),
        phone=normalized_phone,
        product_id=req.product_id,
        product_name=req.product_name,
        description=req.description,
        date=req.date,
        photo=req.photo,
    )
    _notify_customer_order_created(req.user_id, order_id)
    return {"id": order_id, "status": "Створено"}


@app.get("/api/favorites/{user_id}")
def favorites(user_id: int):
    return [_localized_product(p, user_id) for p in get_favorites_db(user_id)]


@app.post("/api/favorites/toggle")
def favorites_toggle(req: CartAddRequest):
    active = toggle_favorite_db(req.user_id, req.product_id)
    item = get_product(req.product_id)
    return {"active": active, "product": _localized_product(item, req.user_id) if item else None}


@app.get("/api/reviews")
def reviews(limit: int = 5, review_type: Optional[str] = None):
    if review_type == "bakery":
        return get_bakery_reviews_db(limit)
    return get_reviews_db(limit)


@app.get("/api/reviews/product/{product_id}")
def product_reviews(product_id: int, limit: int = 5):
    return get_product_reviews_db(product_id, limit)


@app.post("/api/reviews")
def create_review(req: ReviewRequest):
    if req.rating < 1 or req.rating > 5:
        raise HTTPException(400, "Rating must be 1..5")
    if req.review_type == "product":
        if not req.order_id or not req.product_id:
            raise HTTPException(400, "Product review requires order_id and product_id")
        order = get_order(req.order_id)
        if not order:
            raise HTTPException(404, "Order not found")
        if int(order["user_id"]) != int(req.user_id):
            raise HTTPException(403, "This order belongs to another user")
        if not _completed_status(order["status"]):
            raise HTTPException(403, "Reviews are available only after order completion")
        if not _order_contains_product(order, req.product_id):
            raise HTTPException(400, "This product is not in the selected order")
    review_id = add_review_db(
        user_id=req.user_id,
        name=req.name,
        text=req.text,
        rating=req.rating,
        review_type=req.review_type,
        product_id=req.product_id,
        product_name=req.product_name,
    )
    return {"id": review_id}


@app.get("/api/language/{user_id}")
def language(user_id: int):
    return {"language": get_user_language(user_id)}


@app.post("/api/language")
def update_language(req: LanguageRequest):
    set_user_language(req.user_id, req.language)
    return {"language": req.language}


if WEBAPP_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="webapp")
