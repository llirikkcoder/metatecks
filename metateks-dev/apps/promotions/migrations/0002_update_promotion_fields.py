from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0019_add_model'),
        ('promotions', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promotion',
            name='products',
        ),
        migrations.AddField(
            model_name='promotion',
            name='model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='promotions', to='catalog.productmodel', verbose_name='Модель по акции'),
        ),
        migrations.AddField(
            model_name='promotion',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='promotions', to='catalog.product', verbose_name='Товар по акции', help_text='в случае, если не выбрана модель'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='end_dt',
            field=models.DateField(blank=True, help_text='оставьте пустым для бессрочной акции', null=True, verbose_name='Дата окончания акции'),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='start_dt',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Дата начала акции'),
        ),
    ]
