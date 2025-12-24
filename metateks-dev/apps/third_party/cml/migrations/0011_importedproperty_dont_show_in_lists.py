from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cml', '0010_importedproduct_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='importedproperty',
            name='dont_show_in_lists',
            field=models.BooleanField(default=False),
        ),
    ]
