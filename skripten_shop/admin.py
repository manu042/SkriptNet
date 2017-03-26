# Django Packages
from django.contrib import admin

# My Packages
from .models import Student, NewStudentRegistration, Paket, Article, ArticleInCart, ArticleInOrder, Professor, \
    BezahltStatus, Skript, CurrentSemester, ShopSettings


# Users
# =======================================================================
class SkriptInline(admin.StackedInline):
    model = Skript
    extra = 0


class ProfessorAdmin(admin.ModelAdmin):
    inlines = [SkriptInline, ]


class StudentSemesterInline(admin.TabularInline):
    model = BezahltStatus
    extra = 0


class StudentAdmin(admin.ModelAdmin):
    inlines = [StudentSemesterInline, ]
    list_display = ['__str__', 'birth_date']


admin.site.register(Professor, ProfessorAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(NewStudentRegistration)

# Skripten
# =======================================================================
admin.site.register(Paket)
admin.site.register(Article)
admin.site.register(ArticleInCart)
admin.site.register(ArticleInOrder)
