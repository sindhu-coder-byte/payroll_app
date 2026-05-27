import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a superuser from env vars if none exists'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('SUPERUSER_EMAIL', '')
        password = os.environ.get('SUPERUSER_PASSWORD')

        if not password:
            self.stdout.write('SUPERUSER_PASSWORD not set — skipping.')
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f'Superuser "{username}" already exists — skipping.')
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(f'Superuser "{username}" created successfully.')
