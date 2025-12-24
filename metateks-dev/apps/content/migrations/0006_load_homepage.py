from django.db import migrations


def load_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command('loaddata', '20241201_homepage.json')


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0005_homepagesalesmanager_name_dative'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=migrations.RunPython.noop),
    ]
