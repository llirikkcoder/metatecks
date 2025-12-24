from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='item_subtitle',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Подзаголовок товара'),
        ),
    ]
