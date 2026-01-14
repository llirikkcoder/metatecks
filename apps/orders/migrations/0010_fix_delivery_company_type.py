from django.db import migrations, connection


def drop_orphaned_delivery_company_type(apps, schema_editor):
    """
    Удаляет composite type orders_deliverycompany ТОЛЬКО если он "сиротский"
    (тип существует, но таблица НЕ существует).

    PostgreSQL автоматически создает composite type для каждой таблицы.
    При миграции вниз (удаление таблицы) тип может остаться, что вызывает
    IntegrityError при повторной миграции вверх (создание таблицы).

    Если таблица существует, мы НЕ удаляем тип - это нормальное состояние.
    """
    with connection.cursor() as cursor:
        # Проверяем: существует ли тип И НЕ существует ли таблица
        cursor.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_type
                    WHERE typname = 'orders_deliverycompany'
                    AND typtype = 'c'
                ) AND NOT EXISTS (
                    SELECT 1 FROM pg_tables
                    WHERE schemaname = 'public'
                    AND tablename = 'orders_deliverycompany'
                ) THEN
                    -- Тип "сиротский" - безопасно удаляем
                    DROP TYPE IF EXISTS orders_deliverycompany CASCADE;
                    RAISE NOTICE 'Dropped orphaned type: orders_deliverycompany';
                ELSE
                    RAISE NOTICE 'Type cleanup skipped: table exists or type does not exist';
                END IF;
            END $$;
        """)


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0009_order_warehouse'),
    ]

    operations = [
        migrations.RunPython(drop_orphaned_delivery_company_type, reverse_code=migrations.RunPython.noop),
    ]
