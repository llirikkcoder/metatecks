from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0003_reorganize_address_models'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserDeliveryAddressData',
            new_name='UserDeliveryAddress',
        ),
        migrations.RenameModel(
            old_name='UserPaymentCardData',
            new_name='UserPaymentCard',
        ),
    ]
