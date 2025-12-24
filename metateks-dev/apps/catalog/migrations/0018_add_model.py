from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0017_add_model'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['order'], 'verbose_name': 'товар', 'verbose_name_plural': '4) Товары'},
        ),
        migrations.RemoveField(
            model_name='product',
            name='attrs',
        ),
        migrations.RemoveField(
            model_name='product',
            name='description',
        ),
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='tech_description',
        ),
        migrations.RemoveField(
            model_name='productphoto',
            name='product',
        ),
        migrations.RemoveField(
            model_name='productvideo',
            name='product',
        ),
        migrations.AlterField(
            model_name='product',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='catalog.productmodel', verbose_name='Модель'),
        ),
        migrations.AlterField(
            model_name='productphoto',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='photos', to='catalog.productmodel', verbose_name='Модель'),
        ),
        migrations.AlterField(
            model_name='productproperty',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='properties', to='catalog.product', verbose_name='Товар'),
        ),
        migrations.AlterField(
            model_name='productvideo',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='videos', to='catalog.productmodel', verbose_name='Модель'),
        ),
    ]
