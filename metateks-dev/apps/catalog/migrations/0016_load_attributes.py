from django.db import migrations


def load_fixture(apps, schema_editor):
    from django.core.management import call_command
    # call_command('loaddata', '20241105_attributes.json')


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0015_attributeunit'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=migrations.RunPython.noop),
    ]
