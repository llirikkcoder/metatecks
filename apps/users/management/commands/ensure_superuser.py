from django.core.management.base import BaseCommand
from apps.users.models import User


class Command(BaseCommand):
    help = 'Ensure superuser exists for Railway deployment'

    def handle(self, *args, **options):
        email = 'admin@metateks.ru'
        password = 'MetaTeks2025Admin!'

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            user.set_password(password)
            user.is_admin = True  # is_staff - это property от is_admin
            user.is_superuser = True
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Superuser {email} updated'))
        else:
            user = User.objects.create_superuser(
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Superuser {email} created'))

        self.stdout.write(f'  email: {user.email}')
        self.stdout.write(f'  is_admin: {user.is_admin}')
        self.stdout.write(f'  is_staff (property): {user.is_staff}')
        self.stdout.write(f'  is_superuser: {user.is_superuser}')
        self.stdout.write(f'  is_active: {user.is_active}')
