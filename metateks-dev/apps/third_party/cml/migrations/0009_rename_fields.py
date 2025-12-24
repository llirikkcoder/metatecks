from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cml', '0008_importedbrand'),
    ]

    operations = [
        migrations.RenameField(
            model_name='importedbrand',
            old_name='bad_name',
            new_name='is_name_bad',
        ),
        migrations.RenameField(
            model_name='importedbrand',
            old_name='good_name',
            new_name='is_name_good',
        ),
        migrations.RenameField(
            model_name='importedbrand',
            old_name='partial_name',
            new_name='is_name_partial',
        ),
        migrations.AlterField(
            model_name='exchange',
            name='exchange_type',
            field=models.CharField(choices=[('import', 'import'), ('export', 'export')], max_length=50),
        ),
        migrations.AlterField(
            model_name='importedgroup',
            name='parent',
            field=models.ForeignKey(blank=True, limit_choices_to={'parent': None}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='cml.importedgroup'),
        ),
    ]
