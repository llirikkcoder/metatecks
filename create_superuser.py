#!/usr/bin/env python
"""
Скрипт для создания суперпользователя
Запускать: railway run python create_superuser.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from apps.users.models import User

email = 'admin@metateks.ru'
password = 'MetaTeks2025Admin!'

if User.objects.filter(email=email).exists():
    print(f'✓ Пользователь {email} уже существует')
    user = User.objects.get(email=email)
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f'✓ Пароль обновлён')
else:
    user = User.objects.create_superuser(
        email=email,
        password=password,
        first_name='Admin',
        last_name='Metateks'
    )
    print(f'✓ Создан суперпользователь {email}')

print(f'\n=== УЧЁТНЫЕ ДАННЫЕ ===')
print(f'URL: https://metatecks-production.up.railway.app/admin/')
print(f'Email: {email}')
print(f'Пароль: {password}')
print(f'======================\n')
