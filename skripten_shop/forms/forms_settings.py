# Django Packages
from django import forms

# Third party packages
from skripten_shop.models import ShopSettings


class SettingsForm(forms.ModelForm):
    class Meta:
        state = forms.BooleanField(widget=forms.CheckboxInput)
        info_text = forms.TextInput(attrs={'required': False})

        model = ShopSettings
        fields = [
            'state',
            'max_article',
            'days_reserved',
        ]


class InfoTextForm(forms.ModelForm):
    class Meta:
        info_text = forms.TextInput(attrs={'required': False})

        model = ShopSettings
        fields = [
            'info_text',
        ]
