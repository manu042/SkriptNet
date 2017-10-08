from django.core.mail import send_mail
from django.template import loader
from django.core.mail import EmailMessage


def send_registration_mail(user, confirm_url):
    """
    Funktion zum versenden der Bestätigungs Email beim Registrierungsprozess
    """
    subject = 'Skripten FS04: E-Mail-Adresse verifizieren'

    html_message = loader.render_to_string(
        "skripten_shop/home_templates/registration_mail_template.html",
        {
            "user": user,
            "confirm_url": confirm_url,
        }
    )

    message = """ Hallo %s %s,
    
    du erhälst diese Email, weil du dich für den Skriptendienst der Fachschaft 04 angemeldet hast. 
    Öffne bitte den folgden Link, um deine Anmeldung abzuschließen:
    
    %s
    
    Viele Grüße

    Skriptenteam - Fachschaft 04 Elektrotechnik und Informationstechnik
    """ % (user.first_name, user.last_name, confirm_url)

    send_mail(subject=subject, from_email=None, message=message, html_message=html_message,
              recipient_list=[user.email])
