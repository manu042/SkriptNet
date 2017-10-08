# Django packages
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Third party packages
import hashlib


# TODO: Verwenden oder löschen?
class NewStudentManager(models.Manager):

    def create_user(self):
        pass


class NewStudentRegistration(models.Model):
    """
     Dieses Model dient dazu, ein neu angelegten Account temporär zu speichern, bis dieser aktiviert wurde.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(verbose_name='Geburtsdatum')
    registration_date = models.DateField(default=timezone.now)
    activation_key = models.CharField(max_length=64)
    activated = models.BooleanField(default=False)

    #object = NewStudentManager()

    class Meta:
        verbose_name = 'Neu Registrierte Studenten'
        verbose_name_plural = 'Neu Registrierte Studenten'

    def __str__(self):
        name = self.user.first_name + ' ' + self.user.last_name
        return name

    # TODO: Evtl. löschen
    def create_activation_key(self):
        first_name = self.user.first_name
        last_name = self.user.last_name
        time = str(timezone.now())
        string_to_hash = first_name + last_name + time
        self.activation_key = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()


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
    student = models.ForeignKey('Student', null=True)
    date = models.DateTimeField(default=timezone.now, verbose_name='Bezahlt am')


# TODO: Evtl. Felder hinzufügen Bsp: Anrede, Titel
class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professoren'

    def __str__(self):
        return self.user.last_name
