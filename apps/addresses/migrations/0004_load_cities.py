from django.db import migrations


def load_fixture(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0003_city_en_fields'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=migrations.RunPython.noop),
    ]
