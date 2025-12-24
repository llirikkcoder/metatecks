from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0020_update_video_fields'),
        ('addresses', '0002_load_data'),
        ('cml', '0006_importedgoup_tree'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='importedgroup',
            options={'ordering': ['-tn_priority', 'name']},
        ),
        migrations.AddField(
            model_name='importedstockbalance',
            name='balance_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_balance', to='catalog.productstockbalance'),
        ),
        migrations.AddField(
            model_name='importedwarehouse',
            name='warehouse_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_warehouses', to='addresses.warehouse'),
        ),
    ]
