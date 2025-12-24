from django.db import migrations
import galleryfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0018_add_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='productmodel',
            name='gallery',
            field=galleryfield.fields.GalleryField(blank=True, help_text='до 5 фото', null=True, target_model='galleryfield.BuiltInGalleryImage', verbose_name='Фотогалерея'),
        ),
        migrations.AddField(
            model_name='productmodel',
            name='gallery_3d',
            field=galleryfield.fields.GalleryField(blank=True, null=True, target_model='galleryfield.BuiltInGalleryImage', verbose_name='3D-галерея'),
        ),
    ]
