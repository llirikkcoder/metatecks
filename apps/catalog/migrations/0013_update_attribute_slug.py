from django.db import migrations, models


def set_slug(apps, schema_editor):
    Attribute = apps.get_model('catalog', 'Attribute')
    for obj in Attribute.objects.all():
        obj.slug = f'attr{obj.id}'
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0012_load_data'),
    ]

    operations = [
        migrations.RunPython(set_slug, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='attribute',
            name='slug',
            field=models.SlugField(help_text='уникальное поле; принимаются английские буквы, цифры и символ "_"\n            <br><br>примеры:<br>- weight<br>- teeth<br>- load_capacity', unique=True, blank=True, null=True, verbose_name='В URL'),
        ),
    ]
