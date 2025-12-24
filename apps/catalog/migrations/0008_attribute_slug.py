from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_add_h1_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='slug',
            field=models.SlugField(default='x', help_text='уникальное поле; принимаются английские буквы, цифры и символ "_"\n            <br><br>примеры:<br>- weight<br>- teeth<br>- load_capacity', verbose_name='В URL'),
            preserve_default=False,
        ),
    ]
