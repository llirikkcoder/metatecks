from django.db import migrations, models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')),
                ('is_active', models.BooleanField(default=True, help_text='имеет возможность войти на сайт', verbose_name='Активен')),
                ('first_name', models.CharField(blank=True, max_length=31, null=True, verbose_name='Имя')),
                ('partonymic_name', models.CharField(blank=True, max_length=31, null=True, verbose_name='Отчество')),
                ('last_name', models.CharField(blank=True, max_length=31, null=True, verbose_name='Фамилия')),
                ('avatar', easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='users/avatars/', verbose_name='Аватар')),
                ('phone', models.CharField(blank=True, max_length=31, verbose_name='Телефон')),
                ('contact_email', models.EmailField(blank=True, max_length=254, verbose_name='Email для связи')),
                ('is_admin', models.BooleanField(default=False, help_text='имеет доступ к админ.панели', verbose_name='Админ')),
                ('is_superuser', models.BooleanField(default=False, help_text='имеет все права в админ.панели без явного их назначения', verbose_name='Суперпользователь')),
                ('is_synced_with_b24', models.BooleanField(default=False, verbose_name='Синхронизирован с Битрикс24')),
                ('groups', models.ManyToManyField(blank=True, related_name='users', to='auth.group', verbose_name='Группы')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='users', to='auth.permission', verbose_name='Доступы')),
            ],
            options={
                'verbose_name': 'пользователь',
                'verbose_name_plural': 'пользователи',
                'ordering': ['id'],
            },
        ),
    ]
