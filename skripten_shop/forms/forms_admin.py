# Django packages
from django import forms

# My packages
from skripten_shop.models import Skript, Paket


class StudygroupHorizontalAdminForm(forms.ModelForm):
    """
    https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.filter_horizontal
    """

    class Meta:
        model = Paket
        fields = '__all__'


class SkriptenHorizontalAdminForm(forms.ModelForm):
    """
    https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.filter_horizontal
    """

    class Meta:
        model = Skript
        fields = '__all__'