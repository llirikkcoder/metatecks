from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0009_subcategory_attr_ids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='unit',
            field=models.CharField(blank=True, max_length=15, verbose_name='Единица измерения'),
        ),
    ]
