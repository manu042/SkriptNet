# Django packages
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# My Packages


class NewUserManager(models.Manager):
    pass


class NewUserRegistration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        name = self.user.first_name + ' ' + self.user.last_name
        return name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    legic_id = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField()
    begin_membership = models.DateField(default=timezone.now)

    def __str__(self):
        name = self.user.first_name + ' ' + self.user.last_name
        return name


class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        name = self.user.first_name + ' ' + self.user.last_name
        return name


class BezahltStatus(models.Model):
    semester = models.CharField(max_length=30)
    paid = models.BooleanField(default=False)
    student = models.ForeignKey('Student', null=True)
    date = models.DateTimeField(default=timezone.now)
