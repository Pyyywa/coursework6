from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email='manager@test.com',
            first_name='Manager',
            last_name='Manager',
            is_superuser=False,
            is_staff=True,
            is_active=True
        )

        user.set_password('user12345')
        user.save()
