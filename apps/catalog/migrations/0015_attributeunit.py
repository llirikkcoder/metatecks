from django.db import migrations, models
import django.db.models.deletion


def clear_unit(apps, schema_editor):
    Attribute = apps.get_model('catalog', 'Attribute')
    Attribute.objects.all().update(unit=None)


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0014_attributefilteroption'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttributeUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('name', models.CharField(max_length=31, verbose_name='Название')),
                ('name_html', models.CharField(blank=True, max_length=31, verbose_name='Отображение на сайте')),
                ('icon', models.CharField(choices=[('kg', 'вес'), ('gear', 'другое')], default='gear', max_length=7, verbose_name='Иконка')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'единица измерения',
                'verbose_name_plural': 'характеристики: единицы измерения',
                'ordering': ['order'],
            },
        ),
        migrations.AlterField(
            model_name='attribute',
            name='unit',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Единица измерения'),
        ),
        migrations.RunPython(clear_unit, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='attribute',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.attributeunit', verbose_name='Единица измерения'),
        ),
    ]
