# Django Packages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail

# Third party packages
import hashlib

# My Packages
from skripten_shop.forms import UserLoginForm, UserRegisterForm
from skripten_shop.models import NewStudentRegistration, Student


def login_view(request):
    """
    View für Login Seite
    - Anmeldung Erfolgt mit HM-Email
    - Username und Email sind in der Datenbank dasselbe
    """

    # Falls User bereits angemeldet, zur Startseite weiterleiten
    if request.user.is_authenticated:
        return redirect('/home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            # authenticate prüft nur, ob der User existiert
            # Redundant
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/home')
    else:
        # TODO: initial entfernen
        form = UserLoginForm(initial={'username': 'admin@hm.edu'})

    context = {
        'form': form,
    }

    return render(request, 'skripten_shop/home_templates/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('/')


def registration_view(request):
    """
    Diese Seite dient zur Registrierung neuer Accounts für Studenten

    - Nach dem ausfüllen der Form, wird ein neues (inaktives) User Profil und ein Model "NewStudentRegistration" angelegt,
      zudem wird eine Bestätigungs Email mit einem activation_key versendet
    """

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():

            user = User.objects.create_user(username=form.cleaned_data.get('mail_address'))
            user.email = form.cleaned_data.get('mail_address')
            user.set_password(form.cleaned_data.get('password'))
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.is_active = False
            user.save()

            birth_date = form.cleaned_data.get('birth_date')
            string_to_hash = user.first_name + user.last_name + str(timezone.now())
            activation_key = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
            new_student = NewStudentRegistration()
            new_student.user = user
            new_student.birth_date = birth_date
            new_student.activation_key = activation_key
            new_student.save()

            subject = 'Verifiziere deine Email-Adresse'
            confirm_url = request.build_absolute_uri() + "confirm/" + new_student.activation_key
            message = "Um den Verifizierungsprozess zu beenden, klicke einfach auf den Link unten. \n" + confirm_url
            # TODO: recipient_list anpassen
            send_mail(subject=subject, from_email=None, message=message,
                      recipient_list=["inbox9k@gmail.com"])
            success_message = form.cleaned_data.get('mail_address')

            context = {
                'success_message': success_message,
            }

            return render(request, 'skripten_shop/home_templates/registrierung.html', context)

    else:
        form = UserRegisterForm()

    context = {
        'form':form,
    }

    return render(request, 'skripten_shop/home_templates/registrierung.html', context)


def confirm_mail_view(request, activation_key):
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

        # User Objekt abrufen und User auf aktiv setzen
        user = new_student.user
        user.is_active = True
        user.save()
        student = Student()
        student.user = new_student.user
        student.birth_date = new_student.birth_date
        student.save()
    return render(request, 'skripten_shop/home_templates/registration_confirm.html')


@method_decorator(login_required, name='dispatch')
class HomeView(TemplateView):
    """
    Startseite des Skripten Shops
    """
    template_name = 'skripten_shop/home_templates/home.html'


