# Django Packages
from django.contrib import admin

# My Packages
from .models import Student, NewStudentRegistration, Paket, Article, ArticleInCart, Professor, \
    BezahltStatus, Skript, ShopSettings
from skripten_shop.forms import SkriptAdminForm
from .models import AritcleInStock, Order, StudyGroup

# Users
# =======================================================================


class SkriptAdmin(admin.ModelAdmin):
    """
    nifty unobtrusive JavaScript “filter” für MultiToManyField
    """
    filter_horizontal = ('studygroup',)
    form = SkriptAdminForm

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


admin.site.register(Skript, SkriptAdmin)
admin.site.register(Professor, ProfessorAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(NewStudentRegistration)
admin.site.register(Paket)
admin.site.register(Article)
admin.site.register(ArticleInCart)
admin.site.register(StudyGroup)
admin.site.register(AritcleInStock)

# TODO: Löschen
admin.site.register(ShopSettings)
admin.site.register(Order)

