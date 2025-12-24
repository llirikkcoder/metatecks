from django.db import models

from easy_thumbnails.fields import ThumbnailerImageField
from solo.models import SingletonModel
from tinymce.models import HTMLField

from apps.utils.thumbs import get_thumb_url


class Homepage(SingletonModel):
    # Шапка страницы
    page_title = models.CharField('Заголовок страницы', max_length=255, default='Производитель навесного оборудования для&nbsp;спецтехники')
    # О компании
    about_title = models.CharField('О компании: заголовок', max_length=255, default='О компании')
    about_photo = ThumbnailerImageField('О компании: фото с сотрудниками', blank=True, null=True, upload_to='homepage/about/')
    about_text = HTMLField('О компании: текст', blank=True, default='<p>Основное направление деятельности компании Метатэкс&nbsp;&mdash; производство навесного оборудования для&nbsp;строительной и&nbsp;коммунальной техники. В&nbsp;наших цехах производится более 100&nbsp;модификаций навесного оборудования для&nbsp;более чем 3000&nbsp;моделей специальной техники.</p>')
    # Наши преимущества
    advantages_title = models.CharField('Наши преимущества: заголовок', max_length=255, default='Наши преимущества')
    # Медиа
    news_title = models.CharField('Новости: заголовок', max_length=255, default='Новости')
    news_text = models.TextField('Новости: текст')
    articles_title = models.CharField('Статьи: заголовок', max_length=255, default='Статьи')
    articles_text = models.TextField('Статьи: текст')
    photo_title = models.CharField('Фото: заголовок', max_length=255, default='Фото')
    photo_text = models.TextField('Фото: текст')
    video_title = models.CharField('Видео: заголовок', max_length=255, default='Видео')
    video_text = models.TextField('Видео: текст')
    # Доставка
    delivery_title = models.TextField('Доставка: заголовок', default='Доставка по&nbsp;России со&nbsp;складов<br />Московской области')
    # Отдел продаж
    sales_title = models.CharField('Отдел продаж: заголовок', max_length=255, default='Отдел продаж')
    sales_text = models.TextField('Отдел продаж: текст', blank=True, null=True, default='Чтобы заказать товар, свяжитесь с отделом продаж')

    class Meta:
        verbose_name = 'Главная страница'

    def __str__(self):
        return 'Главная страница'

    @property
    def about_photo_url(self):
        return get_thumb_url(self.about_photo, 'homepage_team')


class HomepageFact(models.Model):
    base = models.ForeignKey(Homepage, models.CASCADE, related_name='facts')

    ICON_CHOICES = (
        ('storage', 'продукция в наличии'),
        ('productions', 'напрямую с завода'),
    )
    icon = models.CharField('Иконка', max_length=15, choices=ICON_CHOICES)
    text_large = models.CharField('Крупный текст (сверху)', max_length=31, blank=True)
    text = models.TextField('Текст', blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'факт'
        verbose_name_plural = 'факты'

    @property
    def full_text(self):
        text = ' '.join([x for x in [self.text_large, self.text] if x])
        return text.replace('&nbsp;', ' ')

    def __str__(self):
        return self.full_text

    @property
    def icon_url(self):
        return f'/static/images/ico/ico-{self.icon}.png'


class HomepageAdvantage(models.Model):
    base = models.ForeignKey(Homepage, models.CASCADE, related_name='advantages')

    ICON_CHOICES = (
        ('buro', 'конструкторское бюро'),
        ('testing', 'испытательная база'),
        ('production', 'собственное производство'),
        ('storage', 'продукция в наличии'),
        ('compatibility', 'совместимость с техникой'),
        ('delivery', 'доставка по России'),
    )
    icon = models.CharField('Иконка', max_length=15, choices=ICON_CHOICES)
    text = models.TextField('Текст', blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'преимущество'
        verbose_name_plural = 'преимущества'

    def __str__(self):
        return self.text

    @property
    def icon_url(self):
        return f'/static/images/ico/ico-{self.icon}-200.png'


class HomepageWarehouse(models.Model):
    base = models.ForeignKey(Homepage, models.CASCADE, related_name='warehouses')
    photo = ThumbnailerImageField('Фото', upload_to='homepage/warehouses/')
    name = models.CharField('Название', max_length=255)
    subtitle = models.TextField('Подзаголовок', blank=True)
    address = models.TextField('Адрес', blank=True)
    schedule = models.TextField('Режим работы', blank=True)
    phone = models.CharField('Телефон', blank=True, max_length=31)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'склад'
        verbose_name_plural = 'склады'

    def __str__(self):
        return self.name.replace('&nbsp;', ' ')

    @property
    def photo_url(self):
        return get_thumb_url(self.photo, 'homepage_warehouse')


class HomepageSalesPhone(models.Model):
    base = models.ForeignKey(Homepage, models.CASCADE, related_name='phones')
    phone = models.CharField('Номер телефона', max_length=31)
    is_free = models.BooleanField('Звонок по России бесплатный', default=False)
    order = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ['order']
        verbose_name = 'номер'
        verbose_name_plural = 'номера телефона'

    def __str__(self):
        return self.phone


class HomepageSalesManager(models.Model):
    base = models.ForeignKey(Homepage, models.CASCADE, related_name='managers')
    name = models.CharField('Имя', max_length=31)
    name_dative = models.CharField('Имя (дательный падеж)', null=True, blank=True, max_length=31)
    photo = ThumbnailerImageField('Фото', upload_to='homepage/managers/', null=True, blank=True)
    phone = models.CharField('Номер телефона', max_length=31)
    order = models.PositiveSmallIntegerField('Порядок', default=1)
    is_shown = models.BooleanField('Показывать на странице?', default=True)

    class Meta:
        ordering = ['-is_shown', 'order']
        verbose_name = 'менеджер'
        verbose_name_plural = 'менеджеры'

    def __str__(self):
        return self.name

    def get_name_dative(self):
        return self.name_dative or self.name

    @property
    def photo_url(self):
        return get_thumb_url(self.photo, 'homepage_manager')
