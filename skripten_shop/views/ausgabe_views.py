# Django Packages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from django.views.generic import TemplateView, DetailView, View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator

# Third party packages
import hashlib
import logging

# My Packages
from skripten_shop.forms import ScanLegicForm, ActivateStudentForm, NewLegicCardForm
from skripten_shop.models import Article, Skript, Order, Student, BezahltStatus, AritcleInStock
from skripten_shop.utilities import has_permisson_skriptenausgabe
from skripten_shop.utilities import current_semester_is, max_article_is

logger = logging.getLogger('skripten_shop.default')


@login_required
@user_passes_test(has_permisson_skriptenausgabe)
def scan_legic_view(request):
    """
    View zum scannen der Legic-ID eiens Studenten
    """
    # Legic-ID aus Session Cookie löschen
    try:
        del request.session['current_legic']
    except:
        pass

    if request.method == 'POST':
        form = ScanLegicForm(request.POST)

        if form.is_valid():
            legic_id = form.cleaned_data.get('legic_id')

            # Speichern der Legic-ID im Session Cookie
            request.session['current_legic'] = legic_id

            try:
                # Hashwert der Legic-ID berechnen
                legic_id_hash_value = hashlib.sha256(legic_id.encode('utf-8')).hexdigest()

                # Liefert Student mit zugehöriger Legic ID zurück
                student = Student.objects.get(legic_id=legic_id_hash_value)

                # Letzen BezahltStatus des Studenten abrufen
                last_semester_paid = BezahltStatus.objects.filter(student=student).latest('date')

                # Prüft ob der Student in diesem Semester bereits bezahlt hat
                # Falls nicht wird die Ausgabe weitergeleitet zur reaktivierungsview
                if not last_semester_paid.semester == current_semester_is():
                    return redirect(reverse('skripten_shop:reaktivierung'))
                else:
                    return redirect(reverse('skripten_shop:ausgabe'))

            # Falls kein Student mit dieser Legic-ID gefunden wurde
            except Student.DoesNotExist:
                return redirect(reverse('skripten_shop:aktivierung'))

    # Die Seite wird mit der Request Methode Get aufgerufen
    else:
        form = ScanLegicForm()

    context = {
        'form': form
    }

    return render(request, 'skripten_shop/ausgabe_templates/scan_legic.html', context)


@login_required
@user_passes_test(has_permisson_skriptenausgabe)
def individual_assistance_view(request):
    try:
        # Legic-ID aus Session Cookie auslesen
        legic_id_hash_value = hashlib.sha256(request.session['current_legic'].encode('utf-8')).hexdigest()
    except Exception:
        logger.error('Legic-ID konnte nich aus dem Session Cookie ausgelesen werden.')

        context = {
            'error_message': 'Legic-ID konnte nich aus dem Session Cookie ausgelesen werden.'
                             ' Bitte an den Administrator wenden.'
        }

        return render(request, 'skripten_shop/ausgabe_templates/individual_assistance.html', context)

    student = Student.objects.get(legic_id=legic_id_hash_value)
    student_order = Order.objects.filter(student=student)

    if request.method == 'POST':
        # Rückgabe starten
        if "return" in request.POST:
            order_id = request.POST["return"]
            order_return = Order.objects.get(pk=order_id)

            context = {
                'student': student,
                "return": order_return
            }
            return render(request, 'skripten_shop/ausgabe_templates/individual_assistance.html', context)
        # Rückgabe durchführen
        elif "execute_return" in request.POST:
            try:
                order_id = request.POST["execute_return"]
                order_return = Order.objects.get(pk=order_id)
                order_return.delete()
                article_in_stock = AritcleInStock.objects.get(article=order_return.article)
                article_in_stock.amount += 1
                article_in_stock.save()
                messages.success(request, "Das Skript wurde erfolgreich zurückgegeben")
            except Exception as e:
                messages.error(request, "Bei der Rückgabe ist ein Fehler aufgetreten")
                logger.error(e)
            finally:
                return redirect(reverse("skripten_shop:individualbetreuung"))

        selected_orders_id = request.POST.getlist('selected_reserved[]')
        for selected_order_id in selected_orders_id:
            order = Order.objects.get(pk=selected_order_id)
            order.status = Order.DELIVERD_STATUS
            order.save()

        # Legic-ID aus Session Cookie löschen
        del request.session['current_legic']

        return redirect(reverse('skripten_shop:scan-legic'))


    context = {
        'student': student,
        'student_order': student_order,
    }

    return render(request, 'skripten_shop/ausgabe_templates/individual_assistance.html', context)


@login_required
@user_passes_test(has_permisson_skriptenausgabe)
def reorder_view(request):
    try:
        # Legic-ID aus Session Cookie auslesen
        legic_id_hash_value = hashlib.sha256(request.session['current_legic'].encode('utf-8')).hexdigest()
    except Exception:
        logger.error('Legic-ID konnte nich aus dem Session Cookie ausgelesen werden.')

        context = {
            'error_message': 'Legic-ID konnte nicht aus dem Session Cookie ausgelesen werden.'
                             ' Bitte an den Administrator wenden.'
        }

        return render(request, 'skripten_shop/ausgabe_templates/reorder.html', context)

    student = Student.objects.get(legic_id=legic_id_hash_value)

    if request.method == 'POST':

        selected_articels_id = request.POST.getlist('selected_articel[]')

        error_message = False
        for selected_articel_id in selected_articels_id:
            try:
                article = Article.objects.get(pk=selected_articel_id)
                order = Order(article=article, student=student)
                order.save()
            except IntegrityError:
                error_message = True
                messages.error(request,
                               'Das Skript %s kann nicht bestellt werden!  Der Student hat dieses Skript bereits bestellt.' % Article.objects.get(
                                   pk=selected_articel_id).article_number)

        if error_message:
            return redirect(reverse('skripten_shop:reorder'))

        # Legic-ID aus Session Cookie löschen
        del request.session['current_legic']

        return redirect(reverse('skripten_shop:scan-legic'))

    # Alle aktiven Skripte aus der Datenbank laden
    skripte_active = Skript.objects.filter(active=True)
    # Dictonary mit allen Skripten aus dem Lager und deren Menge erstellen
    stock_dict = {x.article.article_number: x.amount for x in AritcleInStock.objects.all()}
    # Alle Bestellungen des Studenten aus der DB laden
    order = [order.article.article_number for order in Order.objects.filter(student=student)]

    skripte = []
    # Liste der nachbestellbaren Skripte für den aktuellen Student erstellen
    for skript in skripte_active:
        try:
            # Prüfen, ob das Skript noch frei verfügbar ist
            amount = stock_dict[skript.article_number]
            if amount == 0:
                # Prüfen, ob der Student das Skript bereits erhalten hat
                if skript.article_number not in order:
                    skripte.append(skript)

        except Exception as e:
            # Prüfen, ob der Student das Skript bereits erhalten hat
            if skript.article_number not in order:
                skripte.append(skript)

    context = {
        'student': student,
        'skripte': skripte,
    }

    return render(request, 'skripten_shop/ausgabe_templates/reorder.html', context)


@login_required
@user_passes_test(has_permisson_skriptenausgabe)
def activation_view(request):
    """
    View zur verknüpfung des Studenten und seiner Legic-ID
    - Wird aufgerufen, falls die Legic-ID unbekannt ist
    """

    if request.method == 'POST':
        form = ActivateStudentForm(request.POST)

        # Wenn Button Suchen gedrückt wurde
        if 'search' in request.POST:
            if form.is_valid():
                birth_date = form.cleaned_data.get('birth_date')
                legic_id = form.cleaned_data.get('legic_id')

                # Die Legic ID wird im Session Cookie gespeichert
                request.session['current_legic'] = legic_id

                # Es werden alle Neuregistrierungen (Studenten) mit dem selben Geburtsdatum gefiltert und die Anzahl berechnet
                quantity = Student.objects.filter(legic_id='').filter(birth_date=birth_date).count()

                # Falls keine Neuregistrierungen (Studenten) gefunden wurden
                if quantity < 1:

                    context = {
                        'form': form,
                        'error_message': 'Es wurde kein Student mit diesem Geburtsdatum gefunden.'
                    }
                    return render(request, 'skripten_shop/ausgabe_templates/aktivierung.html', context)
                else:
                    context = {
                        'students': Student.objects.filter(legic_id='').filter(birth_date=birth_date),
                        'birth_date': birth_date,
                    }
                    return render(request, 'skripten_shop/ausgabe_templates/aktivierung.html', context)

        # Wenn Button Speichern gedrückt wurde
        if 'save' in request.POST:
            # User ID auslesen
            user_id = request.POST['optradio']
            student = Student.objects.get(user=user_id)

            # Hashwert der Legic-ID berechnen
            legic_id_hash_value = hashlib.sha256(request.session['current_legic'].encode('utf-8')).hexdigest()

            # Legic-ID als Hashwert speichern
            student.legic_id = legic_id_hash_value

            bezahlt_status = BezahltStatus()
            # Dem Studenten einen BezahltStatus für das aktuelle Semester zuordnen
            bezahlt_status.semester = current_semester_is()
            bezahlt_status.student = student
            # Objekete speichern
            bezahlt_status.save()
            student.save()

            context = {
                'success_message': 'Student wurde aktiviert',
            }

            return render(request, 'skripten_shop/ausgabe_templates/aktivierung.html', context)
    else:
        form = ActivateStudentForm(initial={'legic_id': request.session['current_legic']})

    context = {
        'form': form,
    }

    return render(request, 'skripten_shop/ausgabe_templates/aktivierung.html', context)


@login_required
@user_passes_test(has_permisson_skriptenausgabe)
def reactivation_view(request):
    """
    View zum kassieren des Mitgliedsbeitrags für das laufende Semester
    """
    # Auslesen der Legic-ID aus dem Session Cookie
    legic_id = request.session['current_legic']

    # Hashwert der Legic-ID berechnen
    legic_id_hash_value = hashlib.sha256(legic_id.encode('utf-8')).hexdigest()

    student = Student.objects.get(legic_id=legic_id_hash_value)

    if request.method == 'POST':
        paid = BezahltStatus()
        # Setze Semester des BezahltStatus auf den Wert des aktuellen Semesters (Wert aus Datenbank)
        paid.semester = current_semester_is()
        paid.student = student
        paid.save()

        context = {
            'success_message': 'Bezahlung ist erfolgt'
        }

        return render(request, 'skripten_shop/ausgabe_templates/reaktivierung.html', context)

    context = {
        'student': student
    }

    return render(request, 'skripten_shop/ausgabe_templates/reaktivierung.html', context)


@login_required
@user_passes_test(has_permisson_skriptenausgabe)
def newlegic_view(request):
    """
    View zum aktualisieren der Legic-ID
    """
    if request.method == 'POST':
        form = NewLegicCardForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            new_legic_id = form.cleaned_data.get('new_legic_id')

            try:
                student = Student.objects.get(user__email=email)

                # Hashwert der Legic-ID berechnen
                new_legic_id_hash_value = hashlib.sha256(new_legic_id.encode('utf-8')).hexdigest()

                student.legic_id = new_legic_id_hash_value
                student.save()

                # Legic-ID aus Session Cookie löschen
                del request.session['current_legic']

                context = {
                    'success_message': 'Legic-ID wurde aktualisiert',
                }

                return render(request, 'skripten_shop/ausgabe_templates/newlegic.html', context)

            except Student.DoesNotExist:

                context = {
                    'form': form,
                    'error_message': 'Es wurde kein Student mit dieser Email Adresse gefunden'
                }

                return render(request, 'skripten_shop/ausgabe_templates/newlegic.html', context)

    else:
        form = NewLegicCardForm({'email': '@hm.edu', 'new_legic_id': request.session['current_legic']})

    context = {
        'form': form,
    }

    return render(request, 'skripten_shop/ausgabe_templates/newlegic.html', context)


@method_decorator(login_required, name='dispatch')
class AusgabeView(UserPassesTestMixin, View):

    def test_func(self):
        """
        Prüfen, ob der User die Berechtigung für diese Seite hat
        """
        return self.request.user.groups.filter(name='Skriptenausgabe').exists()

    def dispatch(self, request, *args, **kwargs):
        try:
            self.student = self.get_student(request)
        except Exception:
            # Fehler ins Log schreiben
            logger.error('Legic-ID konnte nich aus dem Session Cookie ausgelesen werden.')

            context = {'error_message': 'Legic-ID konnte nich aus dem Session Cookie ausgelesen werden.'
                                        ' Bitte an den Administrator wenden.'
                       }

            return render(request, 'skripten_shop/ausgabe_templates/ausgabe.html', context)

        # Die Bestellungen des Studenten aus der Datenbank laden
        self.student_order = Order.objects.filter(student=self.student)

        return super(AusgabeView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        context = {
            'student': self.student,
            'student_order': self.student_order,
            'stock_infos': self.get_stock_infos(),
            'max_article': int(max_article_is()),
        }
        return render(request, 'skripten_shop/ausgabe_templates/ausgabe.html', context)

    def post(self, request, *args, **kwargs):
        # Liste der ausgewählten Skripte abrufen
        selected_articels_id = request.POST.getlist('selected_articel[]')

        if "ausgeben" in request.POST:
            if request.POST["ausgeben"] == "Ausgabe starten":
                # Wenn kein Skript ausgewählt wurde, wird die Seite neu geladen
                if len(selected_articels_id) < 1:
                    return redirect(reverse("skripten_shop:ausgabe"))

                # Prüfen, ob mehr Skripte ausgegeben werden sollen als der Student noch erhalten kann
                if len(selected_articels_id) + self.student_order.count() > int(max_article_is()):
                    residue = int(max_article_is()) - self.student_order.count()
                    messages.error(request, "Der Student kann nur noch " + str(residue) + " Skripte erhalten!")
                    return redirect(reverse("skripten_shop:ausgabe"))
                else:
                    # Eigentliche Ausgabe starten
                    articles = []
                    shelf_nums = ""
                    for article_id in selected_articels_id:
                        article = Article.objects.get(pk=article_id)
                        articles.append(article)

                        if article.shelf_number:
                            for x in article.shelf_number.split(","):
                                shelf_nums += (x.strip()) + ","

                    context = {
                        'articles': articles,
                        "shelf_nums": shelf_nums,
                    }

                    return render(request, "skripten_shop/ausgabe_templates/ausgabe_b.html", context)

            elif request.POST["ausgeben"] is "Ausgeben" or "Ausgeben und Nachbestellen":
                # Hier findet die eigentliche Ausgabe statt.
                articel_ids = request.POST.getlist('article[]')

                # Verfügbare Menge eines Skripts in der Datenbank anpassen und dem Studenten die Skripte zuordnen
                for article_id in articel_ids:
                    try:
                        # Ausgewählte Artikel (Skripte) aus Datenbank laden und deren Menge um 1 reduzieren
                        article_in_stock = AritcleInStock.objects.get(article=article_id)
                        article_in_stock.amount -= 1

                        # Dem Studenten die Bestellung bzw. Skripte zuordnen
                        served_article = Order(student=self.student, status=Order.DELIVERD_STATUS)
                        served_article.article = article_in_stock.article

                        # Änderungen in der Datenbank speichern
                        served_article.save()
                        article_in_stock.save()

                        # Bei erfolgreicher Ausgabe, Erfolgsmeldung in Messages speichern
                        # messages.success(request, 'Das Skript %s wurde ausgegeben.' % Article.objects.get(
                        #    pk=article_id).article_number)

                    except IntegrityError:
                        # Bei einem Fehler während er Ausgabe Fehlermeldung in Messages speichern
                        # Ein Fehler tritt z.B. auf, wenn das Objekt "served_article" nicht gespeichert werden kann.
                        # - In diesem Fall hat der Student bereits den jeweiligen Artikel (Skript) erhalten.
                        messages.error(request,
                                       'Das Skript %s kann nicht ausgegeben werden! Der Student hat dieses Skript bereits bestellt.'
                                       % Article.objects.get(pk=article_id).article_number)

                # Evtl. Weiterleitung zur Nachbestellung
                if request.POST["ausgeben"] == "Ausgeben und Nachbestellen":
                    return redirect(reverse("skripten_shop:reorder"))
                else:
                    # Sonst Ausgabe beenden und zurück zur Scan-Legic Seite
                    # Legic-ID aus Session Cookie löschen
                    del request.session['current_legic']

                    return redirect(reverse("skripten_shop:scan-legic"))

    def get_student(self, request):
        try:
            # Legic-ID aus Session Cookie auslesen
            legic_id_hash_value = hashlib.sha256(request.session['current_legic'].encode('utf-8')).hexdigest()
        except Exception:
            raise Exception

        # Objekt Student anhand der Legic_ID aus der Datenbank laden
        student = Student.objects.get(legic_id=legic_id_hash_value)

        return student

    def get_stock_infos(self):
        # Alle bestellbaren Artikel (Skripte) aus der Datenbank laden und nach Artikelnummer sortieren
        articles = Article.objects.filter(active=True).order_by("article_number")
        skripte = Skript.objects.filter(active=True)

        # Menge der Verfügbaren Skripten ermitteln
        stock_infos = []
        for skript in skripte:
            # Falls der Student ein Skript bereits erhalten hat, wird es nicht in der Ausgabe angezeigt
            if self.student_order.filter(article=skript).exists():
                continue

            try:
                # Die Menge der nicht reservierten Skripten im Lager ermitteln
                amount_available = AritcleInStock.objects.get(article=skript).amount
            except AritcleInStock.DoesNotExist:
                # Wenn das Objekt nicht existiert, wird die Menge auf 0 gesetzt
                amount_available = 0

            # Menge der reservierten Skripte im Lager ermitteln
            amount_reserved = Order.objects.filter(status=Order.RESERVED_STATUS).filter(article=skript).count()
            stock_infos.append({
                'skript': skript,
                'amount_available': amount_available,
                'amount_reserved': amount_reserved,
            })

        return stock_infos
