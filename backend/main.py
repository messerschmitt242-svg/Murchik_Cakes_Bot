
from pathlib import Path
import http.client
import json
from urllib.parse import quote
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, RedirectResponse
from pydantic import BaseModel

from database.db import init_db
from database.products_db import get_all_products, get_product, get_categories
from database.cart_db import (
    add_to_cart_db,
    get_cart_items_db,
    change_cart_qty_db,
    remove_from_cart_db,
    clear_cart_db,
    apply_promo_to_cart_item,
)
from database.orders_db import create_order, get_user_orders, get_order
from database.custom_orders_db import create_custom_order_db, get_user_custom_orders
from database.favorites_db import toggle_favorite_db, get_favorites_db, is_favorite_db
from database.reviews_db import add_review_db, get_product_reviews_db, get_product_rating_db, get_reviews_db, get_bakery_reviews_db
from database.user_settings_db import get_user_language, set_user_language
from utils_translation import translate_product_name, translate_description, translate_product_name_raw
from database.orders_db import format_items
from config import BOT_TOKEN

app = FastAPI(title="Murchik Cakes API", version="3.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parent.parent
WEBAPP_DIR = ROOT / "webapp"


class CartAddRequest(BaseModel):
    user_id: int
    product_id: int


class CartQtyRequest(BaseModel):
    user_id: int
    product_id: int
    delta: int


class CartPromoRequest(BaseModel):
    user_id: int
    product_id: int
    code: str


class OrderRequest(BaseModel):
    user_id: int
    name: str
    phone: str
    date: str = ""
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
    return {
        "average": avg,
        "count": count,
    }


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
    # This is simple and safe: keep original order data, but adapt first word if possible.
    import json
    try:
        items = json.loads(raw_items or "[]")
    except Exception:
        return []

    lang = get_user_language(user_id)
    result = []
    for item in items:
        name = item.get("name", "Товар")
        item = dict(item)
        item["display_name"] = translate_product_name_raw(name, lang)
        result.append(item)
    return result

def _order_contains_product(order, product_id: int) -> bool:
    import json
    try:
        items = json.loads(order["items"] or "[]")
    except Exception:
        return False
    return any(int(item.get("product_id") or 0) == int(product_id) for item in items)


def _completed_status(status: str) -> bool:
    return status in ("Завершено", "Завершений", "Completed", "done", "completed")


@app.get("/api/health")
def health():
    return {"ok": True, "version": "3.4.0", "telegram_photo_proxy": bool(BOT_TOKEN)}


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
    return data


@app.get("/api/products/{product_id}")
def product(product_id: int, user_id: int = Query(0)):
    item = get_product(product_id)
    if not item:
        raise HTTPException(404, "Product not found")
    return _localized_product(item, user_id)


@app.get("/api/telegram-photo")
def telegram_photo(file_id: str):
    """
    Telegram file_id is not a public image URL.
    This endpoint converts Telegram file_id into a browser-readable image response for Mini App.
    """
    if not BOT_TOKEN:
        raise HTTPException(500, "BOT_TOKEN is not configured")

    try:
        conn = http.client.HTTPSConnection("api.telegram.org", timeout=15)
        conn.request("GET", f"/bot{BOT_TOKEN}/getFile?file_id={quote(file_id, safe='')}")
        resp = conn.getresponse()
        payload = resp.read()
        conn.close()

        data = json.loads(payload.decode("utf-8"))
        if not data.get("ok"):
            raise HTTPException(404, "Telegram file not found")

        file_path = data["result"]["file_path"]

        file_conn = http.client.HTTPSConnection("api.telegram.org", timeout=30)
        file_conn.request("GET", f"/file/bot{BOT_TOKEN}/{file_path}")
        file_resp = file_conn.getresponse()
        content = file_resp.read()
        content_type = file_resp.getheader("Content-Type") or "image/jpeg"
        file_conn.close()

        return Response(
            content=content,
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=86400"
            },
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
    return {
        "items": items,
        "total": total,
        "total_before_discount": before,
        "total_discount": discount,
    }


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
    success, discount = apply_promo_to_cart_item(req.user_id, req.product_id, req.code)
    return {
        "success": success,
        "discount": discount,
        "cart": cart(req.user_id),
    }


@app.post("/api/orders")
def create_order_api(req: OrderRequest):
    items, total, _, _ = get_cart_items_db(req.user_id)
    if not items:
        raise HTTPException(400, "Cart is empty")

    # Preserve extra Mini App checkout info inside name field for compatibility with old schema.
    display_name = req.name
    if req.date or req.comment:
        display_name = f"{req.name} | Дата: {req.date or '—'} | Коментар: {req.comment or '—'}"

    order_id = create_order(
        user_id=req.user_id,
        name=display_name,
        phone=req.phone,
        items=items,
        total=total,
    )
    clear_cart_db(req.user_id)
    return {
        "id": order_id,
        "status": "Прийнято",
        "total": total,
    }


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
            "created_at": str(o["created_at"]),
            "type": "custom",
        })

    return {
        "orders": regular,
        "custom_orders": custom,
    }


@app.post("/api/custom-orders")
def create_custom_order_api(req: CustomOrderRequest):
    order_id = create_custom_order_db(
        user_id=req.user_id,
        name=req.name,
        phone=req.phone,
        product_id=req.product_id,
        product_name=req.product_name,
        description=req.description,
        date=req.date,
        photo=req.photo,
    )
    return {"id": order_id, "status": "Прийнято"}


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
