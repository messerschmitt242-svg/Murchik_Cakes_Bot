const tg = window.Telegram?.WebApp;
tg?.ready();
tg?.expand();

const API = "";
const state = {
  userId: tg?.initDataUnsafe?.user?.id || Number(localStorage.getItem("mc_user_id") || 777000),
  userName: tg?.initDataUnsafe?.user?.first_name || "",
  lang: localStorage.getItem("mc_lang") || "ua",
  category: "",
  search: "",
  products: [],
  cart: { items: [], total: 0 },
};

localStorage.setItem("mc_user_id", String(state.userId));


const LANG_LABELS = {
  ua: "UA 🇺🇦",
  ru: "RU 🇷🇺",
  pl: "PL 🇵🇱",
  en: "EN 🇬🇧",
};

function updateLangButton() {
  const btn = $("langBtn");
  if (btn) btn.textContent = LANG_LABELS[state.lang] || "🌐";
}


const I18N = {
  ua: {
    subtitle: "Кондитерська у Telegram",
    heroTitle: "Свіжі торти та тістечка",
    heroText: "Замовляйте улюблені десерти у кілька натискань.",
    catalog: "Каталог", cart: "Кошик", orders: "Замовлення", more: "Більше",
    all: "Усе", cakes: "🎂 Торти", pastries: "🧁 Тістечка",
    search: "Пошук десертів...", add: "Додати", view: "Деталі", favorite: "Обране",
    checkout: "Оформлення", name: "Ім'я", phone: "Телефон", date: "Дата", comment: "Коментар",
    createOrder: "Створити замовлення", emptyCart: "Кошик порожній", empty: "Поки нічого немає",
    total: "Разом", orderCreated: "Замовлення створено", favorites: "Обране", reviews: "Відгуки",
    customOrder: "Індивідуальне замовлення", contacts: "Контакти", route: "Побудувати маршрут",
    sendReview: "Надіслати відгук", reviewText: "Ваш відгук", sendCustom: "Надіслати замовлення",
    customDescription: "Опишіть, що саме потрібно", productReviews: "Відгуки про товар",
    addReview: "Залишити відгук", promo: "Промокод", applyPromo: "Застосувати",
    required: "Заповніть обов'язкові поля", done: "Готово", status: "Статус", portion: "Порція", removeFavorite: "Видалити з обраного", leaveOrderReview: "Залишити відгук", confirmReview: "Підтвердити", product: "Товар",
  },
  ru: {
    subtitle: "Кондитерская в Telegram",
    heroTitle: "Свежие торты и пирожные",
    heroText: "Заказывайте любимые десерты в несколько нажатий.",
    catalog: "Каталог", cart: "Корзина", orders: "Заказы", more: "Ещё",
    all: "Все", cakes: "🎂 Торты", pastries: "🧁 Пирожные",
    search: "Поиск десертов...", add: "Добавить", view: "Детали", favorite: "Избранное",
    checkout: "Оформление", name: "Имя", phone: "Телефон", date: "Дата", comment: "Комментарий",
    createOrder: "Создать заказ", emptyCart: "Корзина пуста", empty: "Пока ничего нет",
    total: "Итого", orderCreated: "Заказ создан", favorites: "Избранное", reviews: "Отзывы",
    customOrder: "Индивидуальный заказ", contacts: "Контакты", route: "Построить маршрут",
    sendReview: "Отправить отзыв", reviewText: "Ваш отзыв", sendCustom: "Отправить заказ",
    customDescription: "Опишите, что именно нужно", productReviews: "Отзывы о товаре",
    addReview: "Оставить отзыв", promo: "Промокод", applyPromo: "Применить",
    required: "Заполните обязательные поля", done: "Готово", status: "Статус", portion: "Порция", removeFavorite: "Удалить из избранного", leaveOrderReview: "Оставить отзыв", confirmReview: "Подтвердить", product: "Товар",
  },
  pl: {
    subtitle: "Cukiernia w Telegramie",
    heroTitle: "Świeże torty i ciastka",
    heroText: "Zamów ulubione desery w kilku kliknięciach.",
    catalog: "Katalog", cart: "Koszyk", orders: "Zamówienia", more: "Więcej",
    all: "Wszystko", cakes: "🎂 Torty", pastries: "🧁 Ciastka",
    search: "Szukaj deserów...", add: "Dodaj", view: "Szczegóły", favorite: "Ulubione",
    checkout: "Zamówienie", name: "Imię", phone: "Telefon", date: "Data", comment: "Komentarz",
    createOrder: "Złóż zamówienie", emptyCart: "Koszyk jest pusty", empty: "Nic tu jeszcze nie ma",
    total: "Razem", orderCreated: "Zamówienie utworzone", favorites: "Ulubione", reviews: "Opinie",
    customOrder: "Zamówienie indywidualne", contacts: "Kontakt", route: "Wyznacz trasę",
    sendReview: "Wyślij opinię", reviewText: "Twoja opinia", sendCustom: "Wyślij zamówienie",
    customDescription: "Opisz, czego potrzebujesz", productReviews: "Opinie o produkcie",
    addReview: "Dodaj opinię", promo: "Kod promo", applyPromo: "Zastosuj",
    required: "Wypełnij wymagane pola", done: "Gotowe", status: "Status", portion: "Porcja", removeFavorite: "Usuń z ulubionych", leaveOrderReview: "Dodaj opinię", confirmReview: "Potwierdź", product: "Produkt",
  },
  en: {
    subtitle: "Bakery in Telegram",
    heroTitle: "Fresh cakes and pastries",
    heroText: "Order your favorite desserts in a few taps.",
    catalog: "Catalog", cart: "Cart", orders: "Orders", more: "More",
    all: "All", cakes: "🎂 Cakes", pastries: "🧁 Pastries",
    search: "Search desserts...", add: "Add", view: "Details", favorite: "Favorites",
    checkout: "Checkout", name: "Name", phone: "Phone", date: "Date", comment: "Comment",
    createOrder: "Create order", emptyCart: "Cart is empty", empty: "Nothing here yet",
    total: "Total", orderCreated: "Order created", favorites: "Favorites", reviews: "Reviews",
    customOrder: "Custom order", contacts: "Contacts", route: "Get directions",
    sendReview: "Send review", reviewText: "Your review", sendCustom: "Send order",
    customDescription: "Describe what you need", productReviews: "Product reviews",
    addReview: "Leave review", promo: "Promo code", applyPromo: "Apply",
    required: "Fill required fields", done: "Done", status: "Status", portion: "Portion", removeFavorite: "Remove from favorites", leaveOrderReview: "Leave review", confirmReview: "Confirm", product: "Product",
  }
};

const $ = (id) => document.getElementById(id);
const tr = (key) => (I18N[state.lang] || I18N.ua)[key] || key;

function setText() {
    $("heroTitle").textContent = tr("heroTitle");
  $("heroText").textContent = tr("heroText");
  document.querySelectorAll("[data-i18n]").forEach(el => el.textContent = tr(el.dataset.i18n));
  document.querySelectorAll("[data-placeholder]").forEach(el => el.placeholder = tr(el.dataset.placeholder));
  updateLangButton();
}

async function api(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let msg = await res.text();
    try { msg = JSON.parse(msg).detail || msg; } catch {}
    throw new Error(msg);
  }
  return res.json();
}

function toast(text) {
  const el = $("toast");
  el.textContent = text;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 1800);
}

function haptic(type = "success") {
  tg?.HapticFeedback?.notificationOccurred?.(type);
}

function firstPhoto(product) {
  return product.photos && product.photos.length ? product.photos[0] : "";
}

function imageUrl(src) {
  if (!src) return "";
  if (src.startsWith("http://") || src.startsWith("https://") || src.startsWith("/")) return src;
  return `/api/telegram-photo?file_id=${encodeURIComponent(src)}`;
}

function productImageUrl(product, mode = "label") {
  if (mode === "label") {
    return product.label_image_url || imageUrl(product.label_image || firstPhoto(product));
  }
  return (product.photo_urls && product.photo_urls.length ? product.photo_urls[0] : "") || imageUrl(firstPhoto(product));
}

function imageMarkup(product, cls = "card-img", mode = "label") {
  const url = productImageUrl(product, mode);
  if (url) return `<img class="${cls}" src="${url}" alt="" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement('div'),{className:'${cls}',textContent:'🍰'}))">`;
  return `<div class="${cls}">🍰</div>`;
}


function localizedProductName(product) {
  const fromTranslations = product.translations?.[state.lang]?.name;
  if (fromTranslations) return fromTranslations;
  return product.display_name || product.name || "";
}

function localizedProductDescription(product) {
  const fromTranslations = product.translations?.[state.lang]?.description;
  if (fromTranslations) return fromTranslations;
  return product.display_description || product.description || "";
}

function rerenderVisibleDataAfterLanguageChange() {
  state.products = state.products.map(p => ({
    ...p,
    display_name: localizedProductName(p),
    display_description: localizedProductDescription(p),
  }));
  renderProducts(state.products, $("products"));

  if (!$("favoritesPanel")?.classList.contains("hidden")) {
    loadFavorites();
  }
  if (!$("orders")?.classList.contains("active")) {
    // Nothing.
  } else {
    loadOrders();
  }
}

function renderStars(rating) {
  const avg = rating?.average;
  const count = rating?.count || 0;
  return `⭐ ${avg ? Number(avg).toFixed(1) : "—"} (${count})`;
}

function showTab(tab) {
  document.querySelectorAll(".tab").forEach(b => b.classList.toggle("active", b.dataset.tab === tab));
  document.querySelectorAll(".screen").forEach(s => s.classList.toggle("active", s.id === tab));
  if (tab === "cart") loadCart();
  if (tab === "orders") loadOrders();
}

document.querySelectorAll(".tab").forEach(btn => btn.addEventListener("click", () => showTab(btn.dataset.tab)));

document.querySelectorAll(".pill").forEach(btn => btn.addEventListener("click", () => {
  document.querySelectorAll(".pill").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  state.category = btn.dataset.category;
  loadProducts();
}));

$("searchInput").addEventListener("input", (e) => {
  state.search = e.target.value.trim();
  clearTimeout(window.__searchTimer);
  window.__searchTimer = setTimeout(loadProducts, 250);
});

$("langBtn").addEventListener("click", async () => {
  const order = ["ua", "ru", "pl", "en"];
  const idx = order.indexOf(state.lang);
  state.lang = order[(idx + 1) % order.length];
  localStorage.setItem("mc_lang", state.lang);
  setText();

  // Fast language switch:
  // Do not reload products/images from API. Images keep browser/API cache.
  // Text is rerendered from already loaded translations.
  rerenderVisibleDataAfterLanguageChange();

  try {
    await api("/api/language", { method: "POST", body: JSON.stringify({ user_id: state.userId, language: state.lang }) });
  } catch {}
});

async function bootstrap() {
  try {
    const data = await api(`/api/bootstrap/${state.userId}`);
    state.lang = data.language || state.lang;
    localStorage.setItem("mc_lang", state.lang);
  } catch {}
  setText();
  $("searchInput").placeholder = tr("search");
  prefillUser();
  await loadProducts();
  await loadCart(false);
}

function prefillUser() {
  ["orderName", "reviewName", "customName"].forEach(id => {
    if ($(id) && !$(id).value && state.userName) $(id).value = state.userName;
  });
}

async function loadProducts() {
  const qs = new URLSearchParams({ user_id: state.userId });
  if (state.category) qs.set("category", state.category);
  if (state.search) qs.set("q", state.search);
  state.products = await api(`/api/products?${qs}`);
  renderProducts(state.products, $("products"));
}

function renderProducts(products, container) {
  if (!products.length) {
    container.innerHTML = `<div class="empty">🍰 ${tr("empty")}</div>`;
    return;
  }

  container.innerHTML = products.map(p => `
    <article class="card">
      <button class="image-button" onclick="openProduct(${p.id})" aria-label="${tr("view")}">
        ${imageMarkup(p, "card-img", "label")}
      </button>
      <h3>${localizedProductName(p)}</h3>
      <div class="rating">${renderStars(p.rating)}</div>
      <p>${localizedProductDescription(p).slice(0, 86)}</p>
      <div class="price">${Number(p.price || 0).toFixed(2)} zł</div>
      ${p.portion ? `<div class="muted">📦 ${tr("portion")}: ${p.portion}</div>` : ""}
      <div class="actions">
        <button onclick="addToCart(${p.id})">🛒 ${tr("add")}</button>
      </div>
    </article>
  `).join("");
}

async function openProduct(id) {
  const p = await api(`/api/products/${id}?user_id=${state.userId}`);
  const reviews = await api(`/api/reviews/product/${id}?limit=5`);

  const gallery = ((p.photo_urls && p.photo_urls.length ? p.photo_urls : (p.photos || []).map(imageUrl))).filter(Boolean);
  const mainPhoto = gallery[0] || productImageUrl(p, "photo");

  $("modalContent").innerHTML = `
    <img id="detailMainImage" class="detail-img" src="${mainPhoto}" alt="" onerror="this.replaceWith(Object.assign(document.createElement('div'),{className:'detail-img',textContent:'🍰'}))">
    ${gallery.length > 1 ? `<div class="photo-strip">${gallery.map((src, idx) => `<button class="thumb-button ${idx === 0 ? "active" : ""}" onclick="selectProductPhoto('${src.replaceAll("'", "\\'")}', this)"><img src="${src}" onerror="this.parentElement.style.display='none'"></button>`).join("")}</div>` : ""}
    <h2>${localizedProductName(p)}</h2>
    <p class="muted">${renderStars(p.rating)}</p>
    <p>${localizedProductDescription(p)}</p>
    <h3>${Number(p.price || 0).toFixed(2)} zł</h3>
    ${p.portion ? `<p class="muted">📦 ${tr("portion")}: ${p.portion}</p>` : ""}
    <div class="actions detail-actions">
      <button onclick="addToCart(${p.id})">🛒 ${tr("add")}</button>
      <button class="secondary" onclick="toggleFavorite(${p.id})">${p.is_favorite ? "💔 " + tr("removeFavorite") : "❤️ " + tr("favorite")}</button>
    </div>
    <hr class="reviews-divider">
    <h3 class="reviews-title">💬 ${tr("productReviews")}</h3>
    <div>${renderReviews(reviews)}</div>  `;
  $("modal").classList.remove("hidden");
}


function selectProductPhoto(src, button) {
  const main = $("detailMainImage");
  if (main) main.src = src;
  document.querySelectorAll(".thumb-button").forEach(btn => btn.classList.remove("active"));
  if (button) button.classList.add("active");
}

$("closeModal").addEventListener("click", () => $("modal").classList.add("hidden"));

async function addToCart(productId) {
  await api("/api/cart/add", {
    method: "POST",
    body: JSON.stringify({ user_id: state.userId, product_id: productId }),
  });
  haptic("success");
  toast(`🛒 ${tr("done")}`);
  await loadCart(false);
}

async function toggleFavorite(productId) {
  await api("/api/favorites/toggle", {
    method: "POST",
    body: JSON.stringify({ user_id: state.userId, product_id: productId }),
  });
  tg?.HapticFeedback?.impactOccurred?.("light");
  toast(`❤️ ${tr("done")}`);
  await loadFavorites();
}

async function loadCart(render = true) {
  const data = await api(`/api/cart/${state.userId}`);
  state.cart = data;
  const count = data.items.reduce((s, i) => s + Number(i.qty || 0), 0);
  $("cartBadge").textContent = count;
  $("cartBadge").classList.toggle("hidden", count === 0);
  if (render) renderCart(data);
}

function renderCart(data) {
  const container = $("cartItems");

  if (!data.items.length) {
    container.innerHTML = `<div class="empty">🛒 ${tr("emptyCart")}</div>`;
    return;
  }

  container.innerHTML = data.items.map(i => `
    <div class="cart-row">
      <div>
        <strong>${i.display_name || i.name}</strong>
        <div class="muted">${Number(i.final_subtotal || 0).toFixed(2)} zł</div>
        ${i.promo_code ? `<div class="muted">🎟 ${i.promo_code}: -${i.discount_percent}%</div>` : ""}
        <div style="display:flex;gap:6px;margin-top:8px">
          <input id="promo_${i.product_id}" placeholder="${tr("promo")}" style="padding:9px;margin:0">
          <button class="secondary" onclick="applyPromo(${i.product_id})">${tr("applyPromo")}</button>
        </div>
      </div>
      <div class="qty">
        <button onclick="changeQty(${i.product_id}, -1)">−</button>
        <span>${i.qty}</span>
        <button onclick="changeQty(${i.product_id}, 1)">+</button>
      </div>
    </div>
  `).join("") + `<div class="total">${tr("total")}: ${Number(data.total || 0).toFixed(2)} zł</div>`;
}

$("reloadCart").addEventListener("click", () => loadCart());

async function changeQty(productId, delta) {
  const data = await api("/api/cart/qty", {
    method: "POST",
    body: JSON.stringify({ user_id: state.userId, product_id: productId, delta }),
  });
  renderCart(data);
  await loadCart(false);
}

async function applyPromo(productId) {
  const code = $(`promo_${productId}`).value.trim();
  if (!code) return;
  const res = await api("/api/cart/promo", {
    method: "POST",
    body: JSON.stringify({ user_id: state.userId, product_id: productId, code }),
  });
  renderCart(res.cart);
  toast(res.success ? `🎟 ${tr("done")}` : "❌");
}

$("checkoutBtn").addEventListener("click", async () => {
  const name = $("orderName").value.trim();
  const phone = $("orderPhone").value.trim();
  const date = $("orderDate").value.trim();
  const comment = $("orderComment").value.trim();

  if (!name || !phone) return toast(tr("required"));

  try {
    const res = await api("/api/orders", {
      method: "POST",
      body: JSON.stringify({ user_id: state.userId, name, phone, date, comment }),
    });
    haptic("success");
    toast(`${tr("orderCreated")} #${res.id}`);
    $("orderComment").value = "";
    await loadCart();
    showTab("orders");
    await loadOrders();
  } catch (e) {
    toast(e.message);
  }
});

async function loadOrders() {
  const data = await api(`/api/orders/${state.userId}`);
  const orders = [...(data.orders || []), ...(data.custom_orders || [])].sort((a,b) => b.id - a.id);
  $("ordersList").innerHTML = orders.length ? orders.map(o => `
    <div class="order-row">
      <strong>${o.type === "custom" ? "🎂" : "📦"} #${o.id}</strong>
      <div class="muted">${tr("status")}: ${o.status || ""}</div>
      ${o.total ? `<div>${tr("total")}: ${Number(o.total).toFixed(2)} zł</div>` : ""}
      ${o.items ? `<div class="muted">${o.items.map(i => `${i.display_name || i.name} ×${i.qty}`).join("<br>")}</div>` : ""}
      ${o.description ? `<div class="muted">${o.description}</div>` : ""}
      ${o.type === "regular" && isCompletedOrder(o.status) && o.items && o.items.length ? `<button class="primary" onclick='startOrderReview(${JSON.stringify(o).replaceAll("'", "&apos;")})'>💬 ${tr("leaveOrderReview")}</button>` : ""}
    </div>
  `).join("") : `<div class="empty">📦 ${tr("empty")}</div>`;
}

function isCompletedOrder(status) {
  return ["Завершено", "Завершений", "Completed", "completed"].includes(status);
}

let orderReviewState = null;

function startOrderReview(order) {
  orderReviewState = {
    order,
    index: 0,
    items: (order.items || []).filter(i => i.product_id),
  };
  if (!orderReviewState.items.length) return toast(tr("empty"));
  showOrderReviewForm();
}

function showOrderReviewForm() {
  const stateReview = orderReviewState;
  const item = stateReview.items[stateReview.index];
  const customerName = stateReview.order.name || state.userName || "";
  $("modalContent").innerHTML = `
    <h2>${tr("leaveOrderReview")}</h2>
    <div class="form-card">
      <label>${tr("name")}</label>
      <input id="orderReviewName" value="${customerName}" readonly>
      <label>${tr("product")}</label>
      <input id="orderReviewProduct" value="${item.display_name || item.name}" readonly>
      <select id="orderReviewRating">
        <option value="5">⭐ 5</option>
        <option value="4">⭐ 4</option>
        <option value="3">⭐ 3</option>
        <option value="2">⭐ 2</option>
        <option value="1">⭐ 1</option>
      </select>
      <textarea id="orderReviewText" placeholder="${tr("reviewText")}"></textarea>
      <button class="primary" onclick="submitOrderReview()">${tr("confirmReview")}</button>
    </div>
  `;
  $("modal").classList.remove("hidden");
}

async function submitOrderReview() {
  const s = orderReviewState;
  const item = s.items[s.index];
  const name = $("orderReviewName").value.trim();
  const text = $("orderReviewText").value.trim();
  const rating = Number($("orderReviewRating").value || 5);
  if (!text) return toast(tr("required"));

  await api("/api/reviews", {
    method: "POST",
    body: JSON.stringify({
      user_id: state.userId,
      name,
      text,
      rating,
      review_type: "product",
      product_id: item.product_id,
      product_name: item.name || item.display_name || "",
      order_id: s.order.id,
    }),
  });

  s.index += 1;
  if (s.index < s.items.length) {
    toast(tr("done"));
    showOrderReviewForm();
  } else {
    $("modal").classList.add("hidden");
    toast(tr("done"));
  }
}

$("reloadOrders").addEventListener("click", () => loadOrders());

function hidePanels() {
  ["favoritesPanel", "reviewsPanel", "customPanel", "contactsPanel"].forEach(id => $(id).classList.add("hidden"));
}

$("favoritesBtn").addEventListener("click", async () => {
  hidePanels();
  $("favoritesPanel").classList.remove("hidden");
  await loadFavorites();
});

$("reviewsBtn").addEventListener("click", async () => {
  hidePanels();
  $("reviewsPanel").classList.remove("hidden");
  await loadReviews();
});

$("customBtn").addEventListener("click", () => {
  hidePanels();
  $("customPanel").classList.remove("hidden");
});

$("contactsBtn").addEventListener("click", () => {
  hidePanels();
  $("contactsPanel").classList.remove("hidden");
});

async function loadFavorites() {
  const products = await api(`/api/favorites/${state.userId}`);
  renderProducts(products, $("favoritesList"));
}

function renderReviews(rows) {
  if (!rows || !rows.length) return `<div class="empty">💬 ${tr("empty")}</div>`;
  return rows.map(r => `
    <div class="review-row">
      <strong>⭐ ${r.rating}/5 — ${r.name || "User"}</strong>
      <p>${r.text}</p>
    </div>
  `).join("");
}

async function loadReviews() {
  const rows = await api("/api/reviews?review_type=bakery&limit=5");
  $("reviewsList").innerHTML = renderReviews(rows);
}

$("sendReviewBtn").addEventListener("click", async () => {
  const name = $("reviewName").value.trim() || state.userName || "User";
  const text = $("reviewText").value.trim();
  const rating = Number($("reviewRating").value);
  if (!text || text.length < 3) return toast(tr("required"));

  await api("/api/reviews", {
    method: "POST",
    body: JSON.stringify({ user_id: state.userId, name, text, rating, review_type: "bakery" }),
  });
  $("reviewText").value = "";
  toast(tr("done"));
  await loadReviews();
});

$("sendCustomBtn").addEventListener("click", async () => {
  const name = $("customName").value.trim();
  const phone = $("customPhone").value.trim();
  const date = $("customDate").value.trim();
  const description = $("customDescription").value.trim();
  if (!name || !phone || !description) return toast(tr("required"));

  const res = await api("/api/custom-orders", {
    method: "POST",
    body: JSON.stringify({ user_id: state.userId, name, phone, date, description }),
  });
  toast(`${tr("orderCreated")} C#${res.id}`);
  $("customDescription").value = "";
  showTab("orders");
  await loadOrders();
});


bootstrap();
