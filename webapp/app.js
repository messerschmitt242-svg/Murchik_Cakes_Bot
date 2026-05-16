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
    required: "Заповніть обов'язкові поля", done: "Готово", status: "Статус", portion: "Порція",
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
    required: "Заполните обязательные поля", done: "Готово", status: "Статус", portion: "Порция",
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
    required: "Wypełnij wymagane pola", done: "Gotowe", status: "Status", portion: "Porcja",
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
    required: "Fill required fields", done: "Done", status: "Status", portion: "Portion",
  }
};

const $ = (id) => document.getElementById(id);
const tr = (key) => (I18N[state.lang] || I18N.ua)[key] || key;

function setText() {
  $("subtitle").textContent = tr("subtitle");
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
  try {
    await api("/api/language", { method: "POST", body: JSON.stringify({ user_id: state.userId, language: state.lang }) });
  } catch {}
  loadProducts();
  loadCart(false);
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
      ${imageMarkup(p, "card-img", "label")}
      <h3>${p.display_name || p.name}</h3>
      ${p.portion ? `<div class="muted">📦 ${tr("portion")}: ${p.portion}</div>` : ""}
      <div class="rating">${renderStars(p.rating)}</div>
      <p>${(p.display_description || p.description || "").slice(0, 86)}</p>
      <div class="price">${Number(p.price || 0).toFixed(2)} zł</div>
      <div class="actions">
        <button onclick="addToCart(${p.id})">🛒 ${tr("add")}</button>
        <button class="secondary" onclick="openProduct(${p.id})">${tr("view")}</button>
      </div>
    </article>
  `).join("");
}

async function openProduct(id) {
  const p = await api(`/api/products/${id}?user_id=${state.userId}`);
  const reviews = await api(`/api/reviews/product/${id}?limit=5`);

  $("modalContent").innerHTML = `
    ${imageMarkup(p, "detail-img", "photo")}
    ${((p.photo_urls && p.photo_urls.length ? p.photo_urls : (p.photos || []).map(imageUrl))).filter(Boolean).length > 1 ? `<div class="photo-strip">${((p.photo_urls && p.photo_urls.length ? p.photo_urls : (p.photos || []).map(imageUrl))).filter(Boolean).map(src => `<img src="${src}" onerror="this.style.display='none'">`).join("")}</div>` : ""}
    <h2>${p.display_name || p.name}</h2>
    <p class="muted">${renderStars(p.rating)}</p>
    ${p.portion ? `<p class="muted">📦 ${tr("portion")}: ${p.portion}</p>` : ""}
    <p>${p.display_description || p.description || ""}</p>
    <h3>${Number(p.price || 0).toFixed(2)} zł</h3>
    <div class="actions">
      <button onclick="addToCart(${p.id})">🛒 ${tr("add")}</button>
      <button class="secondary" onclick="toggleFavorite(${p.id})">${p.is_favorite ? "💔" : "❤️"} ${tr("favorite")}</button>
    </div>
    <hr>
    <h3>💬 ${tr("productReviews")}</h3>
    <div>${renderReviews(reviews)}</div>
    <div class="form-card">
      <input id="productReviewName" placeholder="${tr("name")}" value="${state.userName || ""}">
      <textarea id="productReviewText" placeholder="${tr("reviewText")}"></textarea>
      <select id="productReviewRating">
        <option value="5">⭐ 5</option>
        <option value="4">⭐ 4</option>
        <option value="3">⭐ 3</option>
        <option value="2">⭐ 2</option>
        <option value="1">⭐ 1</option>
      </select>
      <button class="primary" onclick="sendProductReview(${p.id}, '${String(p.display_name || p.name).replaceAll("'", "\\'")}')">${tr("sendReview")}</button>
    </div>
  `;
  $("modal").classList.remove("hidden");
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
    </div>
  `).join("") : `<div class="empty">📦 ${tr("empty")}</div>`;
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

async function sendProductReview(productId, productName) {
  const name = $("productReviewName").value.trim() || state.userName || "User";
  const text = $("productReviewText").value.trim();
  const rating = Number($("productReviewRating").value);
  if (!text || text.length < 3) return toast(tr("required"));

  await api("/api/reviews", {
    method: "POST",
    body: JSON.stringify({ user_id: state.userId, name, text, rating, review_type: "product", product_id: productId, product_name: productName }),
  });
  toast(tr("done"));
  await openProduct(productId);
}

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
