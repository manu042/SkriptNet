# Django Packages
from django.core import mail
from django.conf import settings
from django.template import loader
from django.core.mail import send_mail


# Third Party packages
import logging
import datetime
import threading

# My packages
from skripten_shop.models import ShopSettings, Order

logger = logging.getLogger('skripten_shop.default')


# Funktionen, um Seitenzugriffe auf bestimmte Gruppen zu beschränken
# https://docs.djangoproject.com/en/dev/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test
def has_permisson_admin(user):
    return user.groups.filter(name='Admin').exists()


def has_permisson_skriptenadmin(user):
    return user.groups.filter(name='Skriptenadmin').exists()


def has_permisson_skriptenausgabe(user):
    return user.groups.filter(name='Skriptenausgabe').exists()


def has_permisson_vorstand_verein(user):
    return user.groups.filter(name='Vorstand Verein').exists()


def has_permisson_aktives_vereinsmitglied(user):
    return user.groups.filter(name='Vereinsmitglieder').exists()


# Funktionen, um Datenbankwerte auszulesen
def current_semester_is():
    """
    Aktuelles Semester ermitteln
    """
    return ShopSettings.objects.get(pk=1).current_semester


def membership_fee_is():
    """
    Mitgliedsbeitrag aus der Datenbank abrufen
    """
    return ShopSettings.objects.get(pk=1).membership_fee


def max_article_is():
    """
    Wert max. bestellbare Skripten, die ein Student pro Semester erhalten darf ermitteln
    """
    return ShopSettings.objects.get(pk=1).max_article


def get_reservation_deadline():
    """
    Funktion liefert max. anzahl Tage, die ein Skript reserviert ist.
    """
    return ShopSettings.objects.get(pk=1).days_reserved


def get_current_semester():
    """
    Aktuelles Semester ermitteln
    """
    d = datetime.datetime.now()

    # Zeitraum zw. Jan. & Mai
    if d.month < 6:
        # Beginne SoSe
        s_name = "SoSe %s" % d.year
    else:
        # Sonst WiSe
        c_year = str(d.year)[-2:]
        n_year = str(d.year + 1)[-2:]
        s_name = "WS %s/%s" % (c_year, n_year)

    return s_name


class SendRegMailThread:
    """
    Starten eines neuen Threds, um asynchron von Django eine Mail für die Registrierung neuer Studenten zu versenden.
    """

    def __init__(self, user, confirm_url):
        self.user = user
        self.confirm_url = confirm_url
        self.t = threading.Thread(target=self.worker)
        self.t.start()

    def worker(self, *args):
        self.send_registration_mail(self.user, self.confirm_url)

    def send_registration_mail(self, user, confirm_url):
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
        Öffne bitte den folgenden Link, um deine Anmeldung abzuschließen:

        %s

        Viele Grüße

        Skriptenteam - Fachschaft 04 Elektro- und Informationstechnik
        """ % (user.first_name, user.last_name, confirm_url)

        try:
            send_mail(subject=subject, from_email=None, message=message, html_message=html_message,
                      recipient_list=[user.email])
            logger.info('Es wurde eine Mail zur Registrierung an %s gesendet.' % user.email)
        except Exception as e:
            logger.error('Beim Versenden der Mail zur Registrierung an %s ist ein fehler aufgetreten.' % user.email)


class SendStatusMailThread:
    """
    Die Klasse startet einen neuen Thread und versendet an die Studenten eine Lieferbestätigung
    """

    def __init__(self):
        self.thread = threading.Thread(target=self.worker)
        self.thread.start()

    def worker(self):
        self.send_mail()

    def send_mail(self):
        connection = mail.get_connection()
        try:
            logger.info("Bestaetigungsmails werden versendet!")
            # Manually open the connection
            connection.open()

            sendFlag = True
            while sendFlag:
                emails = []
                orders = Order.objects.filter(status=Order.RESERVED_STATUS).filter(mail_flag=False)[:100]
                for order in orders:
                    subject = "Dein Skript %s wurde geliefert" % order.article.article_number
                    send_to = order.student.user.email
                    msg = self.create_mail_body(order.student.user, order.article)

                    email = mail.EmailMessage(subject=subject, body=msg, to=[send_to],
                                             reply_to=[settings.DEFAULT_FROM_EMAIL], connection=connection)
                    emails.append(email)
                    order.mail_flag = True
                    order.save()
                try:
                    # Send emails in a single call
                    connection.send_messages(emails)
                    logger.info("Es wurden %s Bestaetigungsmails versendet" % len(emails))
                except Exception as e:
                    logger.error(e)

                if Order.objects.filter(status=Order.RESERVED_STATUS).filter(mail_flag=False).count() < 1:
                    sendFlag = False

        except Exception as e:
            logger.error(e)
        finally:
            # We need to manually close the connection.
            connection.close()
            logger.info("Bestaetigungsmails wurden versendet!")

    def create_mail_body(self, user, skript):
        res_deadline = get_reservation_deadline()

        msg1 = "Hallo %s %s,\n\n" % (user.first_name, user.last_name)
        msg2 = "das Skript %s %s, liegt absofot für dich für %s Tage in der Fachschaft zur abholung bereit.\n\n\n" % (
            skript.article_number, skript.name, res_deadline)
        msg3 = "Viele Grüße\n\nSkriptenteam - Fachschaft 04 Elektro- und Informationstechnik"
        message = msg1 + msg2 + msg3

        return message
