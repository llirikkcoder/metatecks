from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0021_update_fields'),
        ('cml', '0009_rename_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='importedproduct',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='cml.importedbrand'),
        ),
        migrations.AddField(
            model_name='importedproduct',
            name='brand_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_products', to='catalog.brand'),
        ),
        migrations.AlterField(
            model_name='exchange',
            name='exchange_type',
            field=models.CharField(choices=[('export', 'export'), ('import', 'import')], max_length=50),
        ),
    ]
