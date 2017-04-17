# Django packages
from django.db import models


class ShopSettings(models.Model):
    """
    Model zum Speichern globaler Einstellungen des Skripten Shops
    Nur ein Skripten-Admin kann diese Einstellungen verändern
    """
    current_semester = models.CharField(max_length=20, verbose_name='Aktuelles Semester')
    # Speichert Status des Skripten Shops (Offen bzw. Geschlossen)
    state = models.BooleanField(verbose_name='Shop Status',
                                help_text='Hiermit kann der Skriptenshop geöffnet bzw. geschlossen werden')

    # Max. bestellbare Anzahl an Skritpen/Pakete pro Semester
    max_article = models.CharField(max_length=2, verbose_name='Max. bestellbare Skripten',
                                   help_text='Max. Anzahl bestellbare Skripten pro Semester pro Student')

    # Dauer der Reservierung eines Skripts für einen Studenten
    days_reserved = models.CharField(max_length=2, verbose_name='Skripten Reservierungsfrist',
                                     help_text='Anzahl Tage, die ein Skript reserviert ist')
    membership_fee = models.PositiveIntegerField(verbose_name='Mitgliedsbeitrag')
    info_text = models.TextField(verbose_name='Info Text', blank=True)

    def __str__(self):
        return 'Shop Einstellungen'


class StudyGroup(models.Model):
    title = models.CharField(max_length=10, unique=True, verbose_name='Bezeichnung')

    class Meta:
        verbose_name = 'Studiengruppe'
        verbose_name_plural = 'Studiengruppen'

    def __str__(self):
        return self.title
