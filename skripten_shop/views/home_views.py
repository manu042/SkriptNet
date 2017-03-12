# Django Packages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView


# My Packages
from skripten_shop.forms import UserLoginForm


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
        form = UserLoginForm()

    context = {
        'form': form,
    }

    return render(request, 'skripten_shop/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('/')


def registration_view(request):


    if request.method == 'POST':
        # form =
        #if form.is_valid:
        pass
    else:
        # form =
        pass

    context = {
        'form':0
    }


    return render(request, 'skripten_shop/registrierung.html', context)


@method_decorator(login_required, name='dispatch')
class HomeView(TemplateView):
    """
    Startseite des Skripten Shops
    """
    template_name = 'skripten_shop/home.html'