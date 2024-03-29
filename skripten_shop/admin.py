# Django Packages
from django.contrib import admin

# My Packages
from .models import Student, NewStudentRegistration, Professor, BezahltStatus, Skript
from .models import AritcleInStock, StudyGroup, Order

def make_active(modeladmin, request, queryset):
    queryset.update(active=True)
make_active.short_description = "Set selected skripts active"

def make_inactive(modeladmin, request, queryset):
    queryset.update(active=False)
make_inactive.short_description = "Set selected skripts inactive"

class StudentSemesterInline(admin.TabularInline):
    # Objekt Bezahltsatus für das Objekt Student editierbar machen
    model = BezahltStatus
    extra = 0


class StudentAdmin(admin.ModelAdmin):
    # Für jedes Objekt Student, dessen Bezahltstatus anzeigen
    inlines = [StudentSemesterInline, ]
    # Geburtsdatum in der Gesamtliste anzeigen
    list_display = ['__str__', 'birth_date']
    search_fields = ["user__first_name", "user__last_name"]


class SkriptInline(admin.StackedInline):
    model = Skript
    extra = 0


class ProfessorAdmin(admin.ModelAdmin):
    inlines = [SkriptInline, ]


class SkriptAdmin(admin.ModelAdmin):
    list_display = ["__str__", "name", "active", ]
    filter_horizontal = ('studygroup',)
    ordering = ["article_number", "name",]
    actions = [make_active, make_inactive]


class ArticleInStockAdmin(admin.ModelAdmin):
    list_display = ["article", "__str__", "amount", ]
    ordering = ["article",]


class NewStudentRegistrationAdmin(admin.ModelAdmin):
    search_fields = ["user__first_name", "user__last_name"]


class OrderAdmin(admin.ModelAdmin):
    search_fields = ["student__user__first_name", "student__user__last_name", "article__article_number", "article__name"]
    list_display = ["__str__", "status", "last_modified_date", "mail_flag"]
    list_filter = ["status", "mail_flag"]


# Models in der Django Admin Oberfläche anzeigen
admin.site.register(Student, StudentAdmin)
admin.site.register(Professor, ProfessorAdmin)
admin.site.register(Skript, SkriptAdmin)
admin.site.register(StudyGroup)
admin.site.register(NewStudentRegistration, NewStudentRegistrationAdmin)
admin.site.register(AritcleInStock, ArticleInStockAdmin)
admin.site.register(Order, OrderAdmin)
