# Django Packages
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password

# Third party packages
import re
import datetime
from captcha.fields import ReCaptchaField

# My packages
from skripten_shop.models import ShopSettings


User = get_user_model()


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


class ScanLegicForm(forms.Form):
    """
    Form zum Scannen der Legic ID bei der Ausgabe
    """
    legic_id = forms.CharField(label="Legic-ID", widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))


class ActivateStudentForm(forms.Form):
    """
    Form zum verknüpfen einer Legic ID mit dem Account eines Studenten
    """
    legic_id = forms.CharField(label="Legic-ID")
    birth_date = forms.DateField(label="Geburtsdatum (TT.MM.JJJJ)",
                                 widget=forms.DateInput(attrs={'autofocus': 'autofocus'}))


class NewLegicCardForm(forms.Form):
    """
    Form zur Eingabe einer neuen Legic-ID
    """
    email = forms.EmailField(max_length=100, label='E-Mail Adresse',
                             widget=forms.EmailInput(attrs={'autofocus': 'autofocus'}))
    new_legic_id = forms.CharField(label="Neue Legic-ID")


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


class UserLoginForm(forms.Form):
    """
    Formen für Login Seite
    - Login nur mit HM-Email Adresse möglich
    """
    username = forms.EmailField(label="HM-E-Mail-Adresse", max_length=30,
                                widget=forms.TextInput(
                                    attrs={'class': 'form-control', 'name': 'email', 'placeholder': 'HM-Email',
                                           'autofocus': 'autofocus'}))

    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control', 'name': 'password', 'placeholder': 'Passwort'}))

    def clean(self, *args, **kwargs):
        cleaned_data = super(UserLoginForm, self).clean()

        try:
            username = cleaned_data.get("username").lower()
            password = cleaned_data.get("password")
        except:
            raise forms.ValidationError("E-Mail-Adresse bitte auf Leerzeichen überprüfen")

        if username and password:
            user = None
            # Prüft ob User aktiv ist
            try:
                user = User.objects.get(username=username)
            except:
                pass
            if user:
                if not user.is_active:
                    raise forms.ValidationError('Das Benutzerkonto ist inaktiv.')

            # Prüft, ob Username und Passwort korrekt sind
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Ungültige E-Mail-Adresse oder ungültiges Passwort")


class UserRegisterForm(forms.Form):
    """
    Form zur Registrierung neuer Accounts für Studenten
    - Regisrtrierung erfolgt mit HM-Email
    - Die Email wird in das Userfeld Username eingetragen
    """
    # Erzeugt eine Jahresliste für das Geburtsdatums Feld für Personen zwischen 15 und 60 Jahren
    current_year = datetime.datetime.now().year
    BIRTH_YEAR_CHOICES = sorted(range(current_year - 60, current_year - 14), reverse=True)

    mail_address = forms.EmailField(label='HM-Email', widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'email', 'name': 'email', 'placeholder': 'muster@hm.edu',
               'autofocus': 'autofocus'}))

    first_name = forms.CharField(label='Vorname', widget=forms.TextInput(
        attrs={'class': 'form-control', 'name': 'first_name', 'placeholder': 'Vorname'}))

    last_name = forms.CharField(label='Nachname', widget=forms.TextInput(
        attrs={'class': 'form-control', 'name': 'last_name', 'placeholder': 'Nachname'}))

    password = forms.CharField(label='Passwort', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'name': 'password', 'placeholder': 'Passwort'}))

    password_confirm = forms.CharField(label='Passwort bestätigen', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'name': 'password confirm', 'placeholder': 'Passwort bestätigen'}))

    birth_date = forms.DateField(label="Geburtsdatum", widget=forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES))

    terms = forms.BooleanField(label="Allgemeines & Datenschutz gelesen", widget=forms.CheckboxInput())

    captcha = ReCaptchaField()

    def clean_mail_address(self):
        """
        Prüft, ob Email bereits registriert wurde und ob die Eingabe eine plausible HM Email ist.
        Die Email Adresse wird in der Datenbank, für den Usernamen und die Email Adresse verwendet
        """
        mail_address = self.cleaned_data.get("mail_address").lower()

        username_qs = User.objects.filter(username=mail_address)

        if not re.split(r'@', mail_address)[-1] == 'hm.edu':
            raise forms.ValidationError("Diese Email-Adresse ist keine gültige Hochschul Adresse")

        if username_qs.exists():
            raise forms.ValidationError("Diese Email-Adresse wurde bereits registriert")
        return mail_address

    def clean_password(self):
        '''
        Prüft Passwort anforderungen
        https://docs.djangoproject.com/en/dev/topics/auth/passwords/#password-validation
        '''
        password = self.cleaned_data.get("password")
        validate_password(password)
        return password

    def clean_password_confirm(self):
        """
        Prüft, ob Passwort und Passwort confirm übereinstimmen
        """
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Die Passwörter stimmen nicht überein.")
        return password_confirm
