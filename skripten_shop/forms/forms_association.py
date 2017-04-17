# Django packages
from django import forms

# Third party packages
from skripten_shop.models import ShopSettings


class SendAssociationMailForm(forms.Form):
    subject = forms.CharField(label='Betreff')
    mail_text = forms.CharField(label='Nachricht', widget=forms.Textarea)


class AssociationSettingsForm(forms.ModelForm):
    # max = "{{ order_in_print.order_amount }}

    class Meta:
        model = ShopSettings
        fields = [
            'membership_fee',
        ]
