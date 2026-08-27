# URL Шпаргалка - Метатэкс

Быстрый справочник по всем URL проекта.

---

## 🌐 Домены

```
Production:
  🌍 metateks-admin.vinodesign.ru              # Основной сайт
  🔐 metateks-admin.vinodesign.ru   # Админка

Development:
  💻 localhost:80                   # Через nginx
  💻 localhost:8000                 # Прямой доступ к Django
```

---

## 📄 Основные страницы

```
/                      Главная
/catalog/              Каталог
/brands/               Бренды
/about/                О компании
/news/                 Новости
/articles/             Статьи
/cart/                 Корзина
/promotions/           Акции
/search/?q=запрос      Поиск
/account/              Личный кабинет
```

---

## 🛒 Личный кабинет

```
/account/              Главная ЛК
/account/orders/       Заказы
/account/addresses/    Адреса
/account/favorites/    Избранное
/account/profile/      Профиль
```

---

## 🔌 API

### Аутентификация
```
POST /api/auth/login/          {"email": "...", "password": "..."}
POST /api/auth/logout/
POST /api/auth/registration/   {"email": "...", "password": "..."}
POST /api/auth/reset_password/ {"email": "..."}
```

### Корзина
```
POST /api/cart/update_item/       {"product_id": 123, "quantity": 2}
POST /api/cart/update_extra_item/ {"extra_product_id": 5, "quantity": 1}
POST /api/cart/group_toggle/      {"group": "warehouse_123"}
POST /api/cart/clear_cart/
```

### Избранное
```
POST /api/favorites/add/          {"product_id": 123}
POST /api/favorites/remove/       {"product_id": 123}
```

### Адреса
```
GET /api/addresses/cities/        Список городов
GET /api/addresses/warehouses/    Список складов
```

---

## 🔧 Админка

```
/admin/                     Django Admin
/admin/login/               Вход
/admin/catalog/product/     Товары
/admin/orders/order/        Заказы
/admin/users/user/          Пользователи
```

---

## 🔗 Интеграция 1С

```bash
# Проверка авторизации
curl -u "user:pass" "http://localhost/cml/1c_exchange.php?type=catalog&mode=checkauth"

# Инициализация
curl -u "user:pass" "http://localhost/cml/1c_exchange.php?type=catalog&mode=init"

# Загрузка файла
curl -u "user:pass" -F "filename=@import.xml" \
  "http://localhost/cml/1c_exchange.php?type=catalog&mode=file&filename=import.xml"

# Импорт
curl -u "user:pass" \
  "http://localhost/cml/1c_exchange.php?type=catalog&mode=import&filename=import.xml"
```

---

## 📊 Примеры URL товаров

```
# Прямая ссылка по ID
/catalog/p/12345/

# Полный путь
/catalog/zapchasti/filtry/maslyanyj-filtr-12345/

# Фильтр по модели
/catalog/zapchasti/filtry/model123/

# Фильтр по бренду
/catalog/zapchasti/filtry/xcmg/

# С фильтром
/catalog/zapchasti/filtry/filter/?price_min=1000&price_max=5000
```

---

## 🎨 Статические файлы

```
/static/           Собранные статические файлы
/media/            Загруженные медиа
/css/              CSS (из assets)
/js/               JavaScript (из assets)
/fonts/            Шрифты (из assets)
/images/           Статические изображения (из assets)
```

---

## 🚨 Служебные

```
/health/           ⚠️  Требуется реализовать
/sitemap.xml       ❌ Не реализовано
/robots.txt        ❌ Не реализовано
/favicon.ico       ✓  assets/favicon.svg
```

---

## 🧪 Тестирование

```bash
# Проверить главную
curl http://localhost/

# Проверить API
curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.ru", "password": "12345"}'

# Проверить 1С
curl -u "1c_user:password" \
  "http://localhost/cml/1c_exchange.php?type=catalog&mode=checkauth"

# Проверить healthcheck
curl http://localhost/health/
```

---

## 🔍 Поиск и фильтры

```
# Поиск
/search/?q=фильтр

# Фильтры в каталоге (GET параметры)
?price_min=1000
?price_max=5000
?brand=xcmg
?in_stock=true
?sort=price_asc
?sort=price_desc
?sort=name
```

---

## 📱 AJAX запросы (примеры)

```javascript
// Добавить в корзину
fetch('/api/cart/update_item/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({
    product_id: 123,
    quantity: 1
  })
})

// Добавить в избранное
fetch('/api/favorites/add/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({
    product_id: 123
  })
})

// Авторизация
fetch('/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
})
```

---

**Совет:** Все POST запросы требуют CSRF токен в заголовке `X-CSRFToken`!
