from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0021_update_fields'),
        ('cml', '0007_add_foreign_keys'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchange',
            name='exchange_type',
            field=models.CharField(choices=[('export', 'export'), ('import', 'import')], max_length=50),
        ),
        migrations.CreateModel(
            name='ImportedBrand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=127)),
                ('name_clean', models.CharField(max_length=127)),
                ('good_name', models.BooleanField(default=False)),
                ('partial_name', models.BooleanField(default=False)),
                ('bad_name', models.BooleanField(default=False)),
                ('do_not_sync', models.BooleanField(default=True)),
                ('brand_obj', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cml_brands', to='catalog.brand')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
