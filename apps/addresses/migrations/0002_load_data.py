from django.db import migrations


def load_fixture(apps, schema_editor):
    from django.core.management import call_command
    # call_command('loaddata', '20240722_addresses.json')


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=migrations.RunPython.noop),
    ]
