from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cml', '0002_add_imported_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchange',
            name='exchange_type',
            field=models.CharField(choices=[('export', 'export'), ('import', 'import')], max_length=50),
        ),
    ]
