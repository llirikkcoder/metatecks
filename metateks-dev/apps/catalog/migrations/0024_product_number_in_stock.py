from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0023_subcategory_attribute_in_filter'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='number_in_stock',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Максимальное количество на складе'),
        ),
    ]
