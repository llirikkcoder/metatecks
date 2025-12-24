from django.db import migrations


def load_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command('loaddata', '20250820_cities.json')


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0008_city_name_loct_city_region_name_and_more'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=migrations.RunPython.noop),
    ]
