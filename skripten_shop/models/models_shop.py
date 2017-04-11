# Django Packages
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# My Packages
from .models_skripten import Article
from .models_users import Student


class Order(models.Model):
    """
    Auftrag
    """
    REQUEST_STATUS = 1
    PRINT_STATUS = 2
    RESERVED_STATUS = 3
    DELIVERD_STATUS = 4
    CANCELD_STATUS = 5
    EXPIRED_STATUS = 6

    STATUS_CHOICES = (
        (REQUEST_STATUS, 'in Bearbeitung'),
        (PRINT_STATUS, 'im Druck'),
        (RESERVED_STATUS, 'auf Lager'),
        (DELIVERD_STATUS, 'ausgegeben'),
        (CANCELD_STATUS, 'storniert'),
        (EXPIRED_STATUS, 'ausgelaufen'),
    )

    # https://docs.djangoproject.com/en/dev/ref/models/fields/#choices
    # request_entries = Order.objects.filter(status=Reorder.Order)

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    last_modified_date = models.DateTimeField(default=timezone.now, verbose_name='letzte Änderung')
    status = models.IntegerField(choices=STATUS_CHOICES, default=REQUEST_STATUS)

    class Meta:
        verbose_name = 'Bestellung'
        verbose_name_plural = 'Bestellungen'
        unique_together = (("article", "student"),)

    def __str__(self):
        text = 'Bestellung %s von %s' % (self.article.name, self.student.user.last_name)
        return text
