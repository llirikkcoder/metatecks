from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0026_extra_products_rename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extraproduct',
            name='sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='extra_products', to='catalog.subcategory', verbose_name='Подкатегория'),
        ),
    ]
