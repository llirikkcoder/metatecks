from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0024_product_number_in_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_in_stock',
            field=models.BooleanField(default=False, verbose_name='Есть на складе?'),
        ),
    ]
