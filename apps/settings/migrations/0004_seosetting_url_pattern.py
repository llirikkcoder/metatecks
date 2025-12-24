from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0003_seosetting_header_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='seosetting',
            name='url_pattern',
            field=models.CharField(blank=True, default='', max_length=31, verbose_name='URL pattern'),
        ),
        migrations.AlterField(
            model_name='seosetting',
            name='header_text',
            field=models.TextField(blank=True, default='', verbose_name='Описание страницы (рядом с заголовком)'),
        ),
    ]
