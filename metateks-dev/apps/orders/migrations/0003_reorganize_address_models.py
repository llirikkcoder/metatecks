from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_orderitem_item_subtitle'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdeliveryaddressdata',
            name='first_name',
            field=models.CharField(default='-', max_length=31, verbose_name='Имя'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userdeliveryaddressdata',
            name='last_name',
            field=models.CharField(default='-', max_length=31, verbose_name='Фамилия'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userdeliveryaddressdata',
            name='patronymic_name',
            field=models.CharField(blank=True, null=True, verbose_name='Отчество'),
        ),
        migrations.AddField(
            model_name='userdeliveryaddressdata',
            name='phone',
            field=models.CharField(default='-', max_length=31, verbose_name='Телефон'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='UserContactsData',
        ),
    ]
