from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CallbackRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('name', models.CharField(blank=True, max_length=63, null=True, verbose_name='Имя')),
                ('phone', models.CharField(max_length=63, verbose_name='Телефон')),
                ('ip_address', models.CharField(blank=True, max_length=40, null=True, verbose_name='IP-адрес')),
                ('is_synced_with_b24', models.BooleanField(default=False, verbose_name='Синхронизирован с Битрикс24?')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'заказ обратного звонка',
                'verbose_name_plural': 'заказы обратного звонка',
                'ordering': ['-created_at'],
            },
        ),
    ]
