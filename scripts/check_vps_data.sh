#!/bin/bash

# ============================================================================
# Скрипт проверки данных на VPS (что нужно переносить)
# ============================================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

VPS_USER="${VPS_USER:-your_user}"
VPS_HOST="${VPS_HOST:-your_vps_ip}"
VPS_PATH="${VPS_PATH:-/home/mt/metateks-dev}"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Проверка данных на VPS${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

if [ "$VPS_USER" == "your_user" ] || [ "$VPS_HOST" == "your_vps_ip" ]; then
    echo -e "${RED}ОШИБКА: Настройте параметры подключения!${NC}"
    echo "export VPS_USER=\"ваш_пользователь\""
    echo "export VPS_HOST=\"ip_адрес_vps\""
    echo "export VPS_PATH=\"/путь/к/проекту\""
    exit 1
fi

echo -e "${BLUE}Подключение к VPS: $VPS_USER@$VPS_HOST${NC}"
echo ""

ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
cd /home/mt/metateks-dev

# Активация виртуального окружения
if [ -f ~/.virtualenvs/metateks/bin/activate ]; then
    source ~/.virtualenvs/metateks/bin/activate
fi

echo "============================================================"
echo "  АНАЛИЗ ДАННЫХ НА VPS"
echo "============================================================"
echo ""

python manage.py shell << 'PYEOF'
from apps.users.models import User
from apps.orders.models import Order
from apps.content.models import Page, News
from apps.banners.models import Banner
from apps.catalog.models import Product, Category
from apps.promotions.models import Promotion
from apps.settings.models import SiteSetting
from apps.addresses.models import City, Warehouse

print("=" * 60)
print("  ВАЖНЫЕ ДАННЫЕ (НУЖНО ПЕРЕНОСИТЬ)")
print("=" * 60)

# Пользователи
users_count = User.objects.count()
active_users = User.objects.filter(is_active=True).count()
print(f"\n👤 Пользователи:")
print(f"   Всего: {users_count}")
print(f"   Активных: {active_users}")
if users_count > 0:
    print("   ⚠️  НУЖНО ПЕРЕНОСИТЬ! (регистрации пользователей)")
else:
    print("   ✅ Пользователей нет, переносить не нужно")

# Заказы
orders_count = Order.objects.count()
recent_orders = Order.objects.filter(created_at__gte='2024-01-01').count()
print(f"\n🛒 Заказы:")
print(f"   Всего: {orders_count}")
print(f"   За 2024 год: {recent_orders}")
if orders_count > 0:
    print("   ⚠️  НУЖНО ПЕРЕНОСИТЬ! (история заказов)")
else:
    print("   ✅ Заказов нет, переносить не нужно")

# CMS контент
pages_count = Page.objects.count()
news_count = News.objects.count()
print(f"\n📄 CMS контент:")
print(f"   Страниц: {pages_count}")
print(f"   Новостей: {news_count}")
if pages_count > 0 or news_count > 0:
    print("   ⚠️  НУЖНО ПЕРЕНОСИТЬ! (контент сайта)")
else:
    print("   ✅ Контента нет")

# Баннеры
banners_count = Banner.objects.count()
print(f"\n🎨 Баннеры: {banners_count}")
if banners_count > 0:
    print("   ⚠️  НУЖНО ПЕРЕНОСИТЬ!")
else:
    print("   ✅ Баннеров нет")

# Промо-акции
try:
    promotions_count = Promotion.objects.count()
    print(f"\n🎁 Промо-акции: {promotions_count}")
    if promotions_count > 0:
        print("   ⚠️  НУЖНО ПЕРЕНОСИТЬ!")
except:
    print(f"\n🎁 Промо-акции: таблица не существует")

# Города/склады
cities_count = City.objects.count()
warehouses_count = Warehouse.objects.count()
print(f"\n📍 Города и склады:")
print(f"   Городов: {cities_count}")
print(f"   Складов: {warehouses_count}")
if cities_count > 0:
    print("   ⚠️  НУЖНО ПЕРЕНОСИТЬ! (настройки городов)")

# Настройки сайта
try:
    settings_count = SiteSetting.objects.count()
    print(f"\n⚙️  Настройки сайта: {settings_count}")
    if settings_count > 0:
        print("   ⚠️  НУЖНО ПЕРЕНОСИТЬ!")
except:
    print(f"\n⚙️  Настройки сайта: таблица не существует")

print("\n" + "=" * 60)
print("  ДАННЫЕ ИЗ 1С (ПЕРЕНОСИТЬ НЕ НУЖНО)")
print("=" * 60)

# Каталог (из 1С)
products_count = Product.objects.count()
products_1c = Product.objects.filter(is_synced_with_1c=True).count()
categories_count = Category.objects.count()
print(f"\n📦 Каталог товаров:")
print(f"   Товаров: {products_count}")
print(f"   Из них из 1С: {products_1c}")
print(f"   Категорий: {categories_count}")
print("   ✅ Придет из 1С автоматически, переносить не нужно")

print("\n" + "=" * 60)
print("\n💡 РЕКОМЕНДАЦИЯ:\n")

need_migration = False

if users_count > 0:
    print("⚠️  У вас есть пользователи - ОБЯЗАТЕЛЬНО нужно перенести БД!")
    need_migration = True

if orders_count > 0:
    print("⚠️  У вас есть заказы - ОБЯЗАТЕЛЬНО нужно перенести БД!")
    need_migration = True

if pages_count > 0 or news_count > 0:
    print("⚠️  У вас есть CMS контент - нужно перенести БД!")
    need_migration = True

if not need_migration:
    print("✅ Критичных данных нет - можно начать с чистой базы!")
    print("   Каталог товаров получите из 1С автоматически.")
else:
    print("\n📋 Перенесите базу данных с VPS:")
    print("   ./scripts/migrate_from_vps.sh")
    print("\n   Или используйте команды из DATABASE_MIGRATION.md")

print("")
PYEOF

ENDSSH

echo ""
echo -e "${GREEN}Проверка завершена!${NC}"
