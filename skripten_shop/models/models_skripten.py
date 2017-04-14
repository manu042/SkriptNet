# Django Packages
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# My Packages
from .models_users import Professor
from .models_settings import StudyGroup


class Article(models.Model):
    """
    Model Allgemein für Skripte und Pakete
    """
    # Artikelnummer für Skritpen und Pakete z.B. 01-001
    article_number = models.CharField(verbose_name='Artikel Nummer', max_length=20, unique=True)
    name = models.CharField(verbose_name='Artikel Name', max_length=50)
    description = models.CharField(verbose_name='Beschreibung', max_length=100, null=True, blank=True)
    shelf_number = models.IntegerField(verbose_name='Fach Nummer')
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
    studygroup = models.ManyToManyField(StudyGroup, verbose_name='Studiengruppe')
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

