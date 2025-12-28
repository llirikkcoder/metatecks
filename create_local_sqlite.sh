#!/bin/bash
#
# Создание SQLite базы локально для коммита в git
# Использует Python в Docker контейнере
#

set -e

echo "=============================================================================="
echo "СОЗДАНИЕ SQLITE БАЗЫ ЛОКАЛЬНО"
echo "=============================================================================="
echo ""

# Удалить старую базу если есть
rm -f db.sqlite3

echo "Создание новой базы через Python..."
echo ""

# Создать базу через python3 с минимальными зависимостями
cat > /tmp/create_sqlite.py << 'PYEOF'
import sqlite3

# Создать пустую SQLite базу
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Создать минимальную таблицу чтобы база не была полностью пустой
cursor.execute('''
CREATE TABLE IF NOT EXISTS django_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied DATETIME NOT NULL
)
''')

conn.commit()
conn.close()

print("✓ SQLite база создана: db.sqlite3")
print("  Размер:", end=" ")

import os
size = os.path.getsize('db.sqlite3')
if size < 1024:
    print(f"{size} bytes")
elif size < 1024*1024:
    print(f"{size/1024:.1f} KB")
else:
    print(f"{size/(1024*1024):.1f} MB")
PYEOF

# Запустить скрипт
python3 /tmp/create_sqlite.py

echo ""
echo "=============================================================================="
echo "✅ БАЗА СОЗДАНА!"
echo "=============================================================================="
echo ""
echo "Файл: db.sqlite3"
ls -lh db.sqlite3
echo ""
echo "На Railway при деплое автоматически применятся все миграции Django."
echo ""
echo "Следующие шаги:"
echo "  1. git add db.sqlite3 .gitignore main/settings/base.py"
echo "  2. git commit -m 'Add SQLite for Railway deployment with USE_SQLITE env'"
echo "  3. git push origin feature/seo-improve"
echo ""
echo "После пуша проверь Railway:"
echo "  - Логи покажут применение миграций"
echo "  - Сайт запустится с пустой базой"
echo "  - Можешь добавить данные через админку Railway"
echo ""
echo "Для работы с базой локально:"
echo "  - Установи Python виртуальное окружение"
echo "  - Или используй Django shell через Railway"
echo ""
echo "=============================================================================="

# Удалить временный скрипт
rm /tmp/create_sqlite.py
