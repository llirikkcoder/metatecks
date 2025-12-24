from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0004_homepage'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepagesalesmanager',
            name='name_dative',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='Имя (дательный падеж)'),
        ),
    ]
