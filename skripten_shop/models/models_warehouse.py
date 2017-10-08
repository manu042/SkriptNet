# Django Packages
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# My Packages
from skripten_shop.models import Article

class AritcleInStock(models.Model):
    """
    Das Model speichert die Gesamtmenge eines Skripts im Lager
    """

    article = models.OneToOneField(Article, unique=True, on_delete=models.CASCADE, verbose_name='Artikel')
    amount = models.SmallIntegerField()

    class Meta:
        verbose_name = 'Artikel im Lager'
        verbose_name_plural = 'Artikel im Lager'

    def __str__(self):
        return self.article.name
