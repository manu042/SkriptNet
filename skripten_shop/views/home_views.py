"""
Dieses Modul enthält die folgden Views:

- HomeView: Startseite
- LoginView: Login Seite
- LogoutView: Zum ausloggen des Users
- RegistrationView: Zur Registrierung eines neuen Accounts
- ConfirmationView: Zur Bestätigung der Mail-Adresse
"""

# Django Packages
from django.http import Http404
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required


# Third Party packages
import logging

# My Packages
from skripten_shop.utilities import SendRegMailThread
from skripten_shop.forms import UserLoginForm, UserRegisterForm
from skripten_shop.models import NewStudentRegistration, Student, ShopSettings, Order

logger = logging.getLogger('skripten_shop.default')


@method_decorator(login_required, name='dispatch')
class HomeView(TemplateView):
    """
    Startseite des Skripten-Shops (Nach dem Login)
    """
    template_name = 'skripten_shop/home_templates/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        try:
            student = Student.objects.get(user=self.request.user)
            context["user"] = self.request.user
            context["orders"] = Order.objects.filter(student=student)
        except Exception as e:
            pass

        try:
            # Info Text aus der Datenbank laden
            context['info_text'] = ShopSettings.objects.get(pk=1).info_text
        except Exception as e:
            context['info_text'] = "Willkommen im Skriptenshop der FS04"
            logger.error(e)
        return context


class LoginView(View):
    """
    - Login Seite.
    - Ist der User bereits angemledet, wird der zur Homeseite weitergeleitet.
    - Die Anmeldung erfolgt mit der HM-Mail-Adresse.
    - In der Datenbank sind der Username und die Mail-Adresse das selbe.
    """
    form_class = UserLoginForm
    template_name = "skripten_shop/home_templates/login.html"

    def get(self, request):
        """
        View wird mit der Request Methode get aufgerufen.
        Dem User wird eine leere Login-Form angezeigt.
        """
        # Falls der User bereits angemeldet ist, wird er zur Startseite weitergeleitet
        if request.user.is_authenticated:
            return redirect("skripten_shop:home")

        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """
        View wird mit der Request Methode Post aufgerufen (Absenden der Login-Form).
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username").lower()
            password = form.cleaned_data.get("password")
            # authenticate prüft nur, ob der User existiert
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('skripten_shop:home')
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    """
    View zum ausloggen des Users
    """
    def get(self, request):
        logout(request)
        return redirect('skripten_shop:login')


class RegistrationView(View):
    """
    View zur Registrierung eines neuen Accounts für Studenten

    - Es wird ein inaktives Userprofil und ein Objekt der Klasse "NewStudentRegistration" erstellt.
      Zudem wird eine E-Mail mit einem Link zur Bestätigung der E-Mail-Adresse versendet.
    """
    form_class = UserRegisterForm
    template_name = "skripten_shop/home_templates/registrierung.html"

    def get(self, request):
        """
        View wird mit der Request Methode get aufgerufen.
        """
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """
        View wird mit der Request Methode Post aufgerufen.
        """
        form = self.form_class(request.POST)

        if form.is_valid():
            mail_address = form.cleaned_data.get('mail_address')

            # Objekt User erstellen; Für den Usernamen wird die Email-Adresse verwendet
            user = User.objects.create_user(username=mail_address)
            user.email = form.cleaned_data.get('mail_address')
            user.set_password(form.cleaned_data.get('password'))
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.is_active = False
            user.save()

            # Objekt NewStudentRegistration wird erstellt und mit dem User Objekt verknüpft
            new_student = NewStudentRegistration()
            new_student.user = user
            new_student.birth_date = form.cleaned_data.get('birth_date')
            new_student.create_activation_key()
            new_student.save()

            # Bestätigungs Mail versenden
            confirm_url = request.build_absolute_uri() + "confirm/" + new_student.activation_key
            # Mail für die Bestätigung der Registrierung in eigenem Thread versenden
            SendRegMailThread(user, confirm_url)
            success_message = mail_address

            # TODO: Logger löschen?
            logger.info('ANMELDUNG!!! Es wurde ein Konto mit der E-Mail-Adresse %s erstellt.' % mail_address)

            return render(request, self.template_name, {'success_message': success_message})
        return render(request, self.template_name, {'form': form})


class ConfirmationView(View):
    """
    Die View dient zur Bestätigung der Mail-Adresse und der Aktiverung des Accounts.
    """

    def get(self, request, activation_key):
        """
        Diese Seite dient zur Aktiverung eines neuen Accounts
        """
        # Lade Objekt aus der Datenbank. Falls Objekt nicht existiert, rufe 404 Page auf
        try:
            new_student = NewStudentRegistration.objects.get(activation_key=activation_key)
        except:
            raise Http404

        # Falls Account bereits Aktiviert wurde, zeige Error
        if new_student.activated:
            context = {'error_message': True}
            return render(request, 'skripten_shop/home_templates/registration_confirm.html', context)
        else:
            # Sonst aktiviere User und erstelle Objekt Student
            new_student.activated = True
            new_student.save()

            # User Objekt abrufen und auf aktiv setzen
            user = new_student.user
            user.is_active = True
            user.save()
            student = Student()
            student.user = new_student.user
            student.birth_date = new_student.birth_date
            student.save()
            return render(request, 'skripten_shop/home_templates/registration_confirm.html')