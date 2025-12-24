from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0013_update_attribute_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttributeFilterOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('filter_type', models.CharField(choices=[('eq', 'Равно'), ('gte', 'От'), ('lte', 'До')], default='eq', max_length=3, verbose_name='Тип')),
                ('value_int', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Значение (целое число)')),
                ('value_float', models.FloatField(blank=True, null=True, verbose_name='Значение (дробное число)')),
                ('value_string', models.CharField(blank=True, max_length=31, null=True, verbose_name='Значение (строка)')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filter_options', to='catalog.attribute', verbose_name='Характеристика')),
            ],
            options={
                'verbose_name': 'вариант',
                'verbose_name_plural': 'характеристики: варианты в фильтре',
                'ordering': ['order'],
            },
        ),
    ]
