from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_rename_a_couple_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderpaymentcashlessdata',
            name='account',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='Р/С'),
        ),
        migrations.AddField(
            model_name='orderpaymentcashlessdata',
            name='bank',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='Банк'),
        ),
        migrations.AddField(
            model_name='orderpaymentcashlessdata',
            name='bik',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='БИК'),
        ),
        migrations.AddField(
            model_name='orderpaymentcashlessdata',
            name='director',
            field=models.CharField(blank=True, max_length=63, null=True, verbose_name='Генеральный директор'),
        ),
        migrations.AddField(
            model_name='orderpaymentcashlessdata',
            name='jur_email',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='E-mail'),
        ),
        migrations.AddField(
            model_name='orderpaymentcashlessdata',
            name='jur_phone',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='Телефон'),
        ),
        migrations.AddField(
            model_name='orderpaymentcashlessdata',
            name='kpp',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='КПП'),
        ),
        migrations.AddField(
            model_name='orderpaymentcashlessdata',
            name='ogrn',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='ОГРН'),
        ),
        migrations.AddField(
            model_name='userpaymentcashlessdata',
            name='account',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='Р/С'),
        ),
        migrations.AddField(
            model_name='userpaymentcashlessdata',
            name='bank',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='Банк'),
        ),
        migrations.AddField(
            model_name='userpaymentcashlessdata',
            name='bik',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='БИК'),
        ),
        migrations.AddField(
            model_name='userpaymentcashlessdata',
            name='director',
            field=models.CharField(blank=True, max_length=63, null=True, verbose_name='Генеральный директор'),
        ),
        migrations.AddField(
            model_name='userpaymentcashlessdata',
            name='jur_email',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='E-mail'),
        ),
        migrations.AddField(
            model_name='userpaymentcashlessdata',
            name='jur_phone',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='Телефон'),
        ),
        migrations.AddField(
            model_name='userpaymentcashlessdata',
            name='kpp',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='КПП'),
        ),
        migrations.AddField(
            model_name='userpaymentcashlessdata',
            name='ogrn',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='ОГРН'),
        ),
        migrations.AlterField(
            model_name='orderpaymentcashlessdata',
            name='inn',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='ИНН организации'),
        ),
        migrations.AlterField(
            model_name='orderpaymentcashlessdata',
            name='jur_address',
            field=models.TextField(blank=True, null=True, verbose_name='Юридический адрес'),
        ),
        migrations.AlterField(
            model_name='orderpaymentcashlessdata',
            name='organization',
            field=models.CharField(blank=True, max_length=63, null=True, verbose_name='Название организации'),
        ),
        migrations.AlterField(
            model_name='userpaymentcashlessdata',
            name='inn',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='ИНН организации'),
        ),
        migrations.AlterField(
            model_name='userpaymentcashlessdata',
            name='jur_address',
            field=models.TextField(blank=True, null=True, verbose_name='Юридический адрес'),
        ),
        migrations.AlterField(
            model_name='userpaymentcashlessdata',
            name='organization',
            field=models.CharField(blank=True, max_length=63, null=True, verbose_name='Название организации'),
        ),
    ]
