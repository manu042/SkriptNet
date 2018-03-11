# Django Packages
from django.contrib import admin

# My Packages
from .models import Student, NewStudentRegistration, Professor, BezahltStatus, Skript
from .models import AritcleInStock, StudyGroup, SkriptInStock, Order


class StudentSemesterInline(admin.TabularInline):
    # Objekt Bezahltsatus für das Objekt Student editierbar machen
    model = BezahltStatus
    extra = 0


class StudentAdmin(admin.ModelAdmin):
    # Für jedes Objekt Student, dessen Bezahltstatus anzeigen
    inlines = [StudentSemesterInline, ]
    # Geburtsdatum in der Gesamtliste anzeigen
    list_display = ['__str__', 'birth_date']


class SkriptInline(admin.StackedInline):
    model = Skript
    extra = 0


class ProfessorAdmin(admin.ModelAdmin):
    inlines = [SkriptInline, ]


class SkriptAdmin(admin.ModelAdmin):
    list_display = ["__str__", "name", "active", ]
    filter_horizontal = ('studygroup',)
    ordering = ["article_number", "name",]


# Models in der Django Admin Oberfläche anzeigen
admin.site.register(Student, StudentAdmin)
admin.site.register(Professor, ProfessorAdmin)
admin.site.register(Skript, SkriptAdmin)
admin.site.register(StudyGroup)
admin.site.register(NewStudentRegistration)
admin.site.register(AritcleInStock)
admin.site.register(SkriptInStock)
admin.site.register(Order)
