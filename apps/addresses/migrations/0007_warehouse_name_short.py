from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0006_city_contacts_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouse',
            name='name_short',
            field=models.CharField(blank=True, max_length=127, verbose_name='Краткое название'),
        ),
    ]
