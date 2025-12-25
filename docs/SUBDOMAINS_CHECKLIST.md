# Чеклист: Настройка поддоменов городов

Быстрая инструкция для внедрения поддоменов.

---

## ✅ ДА - Текущий Docker ПОЛНОСТЬЮ ГОТОВ!

**Не нужно ничего менять в архитектуре.**

Только 3 конфига + код middleware.

---

## 📋 Что нужно сделать

### 1️⃣ Обновить Nginx (1 файл)

**Файл:** `docker/nginx/conf.d/default.conf`

```nginx
server {
    listen 80;
    server_name metateks.ru *.metateks.ru admin.metateks.ru;
    
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;  # ← ВАЖНО для поддоменов
        ...
    }
}
```

### 2️⃣ Обновить .env.docker (1 файл)

```bash
ALLOWED_HOSTS=metateks.ru *.metateks.ru admin.metateks.ru
CSRF_TRUSTED_ORIGINS=https://metateks.ru https://*.metateks.ru
SESSION_COOKIE_DOMAIN=.metateks.ru
CSRF_COOKIE_DOMAIN=.metateks.ru
```

### 3️⃣ Создать middleware (1 файл)

**Файл:** `apps/addresses/subdomain_middleware.py`

```python
class CitySubdomainMiddleware:
    def process_request(self, request):
        host = request.get_host().split(':')[0]
        parts = host.split('.')
        
        if len(parts) > 2:
            city_slug = parts[0]
            request.city = City.objects.get(slug=city_slug)
        else:
            request.city = detect_city_by_ip(request)
```

Добавить в `MIDDLEWARE` в settings.

### 4️⃣ Настроить DNS

У регистратора домена:

```
A    @      ВАШ_IP
A    *      ВАШ_IP
A    admin  ВАШ_IP
```

### 5️⃣ Получить SSL

```bash
certbot certonly --manual --preferred-challenges=dns \
  -d metateks.ru -d *.metateks.ru
```

### 6️⃣ Деплой

```bash
docker-compose restart web nginx
```

---

## 🧪 Локальное тестирование (БЕЗ домена)

**1. /etc/hosts:**
```
127.0.0.1  metateks.local msk.metateks.local spb.metateks.local
```

**2. nginx:**
```nginx
server_name metateks.local *.metateks.local;
```

**3. .env.docker:**
```bash
ALLOWED_HOSTS=metateks.local *.metateks.local
SESSION_COOKIE_DOMAIN=.metateks.local
```

**4. Тест:**
```bash
curl http://msk.metateks.local/
```

---

## 📊 Схема работы

```
msk.metateks.ru
    ↓
Nginx (видит *.metateks.ru → OK)
    ↓
Django Middleware (извлекает "msk")
    ↓
City.objects.get(slug='msk')
    ↓
request.city = Москва
    ↓
View фильтрует товары по городу
```

---

## ✅ Проверка

```bash
# 1. Nginx
docker-compose exec nginx nginx -t

# 2. Django
docker-compose logs web | grep -i error

# 3. Curl
curl -H "Host: msk.metateks.ru" http://localhost/

# 4. Браузер
http://msk.metateks.local/  (если настроили /etc/hosts)
```

---

## 🚨 Частые ошибки

### "Invalid HTTP_HOST header"

**Причина:** Не добавили домен в ALLOWED_HOSTS

**Решение:**
```bash
ALLOWED_HOSTS=metateks.ru *.metateks.ru
```

### Сессии не работают между поддоменами

**Причина:** Не настроили SESSION_COOKIE_DOMAIN

**Решение:**
```bash
SESSION_COOKIE_DOMAIN=.metateks.ru  # С ТОЧКОЙ!
```

### CSRF ошибки

**Причина:** Не добавили в CSRF_TRUSTED_ORIGINS

**Решение:**
```bash
CSRF_TRUSTED_ORIGINS=https://metateks.ru https://*.metateks.ru
```

---

## 📦 Структура файлов

```
docker/nginx/conf.d/default.conf   ← Обновить server_name
.env.docker                        ← Добавить домены
apps/addresses/
  └── subdomain_middleware.py      ← Создать
main/settings/base.py              ← Добавить middleware в MIDDLEWARE
```

---

## 🎯 Минимум для запуска

**Если нужно быстро проверить концепцию:**

1. Только `/etc/hosts` + `*.metateks.local`
2. Только middleware (без DNS, без SSL)
3. Локальный тест

**Время:** 15 минут

---

## 💡 Преимущества

✅ Один Docker для всех городов
✅ Одна база данных
✅ Общие сессии пользователей
✅ Легко добавить новый город
✅ SEO-friendly URLs
✅ Один SSL сертификат (wildcard)

---

## 📞 Помощь

Полная документация: [SUBDOMAINS_SETUP.md](SUBDOMAINS_SETUP.md)

**Важно:** Текущая архитектура Docker УЖЕ ГОТОВА для поддоменов!
