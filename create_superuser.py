#!/usr/bin/env python
"""
Скрипт для создания суперпользователя в Django приложении Metateks

Использование:
    python create_superuser.py

Или через Docker:
    docker-compose exec web python create_superuser.py
"""

import os
import sys
import django

# Настройка Django окружения
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from apps.users.models import User

def create_admin_user():
    """Создает администратора если его еще нет"""

    email = 'admin@metateks.ru'
    password = '123456'

    print("=" * 70)
    print("СОЗДАНИЕ СУПЕРПОЛЬЗОВАТЕЛЯ")
    print("=" * 70)
    print()

    # Проверяем существует ли уже
    if User.objects.filter(email=email).exists():
        print(f"⚠ Пользователь с email {email} уже существует")
        user = User.objects.get(email=email)

        # Обновляем пароль и права
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        print(f"✓ Пароль обновлен, права администратора установлены")
    else:
        # Создаем нового пользователя
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name='Администратор',
            last_name='Системы'
        )
        print(f"✓ Суперпользователь создан успешно")

    print()
    print("Данные для входа:")
    print(f"  Email:    {email}")
    print(f"  Пароль:   {password}")
    print()
    print("Войдите в админку:")
    print("  http://5.188.138.16:8888/admin/")
    print()
    print("⚠ ВАЖНО: Смените пароль после первого входа!")
    print()
    print("=" * 70)

if __name__ == '__main__':
    try:
        create_admin_user()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
