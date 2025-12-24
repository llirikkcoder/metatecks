from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0003_update_promotion_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='promotion',
            options={'ordering': ['start_dt', 'end_dt'], 'verbose_name': 'акция', 'verbose_name_plural': 'акции'},
        ),
        migrations.AddField(
            model_name='promotion',
            name='banner_design',
            field=models.CharField(choices=[('light', 'светлый фон, черный текст'), ('dark', 'темный фон, светлый текст')], default='light', max_length=7, verbose_name='Оформление баннера'),
        ),
    ]
