from django.db import migrations


def load_fixture(apps, schema_editor):
    pass
    # from django.core.management import call_command
    # call_command('loaddata', '20240901_categories_and_models.json')
    # call_command('loaddata', '20240902_brands.json')


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0011_update_attribute_fields'),
        ('watson', '0002_alter_searchentry_object_id'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=migrations.RunPython.noop),
    ]
