from django.core.management.base import BaseCommand

from guess_chan.settings import ADMIN_LOGIN, ADMIN_PASSWORD, SETUP_LANGS
from project.models import User, Lang


class Command(BaseCommand):
    help = "Setup database with init data."

    def handle(self, *args, **options):
        if not Lang.objects.filter(alpha2__in=SETUP_LANGS.keys()).exists():
            langs = []
            for alpha2, name in SETUP_LANGS.items():
                langs.append(Lang(alpha2=alpha2, name=name))
            Lang.objects.bulk_create(langs)
            self.stdout.write('Langs settled up.')

        if not User.objects.filter(login=ADMIN_LOGIN).exists():
            User.objects.create_superuser(ADMIN_LOGIN, ADMIN_PASSWORD)
            self.stdout.write('Superuser created.')
