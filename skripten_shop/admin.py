from django.contrib import admin

from .models import Student, NewStudentRegistration

admin.site.register(Student)
admin.site.register(NewStudentRegistration)