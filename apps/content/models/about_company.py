from django.db import models

from easy_thumbnails.fields import ThumbnailerImageField
from galleryfield.fields import GalleryField
from solo.models import SingletonModel
from tinymce.models import HTMLField

from apps.utils.thumbs import get_thumb_url


class AboutCompany(SingletonModel):
    # Шапка страницы
    about_title = models.CharField('Заголовок страницы', max_length=255, default='О компании')
    about_text = HTMLField('Текст в начале страницы', blank=True, default='<p>Метатэкс — лидер по производству навесного оборудования для спецтехники в России. Мы предоставляем проверенные и надежные решения, которые расширяют возможности вашей техники и повышают производительность.</p>')
    # Блок с фактами
    # Блоки «Наши преимущества»
    # Блок «Люди»
    people_title = models.CharField('Заголовок блока', max_length=255, default='Но главное в Метатэксе — это люди')
    people_photo = ThumbnailerImageField('Фото с сотрудниками', blank=True, null=True, upload_to='about/people/')
    # Блок «Звонок в офис»
    phone_text = models.CharField('Текст на кнопке', max_length=63, default='Звонок в офис')
    phone_number = models.CharField('Номер телефона', max_length=31, default='+7 499 964-41-12')

    class Meta:
        verbose_name = 'Страница «О компании»'

    def __str__(self):
        return 'Страница «О компании»'

    @property
    def people_photo_url(self):
        return get_thumb_url(self.people_photo, 'about_people_photo')


class AboutFact(models.Model):
    PLACE_CHOICES = (
        (1, 'сверху'),
        (2, 'снизу'),
    )
    base = models.ForeignKey(AboutCompany, models.CASCADE, related_name='facts')
    text1 = models.CharField('Текст №1', max_length=31, blank=True)
    number = models.CharField('Число', max_length=15, blank=True)
    text2 = models.CharField('Текст №2', max_length=31, blank=True)
    place = models.PositiveSmallIntegerField('Расположение', choices=PLACE_CHOICES, default=1)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['place', 'order']
        verbose_name = 'факт'
        verbose_name_plural = 'факты'

    def __str__(self):
        return self.get_text()

    def get_text(self):
        pieces = [self.text1, self.number, self.text2]
        return ' '.join(x for x in pieces if x) or f'#{self.id}'


class AboutAdvantage(models.Model):
    base = models.ForeignKey(AboutCompany, models.CASCADE, related_name='advantages')

    ICON_CHOICES = (
        ('buro', 'конструкторское бюро'),
        ('testing', 'испытательная база'),
        ('production', 'собственное производство'),
        ('storage', 'продукция в наличии'),
        ('compatibility', 'совместимость с техникой'),
        ('delivery', 'доставка по России'),
    )
    icon = models.CharField('Иконка в списке', max_length=15, choices=ICON_CHOICES)
    list_title = models.TextField('Заголовок в списке')

    BLOCK_TYPE_CHOICES = (
        ('regular', 'обычный'),
        ('warehouses', 'склады'),
        ('brands', 'бренды'),
        ('delivery', 'доставка'),
    )
    block_type = models.CharField('Тип блока', max_length=15, choices=BLOCK_TYPE_CHOICES, default='regular')
    title = models.CharField('Заголовок блока', max_length=255)
    photo = ThumbnailerImageField('Фото', null=True, blank=True, upload_to='about/advantages/')
    video = models.TextField('Видео (код для вставки на сайт)', null=True, blank=True)
    gallery = GalleryField(verbose_name='Галерея', null=True, blank=True)
    text = HTMLField('Текст', blank=True)

    button_text = models.CharField('Кнопка: текст', max_length=63, blank=True)
    button_link = models.CharField('Кнопка: ссылка', max_length=255, blank=True)

    order = models.PositiveSmallIntegerField('Порядок', default=1)
    is_shown = models.BooleanField('Показывать на странице?', default=True)

    class Meta:
        ordering = ['-is_shown', 'order']
        verbose_name = 'преимущество'
        verbose_name_plural = 'преимущества'

    def __str__(self):
        return self.list_title.replace('\r\n', ' ')

    def get_icon_url(self):
        return f'/images/ico/ico-{self.icon}-200.png'

    @property
    def has_video(self):
        return self.video and not self.video.startswith('http')

    @property
    def has_media(self):
        return self.video or self.gallery

    @property
    def has_small_columns(self):
        return self.block_type == 'regular' and not self.has_media

    @property
    def has_button(self):
        return self.button_text and self.button_link

    @property
    def photo_url(self):
        return get_thumb_url(self.photo, 'about_advantage_photo')

    # @property
    # def people_photo_url(self):
    #     return get_thumb_url(self.people_photo, 'about_people_photo')

    # @property
    # def people_photo_url(self):
    #     return get_thumb_url(self.people_photo, 'about_people_photo')


class AboutWarehouse(models.Model):
    base = models.ForeignKey(AboutCompany, models.CASCADE, related_name='warehouses')
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Краткое описание', blank=True)
    address = models.TextField('Адрес', blank=True)
    schedule = models.TextField('Режим работы', blank=True)
    phone = models.CharField('Телефон', blank=True, max_length=31)
    order = models.PositiveSmallIntegerField('Порядок', default=1)
    is_shown = models.BooleanField('Показывать на странице?', default=True)

    class Meta:
        ordering = ['-is_shown', 'order']
        verbose_name = 'склад'
        verbose_name_plural = 'склады'

    def __str__(self):
        return self.name.replace('&nbsp;', ' ')


class AboutTransportCompany(models.Model):
    base = models.ForeignKey(AboutCompany, models.CASCADE, related_name='transport_companies')
    name = models.CharField('Название', max_length=255)
    logo = models.FileField('Логотип', upload_to='about/delivery/', help_text='файл .svg')
    order = models.PositiveSmallIntegerField('Порядок', default=1)
    is_shown = models.BooleanField('Показывать на странице?', default=True)

    class Meta:
        ordering = ['-is_shown', 'order']
        verbose_name = 'транспортная компания'
        verbose_name_plural = 'транспортные компании'

    def __str__(self):
        return self.name
