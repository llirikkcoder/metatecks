from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cml', '0013_exchangeparsing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchange',
            name='exchange_type',
            field=models.CharField(choices=[('import', 'import'), ('export', 'export')], max_length=50),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='brand_name',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Наименование бренда'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Наименование'),
        ),
        migrations.AlterField(
            model_name='importedproduct',
            name='name_clean',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Наименование (чистое)'),
        ),
    ]
