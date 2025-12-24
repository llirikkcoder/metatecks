from django.db import models

from solo.models import SingletonModel


class FooterData(SingletonModel):
    # 1-й столбец
    first_column_title = models.CharField(
        '1-й столбец: заголовок', max_length=255, blank=True, default='Компания'
    )
    # 2-й столбец
    second_column_title = models.CharField(
        '2-й столбец: заголовок', max_length=255, blank=True, default='Продукция'
    )
    # 3-й столбец
    third_column_title = models.CharField(
        '3-й столбец: заголовок', max_length=255, blank=True, default='Медиа'
    )
    # 4-й столбец
    fourth_column_title = models.CharField(
        '4-й столбец: заголовок', max_length=255, blank=True, default='Личный кабинет'
    )
    # Ссылки на соц.сети
    # Контакты
    contacts_phone = models.CharField('Номер телефона', max_length=31, blank=True, default='+7 800 222-54-32')
    contacts_email = models.CharField('Email', max_length=31, blank=True, default='metall@spmet.ru')

    class Meta:
        verbose_name = 'Данные в футере'

    def __str__(self):
        return 'Данные в футере'

    def get_columns(self):
        return [
            {
                'title': self.first_column_title,
                'links': self.first_column_links.filter(is_shown=True),
            },
            {
                'title': self.second_column_title,
                'links': self.second_column_links.filter(is_shown=True),
            },
            {
                'title': self.third_column_title,
                'links': self.third_column_links.filter(is_shown=True),
            },
            {
                'title': self.fourth_column_title,
                'links': self.fourth_column_links.filter(is_shown=True),
            },
        ]

    def get_social_links(self):
        return self.social_links.filter(is_shown=True)


class FooterFirstColumnLink(models.Model):
    base = models.ForeignKey(FooterData, models.CASCADE, related_name='first_column_links')
    title = models.CharField('Заголовок', max_length=255)
    link = models.CharField('Ссылка', max_length=127)
    order = models.PositiveSmallIntegerField('Порядок', default=1)
    is_shown = models.BooleanField('Показывать?', default=True)

    class Meta:
        ordering = ['-is_shown', 'order']
        verbose_name = 'ссылка'
        verbose_name_plural = '1-й столбец: ссылки'

    def __str__(self):
        return self.title


class FooterSecondColumnLink(models.Model):
    base = models.ForeignKey(FooterData, models.CASCADE, related_name='second_column_links')
    title = models.CharField('Заголовок', max_length=255)
    link = models.CharField('Ссылка', max_length=127)
    order = models.PositiveSmallIntegerField('Порядок', default=1)
    is_shown = models.BooleanField('Показывать?', default=True)

    class Meta:
        ordering = ['-is_shown', 'order']
        verbose_name = 'ссылка'
        verbose_name_plural = '2-й столбец: ссылки'

    def __str__(self):
        return self.title


class FooterThirdColumnLink(models.Model):
    base = models.ForeignKey(FooterData, models.CASCADE, related_name='third_column_links')
    title = models.CharField('Заголовок', max_length=255)
    link = models.CharField('Ссылка', max_length=127)
    order = models.PositiveSmallIntegerField('Порядок', default=1)
    is_shown = models.BooleanField('Показывать?', default=True)

    class Meta:
        ordering = ['-is_shown', 'order']
        verbose_name = 'ссылка'
        verbose_name_plural = '3-й столбец: ссылки'

    def __str__(self):
        return self.title


class FooterFourthColumnLink(models.Model):
    base = models.ForeignKey(FooterData, models.CASCADE, related_name='fourth_column_links')
    title = models.CharField('Заголовок', max_length=255)
    link = models.CharField('Ссылка', max_length=127)
    order = models.PositiveSmallIntegerField('Порядок', default=1)
    is_shown = models.BooleanField('Показывать?', default=True)

    class Meta:
        ordering = ['-is_shown', 'order']
        verbose_name = 'ссылка'
        verbose_name_plural = '4-й столбец: ссылки'

    def __str__(self):
        return self.title


class FooterSocialLink(models.Model):
    ICON_CHOICES = (
        ('vk', 'vk'),
        ('telegram', 'telegram'),
        ('youtube', 'youtube'),
    )
    base = models.ForeignKey(FooterData, models.CASCADE, related_name='social_links')
    icon = models.CharField('Иконка', max_length=15, choices=ICON_CHOICES)
    link = models.URLField('Ссылка', max_length=255)
    order = models.PositiveSmallIntegerField('Порядок', default=1)
    is_shown = models.BooleanField('Показывать?', default=True)

    class Meta:
        ordering = ['-is_shown', 'order']
        verbose_name = 'ссылка'
        verbose_name_plural = 'ссылки на соц.сети'

    def __str__(self):
        return f'#{self.id}: {self.icon}'

    def get_link_title(self):
        return {
            'vk': 'На страницу Вконтакте',
            'telegram': 'Зайти на канал в Телеграме',
            'youtube': 'Наш канал на YouTube',
        }.get(self.icon, self.get_icon_display())
