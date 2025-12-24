from django.db import migrations


def load_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command('loaddata', '20241201_banners.json')


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0002_banner_design_and_order'),
        ('content', '0006_load_homepage'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=migrations.RunPython.noop),
    ]
