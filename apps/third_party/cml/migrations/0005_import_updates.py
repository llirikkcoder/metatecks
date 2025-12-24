from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cml', '0004_import_updates'),
    ]

    operations = [
        migrations.AddField(
            model_name='importedgroup',
            name='do_not_sync',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='importedproduct',
            name='do_not_sync',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='importedproperty',
            name='do_not_sync',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='importedproperty',
            name='unit_name',
            field=models.CharField(blank=True, default='', max_length=31),
        ),
        migrations.AddField(
            model_name='importedpropertyvariant',
            name='do_not_sync',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='importedstockbalance',
            name='do_not_sync',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='importedwarehouse',
            name='do_not_sync',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='exchange',
            name='exchange_type',
            field=models.CharField(choices=[('import', 'import'), ('export', 'export')], max_length=50),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='bar_code',
            field=models.CharField(blank=True, max_length=63),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='vendor_code',
            field=models.CharField(blank=True, max_length=63),
        ),
    ]
