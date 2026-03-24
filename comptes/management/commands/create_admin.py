from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from comptes.models import Profil


class Command(BaseCommand):
    help = 'Crée le superuser admin ESVE'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='esve@esve.com').exists():
            u = User.objects.create_superuser(
                username='esve@esve.com',
                email='esve@esve.com',
                password='esve2026'
            )
            Profil.objects.get_or_create(user=u, defaults={'role': 'ADMIN'})
            self.stdout.write('Admin cree avec succes!')
        else:
            self.stdout.write('Admin existe deja!')