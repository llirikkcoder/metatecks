from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0002_load_data'),
        ('orders', '0008_cashless_data_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='addresses.warehouse', verbose_name='Склад'),
        ),
    ]
