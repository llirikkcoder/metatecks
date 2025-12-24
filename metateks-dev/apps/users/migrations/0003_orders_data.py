from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
        ('users', '0002_rename_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='delivery_company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='orders.deliverycompany', verbose_name='Транспортная компания'),
        ),
        migrations.AddField(
            model_name='user',
            name='delivery_method',
            field=models.CharField(blank=True, choices=[('pickup', 'Самовывоз'), ('metateks', 'Транспортом Метатэкс'), ('company', 'Транспортной компанией')], max_length=15, null=True, verbose_name='Способ доставки'),
        ),
        migrations.AddField(
            model_name='user',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('online', 'Оплата онлайн'), ('non_cash', 'Безналичная оплата'), ('on_receipt', 'Оплата при получении')], max_length=15, null=True, verbose_name='Метод оплаты'),
        ),
    ]
