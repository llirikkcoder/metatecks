from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0008_category_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='description',
            field=models.TextField(blank=True, help_text='рядом с заголовком', verbose_name='Описание страницы'),
        ),
        migrations.AlterField(
            model_name='page',
            name='slug',
            field=models.CharField(max_length=255, unique=True, verbose_name='Адрес в url'),
        ),
    ]
