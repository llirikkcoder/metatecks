from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('catalog', '0027_extra_products_rename'),
        ('addresses', '0002_load_data'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=127, verbose_name='Название')),
                ('logo', models.FileField(help_text='файл .svg', upload_to='delivery/', verbose_name='Логотип')),
                ('is_shown', models.BooleanField(default=True, verbose_name='Показывать на сайте?')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'транспортная компания',
                'verbose_name_plural': 'транспортные компании',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('status', models.CharField(blank=True, choices=[('created', 'Оформлен'), ('collecting', 'Комплектуется'), ('delivering', 'Доставляется'), ('completed', 'Выполнен'), ('canceled', 'Отменен')], max_length=15, null=True, verbose_name='Статус заказа')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Комментарий')),
                ('total_quantity', models.PositiveSmallIntegerField(default=0, verbose_name='Кол-во товаров')),
                ('has_discount', models.BooleanField(default=False, verbose_name='Есть скидка?')),
                ('total_cost', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Стоимость (₽)')),
                ('total_without_discount', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Стоимость без скидки (₽)')),
                ('delivery_method', models.CharField(choices=[('pickup', 'Самовывоз'), ('metateks', 'Транспортом Метатэкс'), ('company', 'Транспортной компанией')], max_length=15, verbose_name='Способ доставки')),
                ('delivery_company_name', models.CharField(blank=True, max_length=127, null=True, verbose_name='Транспортная компания')),
                ('payment_method', models.CharField(choices=[('online', 'Оплата онлайн'), ('non_cash', 'Безналичная оплата'), ('on_receipt', 'Оплата при получении')], max_length=15, verbose_name='Метод оплаты')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Оплачен?')),
                ('paid_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата оплаты')),
                ('is_canceled', models.BooleanField(default=False, verbose_name='Отменен?')),
                ('is_canceled_by_user', models.BooleanField(default=None, null=True, verbose_name='Отменен пользователем?')),
                ('canceled_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата отмены')),
                ('is_synced_with_b24', models.BooleanField(default=False, verbose_name='Синхронизован с Битрикс24')),
                ('delivery_company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='orders.deliverycompany', verbose_name='Транспортная компания')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'заказ',
                'verbose_name_plural': 'заказы',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserPaymentCashlessData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization', models.CharField(max_length=63, verbose_name='Название организации')),
                ('inn', models.CharField(max_length=31, verbose_name='ИНН организации')),
                ('jur_address', models.TextField(verbose_name='Юридический адрес')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment_cashless_data', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'пользователь: данные безналичной оплаты',
                'verbose_name_plural': 'пользователь: данные безналичной оплаты',
            },
        ),
        migrations.CreateModel(
            name='UserPaymentCardData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.CharField(max_length=31, verbose_name='Номер карты')),
                ('card_name', models.CharField(max_length=255, verbose_name='Имя на карте')),
                ('card_expire', models.CharField(max_length=7, verbose_name='Срок действия')),
                ('card_cvv', models.PositiveSmallIntegerField(verbose_name='CVV')),
                ('is_selected', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_cards', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'пользователь: данные карты',
                'verbose_name_plural': 'пользователь: данные карты',
                'ordering': ['-is_selected', 'id'],
            },
        ),
        migrations.CreateModel(
            name='UserDeliveryAddressData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(max_length=63, verbose_name='Область')),
                ('city', models.CharField(max_length=63, verbose_name='Город')),
                ('address', models.TextField(verbose_name='Адрес')),
                ('is_selected', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'пользователь: адрес доставки',
                'verbose_name_plural': 'пользователь: адреса доставки',
                'ordering': ['-is_selected', 'id'],
            },
        ),
        migrations.CreateModel(
            name='UserContactsData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=31, verbose_name='Имя')),
                ('patronymic_name', models.CharField(blank=True, max_length=31, null=True, verbose_name='Отчество')),
                ('last_name', models.CharField(max_length=31, verbose_name='Фамилия')),
                ('phone', models.CharField(max_length=31, verbose_name='Телефон')),
                ('addresses', models.ManyToManyField(blank=True, related_name='contacts_data', to='orders.userdeliveryaddressdata', verbose_name='Адрес')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts_data', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'пользователь: контактные данные',
                'verbose_name_plural': 'пользователь: контактные данные',
            },
        ),
        migrations.CreateModel(
            name='OrderPaymentCashlessData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization', models.CharField(max_length=63, verbose_name='Название организации')),
                ('inn', models.CharField(max_length=31, verbose_name='ИНН организации')),
                ('jur_address', models.TextField(verbose_name='Юридический адрес')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment_cashless_data', to='orders.order')),
            ],
            options={
                'verbose_name': 'заказ: данные безналичной оплаты',
                'verbose_name_plural': 'заказ: данные безналичной оплаты',
            },
        ),
        migrations.CreateModel(
            name='OrderPaymentCardData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.CharField(max_length=31, verbose_name='Номер карты')),
                ('card_name', models.CharField(max_length=255, verbose_name='Имя на карте')),
                ('card_expire', models.CharField(max_length=7, verbose_name='Срок действия')),
                ('card_cvv', models.PositiveSmallIntegerField(verbose_name='CVV')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment_card_data', to='orders.order')),
            ],
            options={
                'verbose_name': 'заказ: данные карты',
                'verbose_name_plural': 'заказ: данные карты',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type', models.CharField(choices=[('product', 'товар'), ('extra', 'доп.товар')], default='product', max_length=7, verbose_name='Тип позиции')),
                ('item_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Название товара')),
                ('quantity', models.PositiveSmallIntegerField(default=0, verbose_name='Кол-во')),
                ('has_discount', models.BooleanField(default=False, verbose_name='Есть скидка?')),
                ('discount_percent', models.PositiveSmallIntegerField(default=0, verbose_name='Скидка за шт. (%)')),
                ('discount_price', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Скидка за шт. (₽)')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Цена (₽)')),
                ('price_without_discount', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Цена без скидки (₽)')),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Стоимость (₽)')),
                ('cost_without_discount', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Стоимость без скидки (₽)')),
                ('base_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='extra_items', to='orders.orderitem', verbose_name='Основной товар')),
                ('extra_product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to='catalog.extraproduct', verbose_name='Доп.товар')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order', verbose_name='Заказ')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to='catalog.product', verbose_name='Товар')),
                ('warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to='addresses.warehouse', verbose_name='Склад')),
            ],
            options={
                'verbose_name': 'товар',
                'verbose_name_plural': 'товары в заказе',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='OrderDeliveryAddressData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(max_length=63, verbose_name='Область')),
                ('city', models.CharField(max_length=63, verbose_name='Город')),
                ('address', models.TextField(verbose_name='Адрес')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='address_data', to='orders.order')),
            ],
            options={
                'verbose_name': 'заказ: адрес доставки',
                'verbose_name_plural': 'заказ: адреса доставки',
            },
        ),
        migrations.CreateModel(
            name='OrderContactsData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=31, verbose_name='Имя')),
                ('patronymic_name', models.CharField(blank=True, max_length=31, null=True, verbose_name='Отчество')),
                ('last_name', models.CharField(max_length=31, verbose_name='Фамилия')),
                ('phone', models.CharField(max_length=31, verbose_name='Телефон')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='contacts_data', to='orders.order')),
            ],
            options={
                'verbose_name': 'заказ: контактные данные',
                'verbose_name_plural': 'заказ: контактные данные',
            },
        ),
    ]
