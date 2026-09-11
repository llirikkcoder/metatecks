# Документация проекта Метатэкс

## 📚 Оглавление

### 🚀 Быстрый старт
- **[Быстрый старт миграции](MIGRATION_QUICK_START.md)** - Основные команды для миграции с VPS
- **[Быстрая настройка Health Endpoint](QUICK_SETUP_HEALTH.md)** - 5-минутная настройка healthcheck

### 🌐 Структура и URL
- **[Структура URL и доменов](URL_STRUCTURE.md)** - Полная документация по всем URL проекта
- **[Шпаргалка URL](URL_CHEATSHEET.md)** - Быстрый справочник по всем endpoint'ам
- **[Архитектура хранилища](STORAGE_ARCHITECTURE.md)** - Структура хранения данных

### 🔄 Миграция данных
- **[Миграция с VPS](MIGRATION_FROM_VPS.md)** - Полная инструкция по миграции
- **[Итоговая конфигурация](SUMMARY.md)** - Обзор настроек проекта

### 📝 CMS и контент
- **[Руководство по CMS](CMS_GUIDE.md)** - Управление контентом через админ-панель
- **[Хранилище CMS](CMS_STORAGE.md)** - Где и как хранятся данные CMS

### 🛒 Каталог и 1С
- **[Каталог: сортировка и характеристики](CATALOG_ADMIN_NOTES.md)** - Как работает порядок товаров и характеристик, частые вопросы администратора, грабли
- **[Интеграция с 1С](1C_INTEGRATION.md)** - Обмен CommerceML, группы, разбор простоя 2025-2026
- **[Мониторинг 1С](1C_MONITORING.md)** - Контроль состояния обмена

### 🔐 Безопасность
- **[Безопасность Docker](DOCKER_SECURITY.md)** - Контрольный список безопасности для production

### 🌍 Поддомены и мультигород
- **[Настройка поддоменов](SUBDOMAINS_SETUP.md)** - Полное руководство по настройке городских поддоменов
- **[Чеклист поддоменов](SUBDOMAINS_CHECKLIST.md)** - Краткий план внедрения

### 💾 Бэкап и восстановление
- **[Бэкап Docker Volumes](DOCKER_VOLUMES_BACKUP.md)** - Полное руководство по бэкапу данных
- Скрипты: `scripts/backup_volumes.sh`, `scripts/restore_volumes.sh`

---

## 📖 Руководства по темам

### Для разработчиков

**URL и Routing:**
1. [URL_STRUCTURE.md](URL_STRUCTURE.md) - Изучите полную структуру URL
2. [URL_CHEATSHEET.md](URL_CHEATSHEET.md) - Используйте как справочник

**Разработка:**
- main/urls.py - Главный роутинг
- apps/*/urls.py - URL модулей
- apps/api/*/urls.py - API endpoints

### Для администраторов

**Первый запуск:**
1. [MIGRATION_QUICK_START.md](MIGRATION_QUICK_START.md) - Запуск за 5 минут
2. [QUICK_SETUP_HEALTH.md](QUICK_SETUP_HEALTH.md) - Настройка healthcheck
3. [DOCKER_SECURITY.md](DOCKER_SECURITY.md) - Проверьте безопасность

**Production развертывание:**
1. Смените пароли ([DOCKER_SECURITY.md](DOCKER_SECURITY.md))
2. Настройте домены ([URL_STRUCTURE.md](URL_STRUCTURE.md#настройка-доменов))
3. Настройте SSL/HTTPS
4. Настройте бэкапы

### Для контент-менеджеров

**Работа с CMS:**
1. [CMS_GUIDE.md](CMS_GUIDE.md) - Полное руководство
2. [CMS_STORAGE.md](CMS_STORAGE.md) - Понимание хранилища
3. http://localhost/admin/ - Вход в админку

---

## 🎯 Быстрые ссылки

### Текущие endpoint'ы

**Frontend:**
- `/` - Главная
- `/catalog/` - Каталог
- `/admin/` - Админка
- `/account/` - Личный кабинет

**API:**
- `/api/auth/login/` - Авторизация
- `/api/cart/` - Корзина
- `/api/favorites/` - Избранное

**Интеграции:**
- `/cml/1c_exchange.php` - 1С обмен
- `/health/` - ⚠️ Требует реализации

### Важные файлы конфигурации

```
├── docker-compose.yml        # Конфигурация Docker
├── .env.docker               # Переменные окружения
├── main/urls.py              # Главный роутинг
├── nginx/conf.d/default.conf # Nginx конфигурация
└── docs/                     # Вся документация
```

---

## 📊 Статус реализации

### ✅ Реализовано

- [x] Все основные страницы (главная, каталог, товары)
- [x] Личный кабинет (заказы, избранное, профиль)
- [x] API для корзины, авторизации, адресов
- [x] Интеграция с 1С (CommerceML)
- [x] Админ-панель Django
- [x] Docker контейнеризация
- [x] Nginx reverse proxy
- [x] Адаптивная верстка

### ⚠️ Требует внимания

- [ ] `/health/` endpoint - **КРИТИЧНО** для healthcheck
- [ ] `/sitemap.xml` - для SEO
- [ ] `/robots.txt` - для SEO
- [ ] Rate limiting - для безопасности API
- [ ] API документация (Swagger)

### ❌ Не реализовано (опционально)

- [ ] Сравнение товаров
- [ ] Отзывы о товарах
- [ ] Подписка на рассылку
- [ ] PWA (Progressive Web App)
- [ ] Мультиязычность

---

## 🔍 Поиск по документации

**Нужно настроить домены?**
→ [URL_STRUCTURE.md#настройка-доменов](URL_STRUCTURE.md#настройка-доменов)

**Нужно узнать какой URL для API?**
→ [URL_CHEATSHEET.md](URL_CHEATSHEET.md#api)

**Как реализовать /health/?**
→ [QUICK_SETUP_HEALTH.md](QUICK_SETUP_HEALTH.md)

**Нужно мигрировать с VPS?**
→ [MIGRATION_FROM_VPS.md](MIGRATION_FROM_VPS.md)

**Как работать с CMS?**
→ [CMS_GUIDE.md](CMS_GUIDE.md)

**Как настроить безопасность?**
→ [DOCKER_SECURITY.md](DOCKER_SECURITY.md)

---

## 📞 Получение помощи

1. **Проверьте документацию** - 99% вопросов уже описаны
2. **Проверьте логи:**
   ```bash
   docker-compose logs -f web     # Django
   docker-compose logs -f nginx   # Nginx
   tail -f logs/*.log             # Файловые логи
   ```
3. **Проверьте статус:**
   ```bash
   docker-compose ps              # Статус контейнеров
   curl http://localhost/health/  # Healthcheck (когда реализуете)
   ```

---

**Последнее обновление:** 2025-12-25  
**Версия документации:** 1.0
