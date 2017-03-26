# Django Packages
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# My Packages
from .models_users import Professor


class Article(models.Model):
    """
    Model Allgemein für alle Artikel (z.B. Skripten und Pakete)
    """
    # Artikelnummer für Skritpen und Pakete z.B. 01-001
    article_number = models.CharField(verbose_name='Artikel Nummer', max_length=20, unique=True)
    name = models.CharField(verbose_name='Artikel Name', max_length=50)
    description = models.CharField(verbose_name='Beschreibung', max_length=100, null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Artikel'
        verbose_name_plural = 'Artikel'

    def __str__(self):
        return self.name


class Skript(Article):
    """
    Model für Skripten, Vererbung von Artikel
    """
    author = models.ForeignKey(Professor, on_delete=models.CASCADE)
    # Professoren, die das Skript Verwenden
    users = models.ManyToManyField(Professor, related_name='user_profile', verbose_name="Verwender")
    # Farbe des Deckblatts Info für Druckdienstleister
    cover_sheet_color = models.CharField(max_length=20, verbose_name='Deckblattfarbe')
    page_numbers = models.IntegerField(default=0, verbose_name='Seitenzahl')
    # Semester indem das Skript angeboten wird
    semester = models.IntegerField()
    revision_date = models.DateField(verbose_name='Änderungsdatum')
    file = models.FileField(blank=True)

    class Meta:
        verbose_name = 'Skript'
        verbose_name_plural = 'Skripten'


class Paket(Article):
    """
    Model für Skriptenpakete, Vererbung von Artikel
    """
    cover_sheet_color = models.CharField(max_length=20, verbose_name='Deckblattfarbe')
    page_numbers = models.IntegerField(default=0, verbose_name='Seitenzahl')
    # Skripte, die das Paket enthält
    skripte = models.ManyToManyField(Skript)
    # Anzahl an Skripten, die im Paket enthalten sind
    amount = models.IntegerField(verbose_name='Skriptenanzahl')
    # Semester indem das Paket angeboten wird
    semester = models.IntegerField()

    class Meta:
        verbose_name = 'Paket'
        verbose_name_plural = 'Pakete'


class ArticleInCart(models.Model):
    """
    Das Model repräsentiert einen Artikel im Warenkorb eines Studenten
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Besteller')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Artikel')
    date_added_to_cart = models.DateTimeField(default=timezone.now, verbose_name='Hinzugefügt am')

    class Meta:
        verbose_name = 'Artikel in Warenkorb'
        verbose_name_plural = 'Artikel in Warenkorb'
        unique_together = (("customer", "article"),)


class ArticleInOrder(models.Model):
    """
    Das Model repräsentiert die Bestellung eines Skripts oder Pakets eines Studenten
    """
    TOORDER = 'to_order'
    INPRINT = 'in_print'
    RESERVED = 'reserved'
    DELIVERD = 'deliverd'
    CANCELD = 'canceled'
    EXPIRED = 'expired'
    status_choices = (
        (TOORDER, 'in Bearbeitung'),
        (INPRINT, 'im Druck'),
        (RESERVED, 'auf Lager'),
        (DELIVERD, 'ausgegeben'),
        (CANCELD, 'storniert'),
        (EXPIRED, 'ausgelaufen'),
    )

    # IF blank, dann nicht reserviert
    customer = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, verbose_name='Besteller')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Artikel')
    date_order_placed = models.DateTimeField(default=timezone.now, verbose_name='Bestellt am')
    status = models.CharField(max_length=20, choices=status_choices, default='to_order')

    class Meta:
        verbose_name = 'Bestellter Artikel'
        verbose_name_plural = 'Bestellte Artikel'
        unique_together = (("customer", "article"),)
