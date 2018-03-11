# Django packages
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Third party packages
import hashlib


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    legic_id = models.CharField(max_length=64, blank=True)
    birth_date = models.DateField(verbose_name='Geburtsdatum')

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Studenten'

    def __str__(self):
        name = self.user.first_name + ' ' + self.user.last_name
        return name


class BezahltStatus(models.Model):
    semester = models.CharField(max_length=30)
    paid = models.BooleanField(default=True, verbose_name='Bezahlt')
    student = models.ForeignKey('Student', null=True, on_delete=True)
    date = models.DateTimeField(default=timezone.now, verbose_name='Bezahlt am')


class Professor(models.Model):
    TITLE_CHOICES = (
        ("Prof. Dr.", 'Prof. Dr.'),
        ("Prof.", 'Prof.'),
        ("Dr.", 'Dr.'),
        ("Herr", 'Herr'),
        ("Frau", 'Frau'),
    )

    title = models.CharField(verbose_name="Anrede", choices=TITLE_CHOICES, default="Prof. Dr.", max_length=10)
    first_name = models.CharField(verbose_name="Vorname", max_length=20)
    last_name = models.CharField(verbose_name="Nachname", max_length=20)
    mail_address = models.EmailField()

    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professoren'

    def __str__(self):
        return self.title + " " + self.last_name


class StudyGroup(models.Model):
    title = models.CharField(max_length=10, unique=True, verbose_name='Bezeichnung')

    class Meta:
        verbose_name = 'Studiengruppe'
        verbose_name_plural = 'Studiengruppen'

    def __str__(self):
        return self.title


class Article(models.Model):
    """
    Model Allgemein für Skripte und Pakete
    """
    # Artikelnummer für Skritpen und Pakete z.B. 01-001
    article_number = models.CharField(verbose_name='Artikel Nummer', max_length=20, unique=True)
    name = models.CharField(verbose_name='Artikel Name', max_length=50)
    description = models.CharField(verbose_name='Beschreibung', max_length=100, null=True, blank=True)
    shelf_number = models.CharField(verbose_name='Fach-Nummer', max_length=15, null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Artikel'
        verbose_name_plural = 'Artikel'

    def __str__(self):
        return self.article_number


class Skript(Article):
    """
    Model für Skripten, Vererbung von Artikel
    """
    author = models.ForeignKey(Professor, verbose_name="Autor", on_delete=models.CASCADE)
    studygroup = models.ManyToManyField(StudyGroup, verbose_name='Studiengruppe')
    # Farbe des Deckblatts Info für Druckdienstleister
    cover_sheet_color = models.CharField(max_length=20, verbose_name='Deckblattfarbe')
    page_numbers = models.IntegerField(default=0, verbose_name='Seitenzahl')
    # Semester indem das Skript angeboten wird
    semester = models.IntegerField()
    revision_date = models.DateField(verbose_name='Änderungsdatum')

    class Meta:
        verbose_name = 'Skript'
        verbose_name_plural = 'Skripte'


class NewStudentRegistration(models.Model):
    """
    Model speichert temporär einen neu erstellten Benutzeraccount
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(verbose_name='Geburtsdatum')
    registration_date = models.DateField(default=timezone.now)
    activation_key = models.CharField(max_length=64)
    activated = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Neu Registrierte Studenten'
        verbose_name_plural = 'Neu Registrierte Studenten'

    def __str__(self):
        name = self.user.first_name + ' ' + self.user.last_name
        return name

    def create_activation_key(self):
        first_name = self.user.first_name
        last_name = self.user.last_name
        time = str(timezone.now())
        string_to_hash = first_name + last_name + time + str(self.user.pk)
        self.activation_key = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()


class ArticleInCart(models.Model):
    """
    Das Model repräsentiert einen Artikel im Warenkorb eines Studenten
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added_to_cart = models.DateTimeField(default=timezone.now, verbose_name='Hinzugefügt am')

    class Meta:
        verbose_name = 'Artikel in Warenkorb'
        verbose_name_plural = 'Artikel in Warenkorb'
        unique_together = (("article", "student"),)


class Order(models.Model):
    """
    Skriptenbestellung eines Studenten
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
        (EXPIRED_STATUS, 'Reservierung abgelaufen'),
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


class SkriptInStock(models.Model):
    """
    Die Klasse repräsentiert ein physikalisches Skript im Lager
    """
    skript = models.ForeignKey(Skript, on_delete=models.CASCADE, verbose_name='Skript', unique=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Bestellung", null=True, blank=True)

    # Todo: Anpassen
    def __str__(self):
        return self.skript.name


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


class ShopSettings(models.Model):
    """
    Model zum Speichern globaler Einstellungen des Skripten Shops
    Nur ein Skripten-Admin kann diese Einstellungen verändern
    """
    current_semester = models.CharField(max_length=20, verbose_name='Aktuelles Semester')
    # Speichert Status des Skripten Shops (Offen bzw. Geschlossen)
    state = models.BooleanField(verbose_name='Shop Status',
                                help_text='Hiermit kann der Skriptenshop geöffnet bzw. geschlossen werden')

    # Max. bestellbare Anzahl an Skritpen pro Semester
    max_article = models.CharField(max_length=2, verbose_name='Max. bestellbare Skripten',
                                   help_text='Max. Anzahl bestellbare Skripten pro Semester pro Student')

    # Anzahl Tage, die ein Skript für einen Studenten reserviert ist
    days_reserved = models.CharField(max_length=2, verbose_name='Skripten Reservierungsfrist',
                                     help_text='Anzahl Tage, die ein Skript reserviert ist')
    membership_fee = models.PositiveIntegerField(verbose_name='Mitgliedsbeitrag')
    info_text = models.TextField(verbose_name='Info Text', blank=True)

    def __str__(self):
        return 'Shop Einstellungen'
