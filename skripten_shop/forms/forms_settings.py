from django import forms

from skripten_shop.models import ShopSettings


class SettingsForm(forms.ModelForm):
    class Meta:
        state = forms.BooleanField(widget=forms.CheckboxInput)

        model = ShopSettings
        fields = [
            'state',
            'max_article',
            'days_reserved',
        ]
