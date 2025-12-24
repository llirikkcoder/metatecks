from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0022_update_attribute_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategory',
            name='attribute_in_filter',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_synced_with_1c': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='filter_sub_category', to='catalog.attribute', verbose_name='Характеристика в фильтре'),
        ),
    ]
