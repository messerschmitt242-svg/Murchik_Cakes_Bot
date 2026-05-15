
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
