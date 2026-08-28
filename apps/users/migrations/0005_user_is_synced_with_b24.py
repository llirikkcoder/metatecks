from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Поле is_synced_with_b24 давно объявлено в модели User, но миграции под
    него не было, при этом в базах прода и локальной разработки колонка уже
    существует (создана вне миграций). ADD COLUMN IF NOT EXISTS корректно
    отрабатывает и на базе с колонкой, и на чистой.
    """

    dependencies = [
        ('users', '0004_favoriteproduct'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        'ALTER TABLE users_user '
                        'ADD COLUMN IF NOT EXISTS is_synced_with_b24 boolean NOT NULL DEFAULT false;'
                    ),
                    reverse_sql=(
                        'ALTER TABLE users_user '
                        'DROP COLUMN IF EXISTS is_synced_with_b24;'
                    ),
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='user',
                    name='is_synced_with_b24',
                    field=models.BooleanField(default=False, verbose_name='Синхронизирован с Битрикс24'),
                ),
            ],
        ),
    ]
