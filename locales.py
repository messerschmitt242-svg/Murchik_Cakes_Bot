
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
    "menu_language":{"ua":"🌐 Мова / Язык / Język / Language","ru":"🌐 Мова / Язык / Język / Language","pl":"🌐 Мова / Язык / Język / Language","en":"🌐 Мова / Язык / Język / Language"},
    "choose_lang":{"ua":"Оберіть мову:","ru":"Выберите язык:","pl":"Wybierz język:","en":"Choose language:"},
    "lang_changed":{"ua":"✅ Мову змінено","ru":"✅ Язык изменен","pl":"✅ Zmieniono język","en":"✅ Language changed"},
}

def tr(user_id, key):
    lang = get_user_language(user_id)
    value = TEXTS.get(key, {}).get(lang, TEXTS.get(key, {}).get("ua", key))

    # Some multiline texts are stored as escaped \\n in dictionaries.
    # Convert them to real Telegram line breaks before sending.
    if isinstance(value, str):
        value = value.replace("\\n", "\n")
        value = value.replace("\\'", "'")

    return value

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


TEXTS.update({
    "start_welcome":{"ua":"Вітаємо вас у кондитерській \'У Мурчика\' 🎂","ru":"Добро пожаловать в кондитерскую \'У Мурчика\' 🎂","pl":"Witamy w cukierni \'U Murchyka\' 🎂","en":"Welcome to \'U Murchyka\' bakery 🎂"},
    "orders_empty":{"ua":"У вас немає замовлень 🍰","ru":"У вас нет заказов 🍰","pl":"Nie masz zamówień 🍰","en":"You have no orders 🍰"},
    "orders_title":{"ua":"📦 Ваші замовлення:\\n\\n","ru":"📦 Ваши заказы:\\n\\n","pl":"📦 Twoje zamówienia:\\n\\n","en":"📦 Your orders:\\n\\n"},
    "order_label":{"ua":"Замовлення","ru":"Заказ","pl":"Zamówienie","en":"Order"},
    "custom_order_label":{"ua":"Індивідуальне замовлення","ru":"Индивидуальный заказ","pl":"Zamówienie indywidualne","en":"Custom order"},
    "status_label":{"ua":"📊 Статус:","ru":"📊 Статус:","pl":"📊 Status:","en":"📊 Status:"},
    "sum_label":{"ua":"💰 Сума:","ru":"💰 Сумма:","pl":"💰 Suma:","en":"💰 Total:"},
    "base_dessert_label":{"ua":"🎂 Базовий десерт:","ru":"🎂 Базовый десерт:","pl":"🎂 Bazowy deser:","en":"🎂 Base dessert:"},
    "date_label":{"ua":"📅 Дата:","ru":"📅 Дата:","pl":"📅 Data:","en":"📅 Date:"},
    "pickup_button":{"ua":"📍 Як отримати замовлення","ru":"📍 Как получить заказ","pl":"📍 Jak odebrać zamówienie","en":"📍 How to pick up the order"},
    "status_created":{"ua":"Створено","ru":"Создан","pl":"Utworzone","en":"Created"},
    "status_accepted":{"ua":"Прийнято","ru":"Принято","pl":"Przyjęte","en":"Accepted"},
    "status_cooking":{"ua":"Готується","ru":"Готовится","pl":"W przygotowaniu","en":"Preparing"},
    "status_ready":{"ua":"Готове до видачі","ru":"Готово к выдаче","pl":"Gotowe do odbioru","en":"Ready for pickup"},
    "status_done":{"ua":"Завершено","ru":"Завершено","pl":"Zakończone","en":"Completed"},
    "status_cancelled":{"ua":"Скасовано","ru":"Отменено","pl":"Anulowane","en":"Cancelled"},
    "contacts_text":{"ua":"📍 Наші контакти\\n\\n📞 Номер телефону:\\n+48 504 690 652\\n\\n🕒 Графік роботи:\\nПн–Нд: 10:00 – 18:00\\n\\n🏠 Адреса:\\nul. Toruńska 45D, Bydgoszcz","ru":"📍 Наши контакты\\n\\n📞 Номер телефона:\\n+48 504 690 652\\n\\n🕒 График работы:\\nПн–Вс: 10:00 – 18:00\\n\\n🏠 Адрес:\\nul. Toruńska 45D, Bydgoszcz","pl":"📍 Kontakt\\n\\n📞 Telefon:\\n+48 504 690 652\\n\\n🕒 Godziny pracy:\\nPon–Nd: 10:00 – 18:00\\n\\n🏠 Adres:\\nul. Toruńska 45D, Bydgoszcz","en":"📍 Contacts\\n\\n📞 Phone number:\\n+48 504 690 652\\n\\n🕒 Working hours:\\nMon–Sun: 10:00 – 18:00\\n\\n🏠 Address:\\nul. Toruńska 45D, Bydgoszcz"},
    "route_button":{"ua":"📍 Побудувати маршрут","ru":"📍 Построить маршрут","pl":"📍 Wyznacz trasę","en":"📍 Get directions"},
    "faq_text":{"ua":"❓ Питання та відповіді\\n\\n📌 За скільки днів замовляти?\\nЗа 4 дні.\\n\\n📌 Можна свій дизайн?\\nТак, можна надіслати референс або опис.\\n\\n📌 Чи є доставка?\\nПоки власної доставки немає. За потреби можемо надіслати через Glovo.","ru":"❓ Вопросы и ответы\\n\\n📌 За сколько дней заказывать?\\nЗа 4 дня.\\n\\n📌 Можно свой дизайн?\\nДа, можно отправить референс или описание.\\n\\n📌 Есть ли доставка?\\nПока собственной доставки нет. При необходимости можем отправить через Glovo.","pl":"❓ Pytania i odpowiedzi\\n\\n📌 Ile dni wcześniej zamawiać?\\n4 dni wcześniej.\\n\\n📌 Czy można własny projekt?\\nTak, można wysłać inspirację albo opis.\\n\\n📌 Czy jest dostawa?\\nNa razie nie mamy własnej dostawy. W razie potrzeby możemy wysłać przez Glovo.","en":"❓ FAQ\\n\\n📌 How many days in advance should I order?\\n4 days in advance.\\n\\n📌 Can I request my own design?\\nYes, you can send a reference or description.\\n\\n📌 Is delivery available?\\nWe do not have our own delivery yet. If needed, we can send via Glovo."},
    "fav_added":{"ua":"❤️ Додано в обране","ru":"❤️ Добавлено в избранное","pl":"❤️ Dodano do ulubionych","en":"❤️ Added to favorites"},
    "fav_removed":{"ua":"💔 Видалено з обраного","ru":"💔 Удалено из избранного","pl":"💔 Usunięto z ulubionych","en":"💔 Removed from favorites"},
    "fav_empty":{"ua":"❤️ У вас поки немає обраних товарів.","ru":"❤️ У вас пока нет избранных товаров.","pl":"❤️ Nie masz jeszcze ulubionych produktów.","en":"❤️ You have no favorite products yet."},
    "fav_title":{"ua":"❤️ Ваші обрані товари:","ru":"❤️ Ваши избранные товары:","pl":"❤️ Twoje ulubione produkty:","en":"❤️ Your favorite products:"},
    "cart_added":{"ua":"✅ Додано у кошик 🛒","ru":"✅ Добавлено в корзину 🛒","pl":"✅ Dodano do koszyka 🛒","en":"✅ Added to cart 🛒"},
    "enter_promo":{"ua":"Введіть промокод для цього товару:","ru":"Введите промокод для этого товара:","pl":"Wpisz kod promocyjny dla tego produktu:","en":"Enter promo code for this product:"},
    "promo_missing_product":{"ua":"Помилка: товар не обрано.","ru":"Ошибка: товар не выбран.","pl":"Błąd: produkt nie został wybrany.","en":"Error: product not selected."},
    "promo_not_found":{"ua":"❌ Промокод не знайдено або він неактивний.","ru":"❌ Промокод не найден или неактивен.","pl":"❌ Kod promocyjny nie został znaleziony albo jest nieaktywny.","en":"❌ Promo code not found or inactive."},
    "promo_applied":{"ua":"✅ Промокод застосовано:","ru":"✅ Промокод применён:","pl":"✅ Kod promocyjny zastosowany:","en":"✅ Promo code applied:"},
    "name_prompt":{"ua":"Ваше ім'я:","ru":"Ваше имя:","pl":"Twoje imię:","en":"Your name:"},
    "phone_prompt":{"ua":"Надішліть ваш номер телефону:","ru":"Отправьте ваш номер телефона:","pl":"Wyślij swój numer telefonu:","en":"Send your phone number:"},
    "share_phone":{"ua":"📱 Надіслати номер","ru":"📱 Отправить номер","pl":"📱 Wyślij numer","en":"📱 Share phone number"},
    "order_created_ok":{"ua":"✅ Замовлення #{id} створено.\\nМи скоро з вами зв'яжемося ❤️","ru":"✅ Заказ #{id} создан.\\nМы скоро с вами свяжемся ❤️","pl":"✅ Zamówienie #{id} zostało utworzone.\\nWkrótce się skontaktujemy ❤️","en":"✅ Order #{id} has been created.\\nWe will contact you soon ❤️"},
    "order_created_no_admin":{"ua":"✅ Замовлення #{id} створено.\\nАдміністратор може побачити його в панелі активних замовлень.","ru":"✅ Заказ #{id} создан.\\nАдминистратор увидит его в панели активных заказов.","pl":"✅ Zamówienie #{id} zostało utworzone.\\nAdministrator zobaczy je w panelu aktywnych zamówień.","en":"✅ Order #{id} has been created.\\nThe administrator can see it in the active orders panel."},
    "need_details":{"ua":"Потрібно уточнити деталі?","ru":"Нужно уточнить детали?","pl":"Chcesz doprecyzować szczegóły?","en":"Need to clarify details?"},
    "write_admin":{"ua":"💬 Написати адміністратору","ru":"💬 Написать администратору","pl":"💬 Napisz do administratora","en":"💬 Message administrator"},
    "pickup_details":{"ua":"📍 Подробиці на місці:\\n\\nНа брамі на клавіатурі натиснути 69,\\nпотім кнопку з значком ключа,\\nпотім код 6314.\\n\\nПоверх 5, квартира 69.","ru":"📍 Детали на месте:\\n\\nНа воротах на клавиатуре нажать 69,\\nзатем кнопку со значком ключа,\\nзатем код 6314.\\n\\nЭтаж 5, квартира 69.","pl":"📍 Szczegóły na miejscu:\\n\\nNa klawiaturze przy bramie naciśnij 69,\\nnastępnie przycisk z ikoną klucza,\\npotem kod 6314.\\n\\nPiętro 5, mieszkanie 69.","en":"📍 On-site details:\\n\\nAt the gate keypad press 69,\\nthen the button with the key icon,\\nthen code 6314.\\n\\nFloor 5, apartment 69."},
})


TEXTS.update({
    "review_write_bakery":{"ua":"Напишіть ваш відгук про кондитерську:","ru":"Напишите ваш отзыв о кондитерской:","pl":"Napisz swoją opinię o cukierni:","en":"Write your review about the bakery:"},
    "review_no_orders":{"ua":"У вас поки немає завершених або створених замовлень, з яких можна вибрати десерт для відгуку.","ru":"У вас пока нет заказов, из которых можно выбрать десерт для отзыва.","pl":"Nie masz jeszcze zamówień, z których można wybrać deser do opinii.","en":"You do not have any orders yet to choose a dessert for review."},
    "review_choose_last_product":{"ua":"Оберіть десерт з вашого останнього замовлення:","ru":"Выберите десерт из вашего последнего заказа:","pl":"Wybierz deser z ostatniego zamówienia:","en":"Choose a dessert from your last order:"},
    "review_write_product":{"ua":"Напишіть відгук про «{name}»:","ru":"Напишите отзыв о «{name}»:","pl":"Napisz opinię o „{name}”:","en":"Write a review for “{name}”:"},
    "review_too_short":{"ua":"Відгук занадто короткий. Напишіть трохи детальніше:","ru":"Отзыв слишком короткий. Напишите немного подробнее:","pl":"Opinia jest za krótka. Napisz trochę więcej:","en":"The review is too short. Please write a bit more:"},
    "review_thanks":{"ua":"Дякуємо за відгук ❤️\\nВаша оцінка: {rating}/5","ru":"Спасибо за отзыв ❤️\\nВаша оценка: {rating}/5","pl":"Dziękujemy za opinię ❤️\\nTwoja ocena: {rating}/5","en":"Thank you for your review ❤️\\nYour rating: {rating}/5"},
    "review_cancelled":{"ua":"Відгук скасовано.","ru":"Отзыв отменён.","pl":"Opinia została anulowana.","en":"Review cancelled."},
    "product_reviews_title":{"ua":"💬 Відгуки про продукт:\\n\\n","ru":"💬 Отзывы о продукте:\\n\\n","pl":"💬 Opinie o produkcie:\\n\\n","en":"💬 Product reviews:\\n\\n"},
    "bakery_reviews_title":{"ua":"💬 Відгуки про кондитерську:\\n\\n","ru":"💬 Отзывы о кондитерской:\\n\\n","pl":"💬 Opinie o cukierni:\\n\\n","en":"💬 Bakery reviews:\\n\\n"},
    "custom_start":{"ua":"🎂 Індивідуальне замовлення\\n\\nНапишіть ваше ім'я:","ru":"🎂 Индивидуальный заказ\\n\\nНапишите ваше имя:","pl":"🎂 Zamówienie indywidualne\\n\\nPodaj swoje imię:","en":"🎂 Custom order\\n\\nEnter your name:"},
    "name_empty":{"ua":"Ім'я не може бути порожнім. Напишіть ваше ім'я:","ru":"Имя не может быть пустым. Напишите ваше имя:","pl":"Imię nie może być puste. Podaj swoje imię:","en":"Name cannot be empty. Enter your name:"},
    "phone_empty":{"ua":"Телефон не може бути порожнім. Надішліть номер:","ru":"Телефон не может быть пустым. Отправьте номер:","pl":"Telefon nie może być pusty. Wyślij numer:","en":"Phone cannot be empty. Send your number:"},
    "custom_choose_category":{"ua":"Оберіть категорію десерту, до якого буде індивідуальне замовлення:","ru":"Выберите категорию десерта для индивидуального заказа:","pl":"Wybierz kategorię deseru dla zamówienia indywidualnego:","en":"Choose the dessert category for the custom order:"},
    "custom_choose_category_short":{"ua":"Оберіть категорію десерту:","ru":"Выберите категорию десерта:","pl":"Wybierz kategorię deseru:","en":"Choose dessert category:"},
    "category_not_found":{"ua":"Категорію не знайдено. Оберіть ще раз:","ru":"Категория не найдена. Выберите ещё раз:","pl":"Nie znaleziono kategorii. Wybierz ponownie:","en":"Category not found. Choose again:"},
    "category_empty":{"ua":"У категорії «{category}» поки немає товарів. Оберіть іншу категорію:","ru":"В категории «{category}» пока нет товаров. Выберите другую категорию:","pl":"W kategorii „{category}” nie ma jeszcze produktów. Wybierz inną kategorię:","en":"There are no products in “{category}” yet. Choose another category:"},
    "custom_choose_base":{"ua":"Оберіть базовий десерт:","ru":"Выберите базовый десерт:","pl":"Wybierz bazowy deser:","en":"Choose base dessert:"},
    "product_not_found":{"ua":"Товар не знайдено. Спробуйте ще раз.","ru":"Товар не найден. Попробуйте ещё раз.","pl":"Nie znaleziono produktu. Spróbuj ponownie.","en":"Product not found. Try again."},
    "custom_chosen_product":{"ua":"Ви обрали: {name}\\n\\nОпишіть, що саме потрібно змінити або додати:\\nдекор, напис, колір, начинка, побажання тощо.","ru":"Вы выбрали: {name}\\n\\nОпишите, что именно нужно изменить или добавить:\\nдекор, надпись, цвет, начинка, пожелания и т.д.","pl":"Wybrano: {name}\\n\\nOpisz, co dokładnie trzeba zmienić lub dodać:\\ndekor, napis, kolor, nadzienie, życzenia itp.","en":"You selected: {name}\\n\\nDescribe what exactly should be changed or added:\\ndecor, inscription, color, filling, wishes, etc."},
    "description_too_short":{"ua":"Опишіть замовлення трохи детальніше:","ru":"Опишите заказ немного подробнее:","pl":"Opisz zamówienie trochę dokładniej:","en":"Describe the order a bit more:"},
    "custom_date_prompt":{"ua":"На яку дату потрібне замовлення?\\nНаприклад: 25.05 або 25 травня","ru":"На какую дату нужен заказ?\\nНапример: 25.05 или 25 мая","pl":"Na kiedy potrzebne jest zamówienie?\\nNp.: 25.05 albo 25 maja","en":"What date do you need the order for?\\nFor example: 25.05 or May 25"},
    "date_empty":{"ua":"Вкажіть дату:","ru":"Укажите дату:","pl":"Podaj datę:","en":"Enter the date:"},
    "custom_photo_prompt":{"ua":"Можете надіслати фото-приклад або натиснути «Пропустити фото».","ru":"Можете отправить фото-пример или нажать «Пропустить фото».","pl":"Możesz wysłać zdjęcie przykładowe albo kliknąć „Pomiń zdjęcie”.","en":"You can send a reference photo or tap “Skip photo”."},
    "skip_photo":{"ua":"Пропустити фото","ru":"Пропустить фото","pl":"Pomiń zdjęcie","en":"Skip photo"},
    "custom_created_ok":{"ua":"✅ Індивідуальне замовлення C#{id} прийнято. Ми скоро з вами зв'яжемося ❤️","ru":"✅ Индивидуальный заказ C#{id} принят. Мы скоро с вами свяжемся ❤️","pl":"✅ Zamówienie indywidualne C#{id} zostało przyjęte. Wkrótce się skontaktujemy ❤️","en":"✅ Custom order C#{id} has been accepted. We will contact you soon ❤️"},
    "custom_created_no_admin":{"ua":"✅ Індивідуальне замовлення C#{id} створено.\\nАдміністратор може побачити його в панелі активних замовлень.","ru":"✅ Индивидуальный заказ C#{id} создан.\\nАдминистратор увидит его в панели активных заказов.","pl":"✅ Zamówienie indywidualne C#{id} zostało utworzone.\\nAdministrator zobaczy je w panelu aktywnych zamówień.","en":"✅ Custom order C#{id} has been created.\\nThe administrator can see it in the active orders panel."},
    "custom_cancelled":{"ua":"Індивідуальне замовлення скасовано.","ru":"Индивидуальный заказ отменён.","pl":"Zamówienie indywidualne anulowane.","en":"Custom order cancelled."},
})
