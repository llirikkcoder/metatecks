from django.db import models
from django.conf import settings
from django.utils.safestring import mark_safe

from dirtyfields import DirtyFieldsMixin
import regex
from treenode.models import TreeNodeModel
from treenode.signals import no_signals


class Exchange(models.Model):

    class Meta:
        verbose_name = 'Exchange log entry'
        verbose_name_plural = 'Exchange logs'

    exchange_type_choices = (
        ('import', 'import'),
        ('export', 'export')
    )

    exchange_type = models.CharField(max_length=50, choices=exchange_type_choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    filename = models.CharField(max_length=200)

    @classmethod
    def log(cls, exchange_type, user, filename=''):
        ex_log = Exchange(exchange_type=exchange_type, user=user, filename=filename)
        ex_log.save()
        return ex_log


class ExchangeParsing(models.Model):
    import_xml_obj = models.OneToOneField(
        Exchange, models.SET_NULL,
        blank=True, null=True,
        related_name='import_xml_parsing',
        verbose_name='Catalog XML object',
    )
    offers_xml_obj = models.OneToOneField(
        Exchange, models.SET_NULL,
        blank=True, null=True,
        related_name='offers_xml_parsing',
        verbose_name='Offers XML object',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    import_filename = models.CharField('Catalog filename', max_length=255)
    import_file_path = models.CharField('Catalog file path', max_length=255)
    import_was_imported = models.BooleanField('Catalog was imported', default=False)
    import_imported_at = models.DateTimeField('Catalog imported at', null=True, blank=True)
    import_error_message = models.TextField('Catalog error message', blank=True)

    offers_filename = models.CharField(max_length=255)
    offers_file_path = models.CharField(max_length=255)
    offers_was_imported = models.BooleanField(default=False)
    offers_imported_at = models.DateTimeField(null=True, blank=True)
    offers_error_message = models.TextField(blank=True)

    is_full = models.BooleanField(default=False)

    was_synced = models.BooleanField(default=False)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_error_message = models.TextField(blank=True)

    stats_before = models.JSONField(default=dict)
    stats_after = models.JSONField(default=dict)

    class Meta(TreeNodeModel.Meta):
        ordering = ['-created_at']
        verbose_name = 'объекты парсинга'
        verbose_name_plural = 'парсинг'

    @classmethod
    def log(cls, exchange_obj, filename, file_path):
        mode = (
            'import' if 'import' in filename
            else 'offers' if 'offers' in filename
            else None
        )
        if not mode:
            return

        kw = {
            f'{mode}_xml_obj': exchange_obj,
            f'{mode}_filename': filename,
            f'{mode}_file_path': file_path,
        }
        obj = None
        if mode == 'import':
            obj = cls.objects.create(**kw)
        elif mode == 'offers':
            obj = cls.objects.first()
            if obj and not obj.offers_xml_obj:
                for k, v in kw.items():
                    setattr(obj, k, v)
                    obj.save()
        return obj


class ImportedItemMixin(DirtyFieldsMixin, models.Model):
    is_new = models.BooleanField('Новый?', default=False)
    has_changed = models.BooleanField('Изменялся?', default=False)
    has_removed = models.BooleanField('Удален?', default=False)

    fields_changed = models.JSONField('Измененные поля', default=list)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    do_not_sync = models.BooleanField(mark_safe('Не&nbsp;синхронизировать'), default=False)

    class Meta:
        abstract = True
        ordering = ['updated_at']

    def save(self, check_changes=True, *args, **kwargs):
        if check_changes is True:
            if self.is_new is False:
                if self.is_dirty(check_relationship=True):
                    self.has_changed = True
                    _fields = self.get_dirty_fields(check_relationship=True).keys()
                    self.fields_changed = list(_fields)
                else:
                    self.has_changed = False
                    self.fields_changed = []
        return super().save(*args, **kwargs)

    @classmethod
    def save_item(cls, query, **kwargs):
        item = cls.objects.filter(**query).first()
        _created = False
        if item:
            item.is_new = False
            item.has_removed = False
        else:
            item = cls(**query)
            item.is_new = True
            _created = True
        for k, v in kwargs.items():
            setattr(item, k, v)
        item.save()
        return item, _created


class ImportedGroup(ImportedItemMixin, TreeNodeModel):
    treenode_display_field = 'name'
    id = models.CharField('ID', max_length=127, primary_key=True)
    name = models.CharField('Наименование', max_length=127)
    name_clean = models.CharField('Наименование (чистое)', max_length=127, blank=True, default='')
    parent = models.ForeignKey('self', verbose_name='Основная группа', on_delete=models.CASCADE, null=True, blank=True, related_name='children', limit_choices_to={'parent': None})

    category_obj = models.ForeignKey('catalog.Category', verbose_name='Категория (сайт)', on_delete=models.SET_NULL, null=True, blank=True, related_name='cml_groups')
    subcategory_obj = models.ForeignKey('catalog.Subcategory', verbose_name='Подкатегория (сайт)', on_delete=models.SET_NULL, null=True, blank=True, related_name='cml_groups')

    FIELDS_TO_CHECK = ['name', 'parent']

    class Meta(TreeNodeModel.Meta):
        ordering = [
            '-tn_priority',
            'name',
        ]
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self):
        return f'{self.name} ({self.id})'


ATTR_TYPES = {
    'Число': 'number',
    'Строка': 'string',
    'Справочник': 'string',
}


class ImportedProperty(ImportedItemMixin, models.Model):
    id = models.CharField('ID', max_length=127, primary_key=True)
    name = models.CharField('Наименование', max_length=127)
    name_clean = models.CharField('Наименование (чистое)', max_length=127, blank=True, default='')
    unit_name = models.CharField('Единица измерения', max_length=31, blank=True, default='')
    value_type = models.CharField('Тип значения', max_length=63)
    dont_show_in_lists = models.BooleanField('Не показывать в списке товаров', default=False)
    attribute_obj = models.ForeignKey('catalog.Attribute', verbose_name='Характеристика (сайт)', on_delete=models.SET_NULL, null=True, blank=True, related_name='cml_properties')
    FIELDS_TO_CHECK = ['name', 'value_type']

    class Meta:
        verbose_name = 'свойство'
        verbose_name_plural = 'свойства товаров'

    def __str__(self):
        return f'{self.name}: {self.value_type} ({self.id})'

    @property
    def attr_type(self):
        return ATTR_TYPES.get(self.value_type, 'string')


class ImportedPropertyVariant(ImportedItemMixin, models.Model):
    id = models.CharField('ID', max_length=127, primary_key=True)
    value = models.CharField('Значение', max_length=127)
    property = models.ForeignKey(ImportedProperty, verbose_name='Свойство (сайт)', on_delete=models.CASCADE, related_name='variants')
    option_obj = models.ForeignKey('catalog.AttributeOption', verbose_name='Вариант (сайт)', on_delete=models.SET_NULL, null=True, blank=True, related_name='cml_variants')
    FIELDS_TO_CHECK = ['value', 'property']

    class Meta:
        verbose_name = 'вариант'
        verbose_name_plural = 'свойства: варианты'

    def __str__(self):
        return f'{self.value} ({self.id})'


class ImportedBrand(models.Model):
    name = models.CharField('Наименование', max_length=127)
    name_clean = models.CharField('Наименование (чистое)', max_length=127)
    is_name_good = models.BooleanField('Хорошее', default=False)
    is_name_partial = models.BooleanField('Частичное', default=False)
    is_name_bad = models.BooleanField('Плохое', default=False)
    do_not_sync = models.BooleanField('Не синхронизировать', default=True)
    brand_obj = models.ForeignKey('catalog.Brand', verbose_name='Бренд (сайт)', on_delete=models.SET_NULL, null=True, blank=True, related_name='cml_brands')
    FIELDS_TO_CHECK = []

    def __str__(self):
        return self.name_clean

    class Meta:
        ordering = ['name']
        verbose_name = 'бренд'
        verbose_name_plural = 'бренды'


class ImportedProduct(ImportedItemMixin, models.Model):
    """
    properties - свойства
    additional_fields - реквизиты
    """
    id = models.CharField('ID', max_length=127, primary_key=True)
    model_id = models.CharField('ID модели', max_length=127, null=True, blank=True, db_index=True)
    product_id = models.CharField('ID товара', max_length=127, null=True, blank=True, db_index=True)

    name = models.CharField('Наименование', max_length=255)
    name_clean = models.CharField('Наименование (чистое)', max_length=255, blank=True, default='')

    brand_name = models.CharField('Наименование бренда', max_length=255, blank=True, default='')
    brand = models.ForeignKey(ImportedBrand, verbose_name='Бренд (1С)', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    brand_obj = models.ForeignKey('catalog.Brand', verbose_name='Бренд (сайт)', on_delete=models.SET_NULL, null=True, blank=True, related_name='cml_products')

    group = models.ForeignKey(ImportedGroup, verbose_name='Группа (1C)', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    group_ids = models.JSONField('ID групп', default=list)

    bar_code = models.CharField('Штрихкод', max_length=63, blank=True)
    vendor_code = models.CharField('Артикул', max_length=63, blank=True)
    description = models.TextField('Описание', blank=True)

    price = models.DecimalField('Цена', max_digits=9, decimal_places=2, default=0)

    properties = models.JSONField('Свойства', default=dict)  # свойства
    image_path = models.CharField('Изображение', max_length=511, blank=True)
    additional_fields = models.JSONField('Реквизиты', default=dict) # реквизиты

    model_obj = models.ForeignKey('catalog.ProductModel', verbose_name='Модель (сайт)', on_delete=models.SET_NULL, null=True, blank=True, related_name='cml_products')
    product_obj = models.ForeignKey('catalog.Product', verbose_name='Товар (сайт)', on_delete=models.SET_NULL, null=True, blank=True, related_name='cml_products')

    FIELDS_TO_CHECK = ['name', 'group', 'description', 'properties', 'image_path', 'additional_fields',]

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return f'{self.name} ({self.id})'

    @classmethod
    def for_sync(cls):
        return cls.objects.select_related('group').filter(
            group__do_not_sync=False, group__subcategory_obj_id__gt=0, has_removed=False
        )

    @property
    def model_name(self):
        return self.additional_fields.get('Полное наименование', self.name)

    @property
    def model_vendor_code(self):
        return self.additional_fields.get('Код', self.vendor_code)

    @staticmethod
    def get_brand_name(name):
        brand_name = ''
        r = regex.findall(r'(\((?:[^)(]++|(?1))*\))\h?\K', name)
        if r:
            brand_name = r[-1]
            brand_name = brand_name.replace('(', '', 1).replace(')', '').strip().split()[0]
        return brand_name


class ImportedWarehouse(ImportedItemMixin, models.Model):
    id = models.CharField('ID', max_length=127, primary_key=True)
    name = models.CharField('Наименование', max_length=127)
    address = models.CharField('Адрес', max_length=127, blank=True, null=True)
    phone = models.CharField('Телефон', max_length=127, blank=True, null=True)
    warehouse_obj = models.ForeignKey('addresses.Warehouse', verbose_name='Склад (сайт)', on_delete=models.SET_NULL, null=True, blank=True, related_name='cml_warehouses')
    FIELDS_TO_CHECK = ['name']

    class Meta:
        verbose_name = 'склад'
        verbose_name_plural = 'склады'

    def __str__(self):
        return f'{self.name} ({self.id})'


class ImportedStockBalance(ImportedItemMixin, models.Model):
    warehouse_id = models.CharField('ID склада', max_length=127, db_index=True)
    product_id = models.CharField('ID товара', max_length=127, db_index=True)
    number = models.PositiveSmallIntegerField('Кол-во на складе', default=0)
    balance_obj = models.ForeignKey('catalog.ProductStockBalance', verbose_name='Остаток (сайт)', on_delete=models.SET_NULL, null=True, blank=True, related_name='cml_balance')
    FIELDS_TO_CHECK = []

    def __str__(self):
        return f'{self.product_id} / {self.warehouse_id}: {self.number} на складе'

    class Meta:
        unique_together = ('warehouse_id', 'product_id')
        ordering = ['updated_at']
        verbose_name = 'количество на складе'
        verbose_name_plural = 'товары: количество на складе'


def print_stats():
    for model in [
        ImportedGroup, ImportedProperty, ImportedPropertyVariant,
        ImportedProduct, ImportedWarehouse, ImportedStockBalance,
    ]:
        print(model.__name__, model.objects.count())


# def init_import_groups():
#     for model in [ImportedGroup]:
#         model.objects.all().update(has_removed=True)
#     # print('--- init groups ---')


def after_import_groups():
    # апдейтим порядок подгрупп
    with no_signals():
        for g in ImportedGroup.objects.filter(parent__isnull=True):
            c = g.children.count()
            for i, sg in enumerate(g.children.all().order_by('name')):
                sg.tn_priority = c
                sg.save()
                c -= 1
    ImportedGroup.update_tree()


# def init_import_properties():
#     for model in [ImportedProperty, ImportedPropertyVariant]:
#         model.objects.all().update(has_removed=True)
#     # print('--- init properties ---')


def init_import_catalog():
    for model in [ImportedProduct]:
        model.objects.all().update(has_removed=True)
    # print('--- init catalog ---')


# def init_import_offers():
#     for model in [ImportedWarehouse, ImportedStockBalance]:
#         model.objects.all().update(has_removed=True)
#     # print('--- init offers ---')


# def init_import_stock_balances():
#     for model in [ImportedStockBalance]:
#         model.objects.all().update(has_removed=True)
#     # print('--- init stock balances ---')
