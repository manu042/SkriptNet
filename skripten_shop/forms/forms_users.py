from django import forms
from django.contrib.auth import authenticate, get_user_model
import datetime
import re
from django import forms

User = get_user_model()


class UserLoginForm(forms.Form):
    """
    Formen für Login Seite
    - Login nur mit HM-Email Adresse möglich
    """
    username = forms.EmailField(label="HM-E-Mail-Adresse", max_length=30,
                                widget=forms.TextInput(
                                    attrs={'class': 'form-control', 'name': 'email', 'placeholder': 'HM-Email',
                                           'autofocus': ''}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control', 'name': 'password', 'placeholder': 'Passwort'}))

    def clean(self, *args, **kwargs):
        clean_data = super(UserLoginForm, self).clean()
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            # authenticate prüft nur, ob der User existiert
            user = authenticate(username=username, password=password)
            print(user)
            if not user:
                raise forms.ValidationError("Ungültige E-Mail-Adresse oder ungültiges Passwort")


class UserRegisterForm(forms.ModelForm):
    """
    Formen für User Registrierungsseite
    - Regisrtrierung erfolgt mit HM-Email statt mit Username

    Notwendig, um Bootstrap und CSS zu verwenden
    """
    username = forms.EmailField(label='HM-Email', widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'email', 'name': 'email', 'placeholder': 'muster@hm.edu'}))

    first_name = forms.CharField(label='Vorname', widget=forms.TextInput(
        attrs={'class': 'form-control', 'name': 'first_name', 'placeholder': 'Vorname'}))

    last_name = forms.CharField(label='Nachname', widget=forms.TextInput(
        attrs={'class': 'form-control', 'name': 'last_name', 'placeholder': 'Nachname'}))

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'name': 'password', 'placeholder': 'Passwort'}))

    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'name': 'password', 'placeholder': 'Passwort wiederholen'}))

    # Erzeugt eine Jahresliste für das Geburtsdatums Feld für Personen zwischen 15 und 60 Jahren
    current_year = datetime.datetime.now().year
    BIRTH_YEAR_CHOICES = sorted(range(current_year - 60, current_year - 14), reverse=True)
    birth_date = forms.DateField(label="Geburtsdatum", widget=forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES))

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
            # "captcha",
            # "terms",
        ]

    def clean_username(self):
        """
        Prüft, ob Email bereits registriert wurde und ob die Eingabe eine plausible HM Email ist
        Email und Username sind identisch
        """
        username = self.cleaned_data.get("username")

        username_qs = User.objects.filter(username=username)

        if re.split(r'@', username)[-1] == 'hm.edu':
            pass
        else:
            raise forms.ValidationError("Email ist keine gültige Hochschul Adresse")

        if username_qs.exists():
            raise forms.ValidationError("Diese Email-Adresse wurde bereits registriert")
        return username

    def clean_password2(self):
        """
        Prüft, ob Passwort und Passwort confirm übereinstimmen

        !!! {{ UserLoginForm.errors }} für raise ValidationError!!!
        """
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")

        if password != password2:
            raise forms.ValidationError("Die Passwörter stimmen nicht überein.")

            # def clean(self):
            #     """
            #     !!! Non_Field_Error für ValidationError!!!
            #     Prüft, ob Passwort und Passwort confirm übereinstimmen
            #     """
            #     password = self.cleaned_data.get("password")
            #     password2 = self.cleaned_data.get("password2")
            #
            #     if password != password2:
            #         raise forms.ValidationError("Die Passwörter stimmen nicht überein. Erneut versuchen?")
