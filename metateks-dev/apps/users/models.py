from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, Group, Permission, PermissionsMixin
from django.db import models

from easy_thumbnails.fields import ThumbnailerImageField

from apps.orders.constants import DeliveryMethods, PaymentMethods
from apps.utils.model_mixins import DatesBaseModel
from apps.utils.thumbs import get_thumb_url


class UserManager(BaseUserManager):

    def create_user(self, email, password):

        if not email:
            raise ValueError('Email: обязательное поле')

        if not password:
            raise ValueError('Password: обязательное поле')

        user = self.model(
            email=UserManager.normalize_email(email),
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            password=password,
        )

        user.is_active = True
        user.is_admin = True
        user.is_superuser = True
        user.save()

        return user

    def get_by_natural_key(self, username):
        """
        Делаем логин регистронезависимым
        """
        return self.get(email__iexact=username)


class User(AbstractBaseUser, PermissionsMixin):
    # данные для входа
    email = models.EmailField('Email', unique=True)
    date_joined = models.DateTimeField('Дата регистрации', auto_now_add=True)
    is_active = models.BooleanField('Активен', default=True, help_text='имеет возможность войти на сайт')

    # контакты
    last_name = models.CharField('Фамилия', null=True, blank=True, max_length=31)
    first_name = models.CharField('Имя', null=True, blank=True, max_length=31)
    patronymic_name = models.CharField('Отчество', null=True, blank=True, max_length=31)
    phone = models.CharField('Телефон', blank=True, max_length=31)
    avatar = ThumbnailerImageField('Аватар', null=True, blank=True, upload_to='users/avatars/')

    # old
    contact_email = models.EmailField('Email для связи', blank=True)

    # доступы
    is_admin = models.BooleanField('Админ', default=False, help_text='имеет доступ к админ.панели')
    is_superuser = models.BooleanField(
        'Суперпользователь', default=False, help_text='имеет все права в админ.панели без явного их назначения'
    )
    groups = models.ManyToManyField(Group, verbose_name='Группы', blank=True, related_name='users')
    user_permissions = models.ManyToManyField(Permission, verbose_name='Доступы', blank=True, related_name='users')

    # данные заказа по умолчанию
    delivery_method = models.CharField('Способ доставки', choices=DeliveryMethods.choices, blank=True, null=True, max_length=15)
    delivery_company = models.ForeignKey(
        'orders.DeliveryCompany', models.SET_NULL,
        verbose_name='Транспортная компания',
        blank=True, null=True, related_name='users',
    )
    payment_method = models.CharField('Метод оплаты', choices=PaymentMethods.choices, blank=True, null=True, max_length=15)

    # интеграции
    is_synced_with_b24 = models.BooleanField('Синхронизирован с Битрикс24', default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ['id',]
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        name = self.get_name()
        email = self.email
        return (
            f'{name} ({email})' if name and email
            else name if name
            else email if email
            else f'#{self.id}'
        )

    def get_name(self, full=False):
        names = [self.first_name, self.last_name]
        if full is True and self.patronymic_name:
            names.insert(1, self.patronymic_name)
        names = [x for x in names if x]
        return ' '.join(names)

    def get_full_name(self):
        return self.get_name(full=True)

    @property
    def initials(self):
        name = self.get_name()
        return (
            ''.join(x[0] for x in name.split()) if name
            else self.email[0] if self.email
            else '?'
        )

    @property
    def header_avatar_url(self):
        return get_thumb_url(self.avatar, 'user_avatar_header')

    @property
    def account_avatar_url(self):
        return get_thumb_url(self.avatar, 'user_avatar_account')

    def get_account_avatar_url(self):
        return (
            self.account_avatar_url
            if self.avatar
            else '/images/account/avatar-default.jpg'
        )

    def get_contacts_data(self):
        return {
            'first_name': self.first_name,
            'patronymic_name': self.patronymic_name,
            'last_name': self.last_name,
            'phone': self.phone,
        }

    @property
    def is_staff(self):
        return self.is_admin

    def get_orders(self):
        return self.orders.filter(status__gt='')

    @property
    def payment_method_full_str(self):
        return {
            PaymentMethods.ONLINE: 'Онлайн оплата банковской&nbsp;картой',
            PaymentMethods.NON_CASH: 'Безналичная оплата для&nbsp;юридических&nbsp;лиц',
            PaymentMethods.ON_RECEIPT: 'Оплата при&nbsp;получении',
        }.get(self.payment_method, self.payment_method)

    def get_favorites(self):
        return self.favorites.filter(product__is_shown=True).select_related(
            'product', 'product__model', 'product__sub_category',
        )

    def get_contacts_data(self):
        return {
            'first_name': self.first_name or '',
            'patronymic_name': self.patronymic_name or '',
            'last_name': self.last_name or '',
            'phone': self.phone or '',
        }


class FavoriteProduct(DatesBaseModel):
    user = models.ForeignKey(
        User, models.CASCADE, verbose_name='Пользователь', related_name='favorites'
    )
    product = models.ForeignKey(
        'catalog.product', models.CASCADE, verbose_name='Товар', related_name='favorites'
    )

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-updated_at']
        verbose_name = 'избранный товар'
        verbose_name_plural = 'избранные товары'

    @classmethod
    def is_exist(cls, user, product_id):
        return cls.objects.filter(user=user, product_id=product_id).exists()

    @classmethod
    def add(cls, user, product_id):
        obj, _created = cls.objects.get_or_create(user=user, product_id=product_id)
        if _created is False:
            obj.save()

    @classmethod
    def remove(cls, user, product_id):
        obj = cls.objects.filter(user=user, product_id=product_id).first()
        if obj:
            obj.delete()
