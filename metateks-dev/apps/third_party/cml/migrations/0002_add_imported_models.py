import dirtyfields.dirtyfields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cml', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportedGroup',
            fields=[
                ('is_new', models.BooleanField(default=False)),
                ('has_changed', models.BooleanField(default=False)),
                ('has_removed', models.BooleanField(default=False)),
                ('fields_changed', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=127, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=127)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='cml.importedgroup')),
            ],
            options={
                'ordering': ['updated_at'],
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ImportedProperty',
            fields=[
                ('is_new', models.BooleanField(default=False)),
                ('has_changed', models.BooleanField(default=False)),
                ('has_removed', models.BooleanField(default=False)),
                ('fields_changed', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=127, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=127)),
                ('value_type', models.CharField(max_length=63)),
            ],
            options={
                'ordering': ['updated_at'],
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.AlterModelOptions(
            name='exchange',
            options={'verbose_name': 'Exchange log entry', 'verbose_name_plural': 'Exchange logs'},
        ),
        migrations.AlterField(
            model_name='exchange',
            name='exchange_type',
            field=models.CharField(choices=[('import', 'import'), ('export', 'export')], max_length=50),
        ),
        migrations.AlterField(
            model_name='exchange',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.CreateModel(
            name='ImportedPropertyVariant',
            fields=[
                ('is_new', models.BooleanField(default=False)),
                ('has_changed', models.BooleanField(default=False)),
                ('has_removed', models.BooleanField(default=False)),
                ('fields_changed', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=127, primary_key=True, serialize=False)),
                ('value', models.CharField(max_length=127)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='cml.importedproperty')),
            ],
            options={
                'ordering': ['updated_at'],
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ImportedProduct',
            fields=[
                ('is_new', models.BooleanField(default=False)),
                ('has_changed', models.BooleanField(default=False)),
                ('has_removed', models.BooleanField(default=False)),
                ('fields_changed', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=127, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=127)),
                ('group_ids', models.JSONField(default=list)),
                ('bar_code', models.CharField(blank=True, max_length=15)),
                ('vendor_code', models.CharField(blank=True, max_length=15)),
                ('description', models.TextField(blank=True)),
                ('properties', models.JSONField(default=dict)),
                ('image_path', models.CharField(blank=True, max_length=511)),
                ('additional_fields', models.JSONField(default=dict)),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='cml.importedgroup')),
            ],
            options={
                'ordering': ['updated_at'],
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
    ]
