from django.db import migrations, models
import django.db.models.deletion
import easy_thumbnails.fields
import tinymce.models


def create_models(apps, schema_editor):
    ProductModel = apps.get_model('catalog', 'ProductModel')
    Product = apps.get_model('catalog', 'Product')

    fields = [
        'name', 'category', 'sub_category', 'photo', 'price', 'description', 'tech_description',
        'attrs', 'is_shown', 'is_popular', 'id_1c', 'is_synced_with_1c',
        'bar_code', 'vendor_code', 'order',
    ]
    for p in Product.objects.all():
        d = {name: getattr(p, name) for name in fields}
        model = ProductModel.objects.create(**d)
        p.model = model; p.save()
        p.photos.update(model_id=model.id)
        p.videos.update(model_id=model.id)
        p.properties.update(model_id=model.id)


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0016_load_attributes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subcategory',
            name='photo',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='sub_categories/photos/', verbose_name='Обложка'),
        ),
        migrations.CreateModel(
            name='ProductModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('meta_title', models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta title (заголовок страницы)')),
                ('meta_description', models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta description (описание страницы)')),
                ('meta_keywords', models.CharField(blank=True, help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Meta keywords (ключевые слова через запятую)')),
                ('h1', models.TextField(blank=True, default='', help_text='Оставьте пустым, чтобы использовать название объекта', max_length=255, verbose_name='Заголовок H1')),
                ('seo_text', tinymce.models.HTMLField(blank=True, verbose_name='SEO-текст')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('photo', easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='models/photos/', verbose_name='Фото')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Цена, руб.')),
                ('description', tinymce.models.HTMLField(blank=True, verbose_name='Описание')),
                ('tech_description', models.FileField(blank=True, null=True, upload_to='models/tech/', verbose_name='Техническое описание')),
                ('attrs', models.JSONField(default=dict)),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать на сайте')),
                ('is_popular', models.BooleanField(default=False, verbose_name='Показывать в списке «Популярное»')),
                ('id_1c', models.UUIDField(blank=True, db_index=True, null=True, verbose_name='ID в 1C')),
                ('is_synced_with_1c', models.BooleanField(default=False, verbose_name='Синхронизовано с 1C')),
                ('bar_code', models.CharField(blank=True, max_length=15, verbose_name='Штрихкод')),
                ('vendor_code', models.CharField(blank=True, max_length=15, verbose_name='Артикул')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='models', to='catalog.category', verbose_name='Категория')),
                ('sub_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='models', to='catalog.subcategory', verbose_name='Подкатегория')),
            ],
            options={
                'verbose_name': 'модель',
                'verbose_name_plural': '3) Модели',
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='catalog.productmodel', verbose_name='Модель'),
        ),
        migrations.AddField(
            model_name='productphoto',
            name='model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='photos', to='catalog.productmodel', verbose_name='Модель'),
        ),
        migrations.AddField(
            model_name='productproperty',
            name='model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='properties', to='catalog.productmodel', verbose_name='Модель'),
        ),
        migrations.AddField(
            model_name='productvideo',
            name='model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='videos', to='catalog.productmodel', verbose_name='Модель'),
        ),
        migrations.RunPython(create_models, reverse_code=migrations.RunPython.noop),
    ]
