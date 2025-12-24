from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0002_load_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='seosetting',
            name='header_text',
            field=models.TextField(blank=True, default='', max_length=255, verbose_name='Описание страницы (рядом с заголовком)'),
        ),
    ]
