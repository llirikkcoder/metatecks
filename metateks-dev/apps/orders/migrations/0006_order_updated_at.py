from django.db import migrations, models


def set_updated_at(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    Order.objects.update(updated_at=models.F('created_at'))


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_update_non_cash_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.RunPython(set_updated_at, reverse_code=migrations.RunPython.noop),
    ]
