
from database.user_settings_db import get_user_language

TEXTS = {
    "menu_catalog":{"ua":"🍰 Каталог","ru":"🍰 Каталог","pl":"🍰 Katalog","en":"🍰 Catalog"},
    "menu_cart":{"ua":"🛒 Кошик","ru":"🛒 Корзина","pl":"🛒 Koszyk","en":"🛒 Cart"},
    "menu_orders":{"ua":"📦 Мої замовлення","ru":"📦 Мои заказы","pl":"📦 Moje zamówienia","en":"📦 My orders"},
    "menu_reviews":{"ua":"💬 Відгуки","ru":"💬 Отзывы","pl":"💬 Opinie","en":"💬 Reviews"},
    "menu_custom":{"ua":"🎂 Індивідуальне замовлення","ru":"🎂 Индивидуальный заказ","pl":"🎂 Zamówienie indywidualne","en":"🎂 Custom order"},
    "menu_favorites":{"ua":"❤️ Обране","ru":"❤️ Избранное","pl":"❤️ Ulubione","en":"❤️ Favorites"},
    "menu_faq":{"ua":"❓ FAQ","ru":"❓ FAQ","pl":"❓ FAQ","en":"❓ FAQ"},
    "menu_contacts":{"ua":"📍 Контакти","ru":"📍 Контакты","pl":"📍 Kontakt","en":"📍 Contacts"},
    "menu_language":{"ua":"🌐 Мова","ru":"🌐 Язык","pl":"🌐 Język","en":"🌐 Language"},
    "choose_lang":{"ua":"Оберіть мову:","ru":"Выберите язык:","pl":"Wybierz język:","en":"Choose language:"},
    "lang_changed":{"ua":"✅ Мову змінено","ru":"✅ Язык изменен","pl":"✅ Zmieniono język","en":"✅ Language changed"},
}

def tr(user_id,key):
    lang=get_user_language(user_id)
    return TEXTS.get(key,{}).get(lang,TEXTS.get(key,{}).get("ua",key))

# Inner UI texts
TEXTS.update({
    "home_button":{"ua":"🏠 Повернутися до головного меню","ru":"🏠 Вернуться в главное меню","pl":"🏠 Wróć do menu głównego","en":"🏠 Back to main menu"},
    "home_menu":{"ua":"Головне меню 🍰","ru":"Главное меню 🍰","pl":"Menu główne 🍰","en":"Main menu 🍰"},
    "cat_choose":{"ua":"Оберіть категорію каталогу 🍰","ru":"Выберите категорию каталога 🍰","pl":"Wybierz kategorię katalogu 🍰","en":"Choose a catalog category 🍰"},
    "cat_cakes":{"ua":"🎂 Торти","ru":"🎂 Торты","pl":"🎂 Torty","en":"🎂 Cakes"},
    "cat_pastries":{"ua":"🧁 Тістечка","ru":"🧁 Пирожные","pl":"🧁 Ciastka","en":"🧁 Pastries"},
    "back_categories":{"ua":"⬅️ До категорій","ru":"⬅️ К категориям","pl":"⬅️ Do kategorii","en":"⬅️ To categories"},
    "choose_product":{"ua":"Оберіть товар:","ru":"Выберите товар:","pl":"Wybierz produkt:","en":"Choose a product:"},
    "cart_empty":{"ua":"Кошик порожній 🛒","ru":"Корзина пуста 🛒","pl":"Koszyk jest pusty 🛒","en":"Cart is empty 🛒"},
    "cart_title":{"ua":"🛒 Ваш кошик:\n\n","ru":"🛒 Ваша корзина:\n\n","pl":"🛒 Twój koszyk:\n\n","en":"🛒 Your cart:\n\n"},
    "checkout":{"ua":"📦 Оформити замовлення","ru":"📦 Оформить заказ","pl":"📦 Złóż zamówienie","en":"📦 Checkout"},
    "reviews_title":{"ua":"💬 Відгуки","ru":"💬 Отзывы","pl":"💬 Opinie","en":"💬 Reviews"},
    "view_reviews":{"ua":"👀 Подивитися відгуки","ru":"👀 Посмотреть отзывы","pl":"👀 Zobacz opinie","en":"👀 View reviews"},
    "leave_review":{"ua":"✍️ Залишити відгук","ru":"✍️ Оставить отзыв","pl":"✍️ Zostaw opinię","en":"✍️ Leave a review"},
    "review_question":{"ua":"Про що хочете залишити відгук?","ru":"О чём хотите оставить отзыв?","pl":"Czego dotyczy opinia?","en":"What would you like to review?"},
    "review_bakery":{"ua":"🏠 Про кондитерську","ru":"🏠 О кондитерской","pl":"🏠 O cukierni","en":"🏠 About bakery"},
    "review_product":{"ua":"🍰 Про конкретний десерт","ru":"🍰 О конкретном десерте","pl":"🍰 O konkretnym deserze","en":"🍰 About a specific dessert"},
    "cancel":{"ua":"❌ Скасувати","ru":"❌ Отменить","pl":"❌ Anuluj","en":"❌ Cancel"},
    "top_reviews":{"ua":"⭐ Топ-5 відгуків:\n\n","ru":"⭐ Топ-5 отзывов:\n\n","pl":"⭐ Top 5 opinii:\n\n","en":"⭐ Top 5 reviews:\n\n"},
})


TEXTS.update({
    "rating_prefix":{"ua":"⭐ Оцінка:","ru":"⭐ Оценка:","pl":"⭐ Ocena:","en":"⭐ Rating:"},
    "rating_empty":{"ua":"⭐ Оцінка: поки немає","ru":"⭐ Оценок пока нет","pl":"⭐ Brak ocen","en":"⭐ No ratings yet"},
    "add_to_cart":{"ua":"🛒 Додати в кошик","ru":"🛒 Добавить в корзину","pl":"🛒 Dodaj do koszyka","en":"🛒 Add to cart"},
    "add_favorite":{"ua":"❤️ Додати в обране","ru":"❤️ Добавить в избранное","pl":"❤️ Dodaj do ulubionych","en":"❤️ Add to favorites"},
    "remove_favorite":{"ua":"💔 Видалити з обраного","ru":"💔 Удалить из избранного","pl":"💔 Usuń z ulubionych","en":"💔 Remove from favorites"},
    "add_product_question":{"ua":"Додати цей товар у кошик?","ru":"Добавить этот товар в корзину?","pl":"Dodać ten produkt do koszyka?","en":"Add this product to cart?"},
})
