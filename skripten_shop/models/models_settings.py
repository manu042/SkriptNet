from django.db import models


class CurrentSemester(models.Model):
    """
    Dieses Model speichert das aktuelle Semester
    """
    current_semester = models.CharField(max_length=20)


class ShopSettings(models.Model):
    """
    Model zum Speichern globaler Einstellungen des Skripten Shops
    Nur ein Skripten-Admin kann diese Einstellungen verändern
    """

    # Speichert Status des Skripten Shops (Offen bzw. Geschlossen)
    state = models.BooleanField(verbose_name='Shop Status',
                                help_text='Hiermit kann der Skriptenshop geöffnet bzw. geschlossen werden')

    # Max. bestellbare Anzahl an Skritpen/Pakete pro Semester
    max_article = models.CharField(max_length=2, verbose_name='Max. bestellbare Skripten',
                                   help_text='Max. Anzahl bestellbare Skripten pro Semester pro Student')

    # Dauer der Reservierung eines Skripts für einen Studenten
    days_reserved = models.CharField(max_length=2, verbose_name='Skripten Reservierungsfrist',
                                     help_text='Anzahl Tage, die ein Skript reserviert ist')