# Django packages
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import User

# Third party packages
import hashlib


class NewStudentManager(models.Manager):

    def create_user(self):
        pass



class NewStudentRegistration(models.Model):
    """
     Dieses Model dient dazu, ein neu angelegten Account temporär zu speichern, bis dieser aktiviert wurde.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField()
    registration_date = models.DateField(default=timezone.now)
    activation_key = models.CharField(max_length=64)
    activated = models.BooleanField(default=False)

    #object = NewStudentManager()

    def __str__(self):
        name = self.user.first_name + ' ' + self.user.last_name
        return name

    def create_activation_key(self):
        first_name = self.user.first_name
        last_name = self.user.last_name
        time = str(timezone.now())
        string_to_hash = first_name + last_name + time
        self.activation_key = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    legic_id = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField()
    begin_membership = models.DateField(default=timezone.now)

    def __str__(self):
        name = self.user.first_name + ' ' + self.user.last_name
        return name
