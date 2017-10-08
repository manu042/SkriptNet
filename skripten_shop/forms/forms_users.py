# Django Packages
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password

# Third party packages
import re
import datetime
from captcha.fields import ReCaptchaField

User = get_user_model()


class UserLoginForm(forms.Form):
    """
    Formen für Login Seite
    - Login nur mit HM-Email Adresse möglich
    """
    username = forms.EmailField(label="HM-E-Mail-Adresse", max_length=30,
                                widget=forms.TextInput(
                                    attrs={'class': 'form-control', 'name': 'email', 'placeholder': 'HM-Email'}))
    # TODO: 'autofocus': 'autofocus' zu username hinzufügen
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control', 'name': 'password', 'placeholder': 'Passwort',
                                          'autofocus': 'autofocus'}))

    def clean(self, *args, **kwargs):
        clean_data = super(UserLoginForm, self).clean()
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

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
        mail_address = self.cleaned_data.get("mail_address")

        username_qs = User.objects.filter(username=mail_address)

        # TODO Code aktivieren und umschreiben (siehe http://chimera.labs.oreilly.com/books/1230000000393/ch02.html#_problem_22)
        # if re.split(r'@', mail_address)[-1] == 'hm.edu':
        #     pass
        # else:
        #     raise forms.ValidationError("Die Email-Adresse ist keine gültige Hochschul Adresse")

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
