from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0025_product_is_in_stock'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AdditionalProduct',
            new_name='ExtraProduct',
        ),
    ]
