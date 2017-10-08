# Django Packages
from django.contrib import admin

# My Packages
from .models import Student, NewStudentRegistration, Paket, ArticleInCart, Professor, \
    BezahltStatus, Skript, ShopSettings
from skripten_shop.forms import StudygroupHorizontalAdminForm, SkriptenHorizontalAdminForm
from .models import AritcleInStock, Order, StudyGroup


# Users
# =======================================================================


class StudygroupHorizontal(admin.ModelAdmin):
    """
    nifty unobtrusive JavaScript “filter” für MultiToManyField
    """
    filter_horizontal = ('studygroup',)
    form = StudygroupHorizontalAdminForm


class SkriptenpHorizontal(admin.ModelAdmin):
    """
    nifty unobtrusive JavaScript “filter” für MultiToManyField
    """
    filter_horizontal = ('skripte',)
    form = SkriptenHorizontalAdminForm


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


admin.site.register(Skript, StudygroupHorizontal)
admin.site.register(Professor, ProfessorAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Paket, SkriptenpHorizontal)
admin.site.register(NewStudentRegistration)
admin.site.register(ArticleInCart)
admin.site.register(StudyGroup)
admin.site.register(AritcleInStock)


# TODO: Löschen
admin.site.register(ShopSettings)
admin.site.register(Order)

