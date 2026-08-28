from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_favoriteproduct'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_synced_with_b24',
            field=models.BooleanField(default=False, verbose_name='Синхронизирован с Битрикс24'),
        ),
    ]
