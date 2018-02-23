# Writing custom django-admin commands
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/

# Django Packages
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

# Third party packages
import logging

# My Packages
from skripten_shop.models import Order, ShopSettings, AritcleInStock

logger = logging.getLogger('skripten_shop.default')


# TODO: logging erweitern
class Command(BaseCommand):
    """
    - Funktion über einen täglichen Cronjob ausführen

    Wenn der Skriptenshop geöffnet ist, werden evtl. abgelaufene Reservierungen freigegben
    
        - Falls sich eine Bestellung mit dem Artikel im Status "in Bearbeitung" befindet, wird der Artikel dieser zugeordnet.
    """

    help = 'Evtl. abgelaufene Bestellungen löschen'

    def handle(self, *args, **options):

        shop_settings = ShopSettings.objects.get(pk=1)

        # Falls Skriptenshop geöffnet ist
        if shop_settings.state:
            logger.info('Evtl. abgelaufene Bestellungen werden freigegeben')
            today = timezone.now()
            max_days_reserved = shop_settings.days_reserved
            reserved_orders = Order.objects.filter(status=Order.RESERVED_STATUS)

            for reserved_order in reserved_orders:
                reserved_since = reserved_order.last_modified_date
                delta = today - reserved_since

                if delta.days > int(max_days_reserved):
                    reserved_order.status = Order.EXPIRED_STATUS
                    reserved_order.last_modified_date = today
                    reserved_order.save()

                    try:
                        # TODO: Mail versenden
                        requested_order = Order.objects.filter(status=Order.REQUEST_STATUS).earliest(
                            'last_modified_date')
                        requested_order.status = Order.RESERVED_STATUS
                        requested_order.last_modified_date = today
                        requested_order.save()
                    except Order.DoesNotExist:
                        try:
                            aritcle_in_stock = AritcleInStock.objects.get(article=reserved_order.article)
                            aritcle_in_stock.amount += 1
                            aritcle_in_stock.save()
                        except AritcleInStock.DoesNotExist:
                            pass

            self.stdout.write(self.style.SUCCESS('Evtl. abgelaufene Bestellungen wurden freigegeben'))

        # Falls Skriptenshop geschlossen ist
        else:
            logger.debug('Cronjob zum freigeben abgelaufener Skripten läuft. Skriptenshop geschlossen.')
            self.stdout.write(self.style.SUCCESS('Der Skriptenshop ist geschlossen'))
