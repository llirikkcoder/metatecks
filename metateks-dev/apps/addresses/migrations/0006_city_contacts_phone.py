from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0005_city_change_en_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='city',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='city',
            name='region_en',
        ),
        migrations.AddField(
            model_name='city',
            name='contacts_phone',
            field=models.CharField(blank=True, max_length=31, verbose_name='Контактный номер'),
        ),
    ]
