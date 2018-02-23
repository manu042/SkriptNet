# Writing custom django-admin commands
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/

# Django Packages
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

# Third party packages
import logging

# My Packages
from skripten_shop.models import Article, Order, ShopSettings, AritcleInStock

logger = logging.getLogger('skripten_shop.default')


# TODO: logging erweitern
class Command(BaseCommand):
    """
    - Funktion über einen täglichen Cronjob ausführen

    Wenn der Skriptenshop geöffnet ist, werden Benachrichtigungen an Bestellung mit dem Status "im Lager" versendet
    """

    help = 'Versenden von Benachrichtigungen für reservierte Skripte'

    def handle(self, *args, **options):

        shop_settings = ShopSettings.objects.get(pk=1)

        # Falls Skriptenshop geöffnet ist
        if shop_settings.state:
            logger.info('Benachrichtigungen werden versendet')
            articles = Article.objects.all()
            reserved_orders = Order.objects.filter(status=Order.RESERVED_STATUS)

            for article in articles:
                reserved_orders = Order.objects.filter(article=article)

                # TODO: Mail senden

            self.stdout.write(self.style.SUCCESS('Benachrichtigungen wurden versendet.'))

        # Falls Skriptenshop geschlossen ist
        else:
            logger.debug('Cronjob zum versenden von Benachrichtigungen läuft. Skriptenshop geschlossen.')
            self.stdout.write(self.style.SUCCESS('Der Skriptenshop ist geschlossen'))
