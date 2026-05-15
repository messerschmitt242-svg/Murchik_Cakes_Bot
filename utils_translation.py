
from database.user_settings_db import get_user_language

LANGS = ("ua", "ru", "pl", "en")

WORD_MAP = {
    "ru": {
        "класичний": "классический",
        "класична": "классическая",
        "київський": "киевский",
        "київська": "киевская",
        "шоколадний": "шоколадный",
        "ванільний": "ванильный",
        "медовий": "медовый",
        "мусовий": "муссовый",
        "фісташковий": "фисташковый",
        "полуничний": "клубничный",
        "малиновий": "малиновый",
        "карамельний": "карамельный",
        "лимонний": "лимонный",
        "ніжний": "нежный",
        "свіжий": "свежий",
        "з": "с",
        "без": "без",
        "та": "и",
        "і": "и",
        "кремом": "кремом",
        "крем": "крем",
        "ягодами": "ягодами",
        "ягоди": "ягоды",
        "горіхами": "орехами",
        "горіхи": "орехи",
        "карамеллю": "карамелью",
        "шоколадом": "шоколадом",
        "бісквіт": "бисквит",
        "начинка": "начинка",
        "торт": "торт",
        "тістечко": "пирожное",
        "тістечка": "пирожные",
    },
    "pl": {
        "класичний": "klasyczny",
        "класична": "klasyczna",
        "київський": "kijowski",
        "київська": "kijowska",
        "шоколадний": "czekoladowy",
        "ванільний": "waniliowy",
        "медовий": "miodowy",
        "мусовий": "musowy",
        "фісташковий": "pistacjowy",
        "полуничний": "truskawkowy",
        "малиновий": "malinowy",
        "карамельний": "karmelowy",
        "лимонний": "cytrynowy",
        "ніжний": "delikatny",
        "свіжий": "świeży",
        "з": "z",
        "без": "bez",
        "та": "i",
        "і": "i",
        "кремом": "kremem",
        "крем": "krem",
        "ягодами": "owocami",
        "ягоди": "owoce",
        "горіхами": "orzechami",
        "горіхи": "orzechy",
        "карамеллю": "karmelem",
        "шоколадом": "czekoladą",
        "бісквіт": "biszkopt",
        "начинка": "nadzienie",
        "торт": "tort",
        "тістечко": "ciastko",
        "тістечка": "ciastka",
    },
    "en": {
        "класичний": "classic",
        "класична": "classic",
        "київський": "Kyiv",
        "київська": "Kyiv",
        "шоколадний": "chocolate",
        "ванільний": "vanilla",
        "медовий": "honey",
        "мусовий": "mousse",
        "фісташковий": "pistachio",
        "полуничний": "strawberry",
        "малиновий": "raspberry",
        "карамельний": "caramel",
        "лимонний": "lemon",
        "ніжний": "delicate",
        "свіжий": "fresh",
        "з": "with",
        "без": "without",
        "та": "and",
        "і": "and",
        "кремом": "cream",
        "крем": "cream",
        "ягодами": "berries",
        "ягоди": "berries",
        "горіхами": "nuts",
        "горіхи": "nuts",
        "карамеллю": "caramel",
        "шоколадом": "chocolate",
        "бісквіт": "sponge cake",
        "начинка": "filling",
        "торт": "cake",
        "тістечко": "pastry",
        "тістечка": "pastries",
    },
}

CATEGORY_TRANSLATIONS = {
    "Торт": {"ua": "Торт", "ru": "Торт", "pl": "Tort", "en": "Cake"},
    "Тістечка": {"ua": "Тістечка", "ru": "Пирожные", "pl": "Ciastka", "en": "Pastries"},
    "Тістечко": {"ua": "Тістечко", "ru": "Пирожное", "pl": "Ciastko", "en": "Pastry"},
}

def _preserve_case(source: str, translated: str) -> str:
    if not source:
        return translated
    if source[0].isupper():
        return translated[:1].upper() + translated[1:]
    return translated

def _translate_words(text: str, lang: str) -> str:
    if lang == "ua":
        return text

    result = []
    current = ""

    def flush_word(word: str):
        if not word:
            return ""
        lower = word.lower()
        translated = WORD_MAP.get(lang, {}).get(lower)
        if translated:
            return _preserve_case(word, translated)
        return word

    for ch in text:
        if ch.isalpha() or ch in ("'", "’", "-"):
            current += ch
        else:
            result.append(flush_word(current))
            current = ""
            result.append(ch)
    result.append(flush_word(current))

    return "".join(result)

def generate_product_translations(name: str, description: str) -> dict:
    translations = {}
    for lang in LANGS:
        translations[lang] = {
            "name": translate_product_name_raw(name, lang),
            "description": _translate_words(description, lang),
        }
    return translations

def translate_product_name_raw(name: str, lang: str) -> str:
    for key, values in CATEGORY_TRANSLATIONS.items():
        if name.startswith(key + " "):
            rest = name[len(key):].strip()
            return f"{values.get(lang, key)} {rest}"
    return _translate_words(name, lang)

def translate_description_raw(text: str, lang: str) -> str:
    return _translate_words(text, lang)

def translate_product_name(name: str, user_id: int, translations: dict | None = None):
    lang = get_user_language(user_id)
    if translations and translations.get(lang, {}).get("name"):
        return translations[lang]["name"]
    return translate_product_name_raw(name, lang)

def translate_description(text: str, user_id: int, translations: dict | None = None):
    lang = get_user_language(user_id)
    if translations and translations.get(lang, {}).get("description"):
        return translations[lang]["description"]
    return translate_description_raw(text, lang)
