from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_load_delivery_companies'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderpaymentcashlessdata',
            name='account',
            field=models.CharField(default='-', max_length=31, verbose_name='Р/С'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderpaymentcashlessdata',
            name='bank',
            field=models.CharField(default='-', max_length=31, verbose_name='Банк'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderpaymentcashlessdata',
            name='bik',
            field=models.CharField(default='-', max_length=31, verbose_name='БИК'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderpaymentcashlessdata',
            name='director',
            field=models.CharField(default='-', max_length=63, verbose_name='Генеральный директор'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderpaymentcashlessdata',
            name='inn',
            field=models.CharField(default='-', max_length=31, verbose_name='ИНН организации'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderpaymentcashlessdata',
            name='jur_address',
            field=models.TextField(default='-', verbose_name='Юридический адрес'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderpaymentcashlessdata',
            name='jur_email',
            field=models.CharField(default='-', max_length=31, verbose_name='E-mail'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderpaymentcashlessdata',
            name='jur_phone',
            field=models.CharField(default='-', max_length=31, verbose_name='Телефон'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderpaymentcashlessdata',
            name='kpp',
            field=models.CharField(default='-', max_length=31, verbose_name='КПП'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderpaymentcashlessdata',
            name='ogrn',
            field=models.CharField(default='-', max_length=31, verbose_name='ОГРН'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderpaymentcashlessdata',
            name='organization',
            field=models.CharField(default='-', max_length=63, verbose_name='Название организации'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userpaymentcashlessdata',
            name='account',
            field=models.CharField(default='-', max_length=31, verbose_name='Р/С'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userpaymentcashlessdata',
            name='bank',
            field=models.CharField(default='-', max_length=31, verbose_name='Банк'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userpaymentcashlessdata',
            name='bik',
            field=models.CharField(default='-', max_length=31, verbose_name='БИК'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userpaymentcashlessdata',
            name='director',
            field=models.CharField(default='-', max_length=63, verbose_name='Генеральный директор'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userpaymentcashlessdata',
            name='inn',
            field=models.CharField(default='-', max_length=31, verbose_name='ИНН организации'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userpaymentcashlessdata',
            name='jur_address',
            field=models.TextField(default='-', verbose_name='Юридический адрес'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userpaymentcashlessdata',
            name='jur_email',
            field=models.CharField(default='-', max_length=31, verbose_name='E-mail'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userpaymentcashlessdata',
            name='jur_phone',
            field=models.CharField(default='-', max_length=31, verbose_name='Телефон'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userpaymentcashlessdata',
            name='kpp',
            field=models.CharField(default='-', max_length=31, verbose_name='КПП'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userpaymentcashlessdata',
            name='ogrn',
            field=models.CharField(default='-', max_length=31, verbose_name='ОГРН'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userpaymentcashlessdata',
            name='organization',
            field=models.CharField(default='-', max_length=63, verbose_name='Название организации'),
            preserve_default=False,
        ),
    ]
