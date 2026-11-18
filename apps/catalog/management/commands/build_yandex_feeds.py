from django.core.management.base import BaseCommand

from apps.catalog.views.feeds import FEEDS, get_feed_xml


class Command(BaseCommand):
    help = 'Пересобирает Яндекс YML-фиды в кэше (можно вызывать из cron); --out DIR сохраняет и в файлы.'

    def add_arguments(self, parser):
        parser.add_argument('--out', help='каталог для сохранения XML-файлов')

    def handle(self, *args, **options):
        out = options.get('out')
        for kind in FEEDS:
            data = get_feed_xml(kind, refresh=True)
            self.stdout.write(f'{kind}: {len(data)} bytes')
            if out:
                import os
                os.makedirs(out, exist_ok=True)
                with open(os.path.join(out, f'{kind}.xml'), 'wb') as f:
                    f.write(data)
