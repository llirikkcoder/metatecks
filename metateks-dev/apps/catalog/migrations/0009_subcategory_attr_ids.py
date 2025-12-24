from django.db import migrations, models


def set_attr_ids(apps, schema_editor):
    SubCategory = apps.get_model('catalog', 'SubCategory')
    for obj in SubCategory.objects.prefetch_related('attributes', 'attributes_in_filter'):
        obj.attr_ids = [attr.id for attr in obj.attributes.all()]
        obj.attr_filter_ids = [attr.id for attr in obj.attributes_in_filter.all()]
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_attribute_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategory',
            name='attr_filter_ids',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='attr_ids',
            field=models.JSONField(default=list),
        ),
        migrations.RunPython(set_attr_ids, reverse_code=migrations.RunPython.noop),
    ]
