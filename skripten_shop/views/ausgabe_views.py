# Django Packages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.utils import timezone

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

    # Fachnummer für Skritpenschrank beleuchtung ermitteln
    shelf_numbers = ""
    reserved_orders = student_order.filter(status=Order.RESERVED_STATUS)
    for reserved_order in reserved_orders:
        # Fachnummern ermitteln
        if reserved_order.article.shelf_number:
            for x in reserved_order.article.shelf_number.split(","):
                shelf_numbers += (x.strip()) + ","

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
        else:
            selected_orders_id = request.POST.getlist('selected_reserved[]')
            for selected_order_id in selected_orders_id:
                order = Order.objects.get(pk=selected_order_id)
                order.status = Order.DELIVERD_STATUS
                order.last_modified_date = timezone.now()
                order.save()

        # Legic-ID aus Session Cookie löschen
        del request.session['current_legic']

        return redirect(reverse('skripten_shop:scan-legic'))

    context = {
        'student': student,
        'student_order': student_order,
        'shelf_numbers': shelf_numbers,
    }

    return render(request, 'skripten_shop/ausgabe_templates/individual_assistance.html', context)


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
            return render(request, 'skripten_shop/ausgabe_templates/ausgabe_a.html', context)

        # Die Bestellungen des Studenten aus der Datenbank laden
        self.student_order = Order.objects.filter(student=self.student)
        return super(AusgabeView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        context = {
            'student': self.student,
            'student_order': self.student_order,
            'stock_infos': self.get_stock_infos(),
            'max_article': int(max_article_is()),
            'rest': int(max_article_is()) - self.student_order.count(),
        }
        return render(request,
                      'skripten_shop/ausgabe_templates/ausgabe_a.html', context)

    def post(self, request, *args, **kwargs):
        # Ausgabe wird gestartet
        if "ausgabe_starten" in request.POST:
            # Liste der ausgewählten Skripte abrufen
            selected_skript_ids = request.POST.getlist('selected_articel[]')

            if len(selected_skript_ids) == 0:
                messages.error(request, "Es wurden keine Skripte für die Ausgabe ausgewählt")
                return redirect(reverse("skripten_shop:ausgabe"))
            else:
                context = self.get_ausgabe_infos(request, selected_skript_ids)
            return render(request,
                          "skripten_shop/ausgabe_templates/ausgabe_b.html", context)

        # Ausgabe durchführen
        elif "ausgeben" in request.POST:
            available_skript_ids = request.POST.getlist('available_skript[]')
            reorder_skript_ids = request.POST.getlist('reorder_skript[]')

            total_checked = len(available_skript_ids) + len(reorder_skript_ids)
            max = int(max_article_is())
            total = total_checked
            rest = max - self.student_order.count()

            # Falls wieder zuviele Skripten ausgewählt wurden
            if total > rest:
                selected_skript_ids = available_skript_ids + reorder_skript_ids
                context = self.get_ausgabe_infos(request, selected_skript_ids)
                return render(request, "skripten_shop/ausgabe_templates/ausgabe_b.html", context)

            # Wenn nichts ausgewählt wurde
            elif total_checked == 0:
                selected_skript_ids = available_skript_ids + reorder_skript_ids
                messages.error(request, "Es wurden keine Skripte für die Ausgabe ausgewählt")
                logger.info("Bei der Ausgabe wurden keine Skripte ausgeweahlt.")
                return redirect(reverse("skripten_shop:scan-legic"))

            # Wenn alles passt, Ausgabe abschließen
            else:
                self.proceed_ausgabe(request, available_skript_ids, reorder_skript_ids)
                # Legic-ID aus Session Cookie löschen
                try:
                    del request.session['current_legic']
                except:
                    pass
                return render(request, "skripten_shop/ausgabe_templates/ausgabe_c.html")

        # Skript von Ausgabe zu Nachbestellung verschieben
        elif "move_to_reorder" in request.POST:
            available_skript_ids = request.POST.getlist('available_skript[]')
            reorder_skript_ids = request.POST.getlist('reorder_skript[]')
            skript_to_move = str(request.POST.get("move_to_reorder"))
            context = self.move_to_reorder(request, available_skript_ids, reorder_skript_ids, skript_to_move)
            return render(request, "skripten_shop/ausgabe_templates/ausgabe_b.html", context)
        else:
            return redirect(reverse("skripten_shop:scan-legic"))

    def proceed_ausgabe(self, request, available_skript_ids, reorder_skript_ids):

        # Skripten ausgeben
        for id in available_skript_ids:
            try:
                skript = Skript.objects.get(pk=id)
                article_in_stock = AritcleInStock.objects.get(article=skript)
                article_in_stock.amount -= 1

                # Dem Studenten die Bestellung bzw. Skripte zuordnen
                order = Order(student=self.student, status=Order.DELIVERD_STATUS)
                order.article = skript

                # Änderungen in der Datenbank speichern
                article_in_stock.save()
                order.save()
                messages.success(request, "Das Skript %s wurde erfolgreich ausgegeben." % skript.article_number)
            except Exception as e:
                messages.error(request,
                               "Das Skript %s kann nicht ausgegeben werden. Der Student hat dieses Skript bereits in seiner Bestellhistorie." % skript.article_number)

        # Skripten nachbestellen
        for id in reorder_skript_ids:
            try:
                skript = Skript.objects.get(pk=id)
                order = Order(article=skript, student=self.student)
                order.save()
                messages.success(request, "Das Skript %s wurde erfolgreich bestellt." % skript.article_number)
            except Exception as e:
                messages.error(request,
                               "Das Skript %s kann nicht bestellt werden. Der Student hat dieses Skript bereits in seiner Bestellhistorie." % skript.article_number)

    def get_ausgabe_infos(self, request, selected_skript_ids):
        skripte_available = []
        skripte_to_reorder = []
        shelf_numbers = ""

        for id in selected_skript_ids:
            skript = Skript.objects.get(pk=id)

            try:
                # Verfügbare Menge im Lager ermitteln
                amount_available = skript.aritcleinstock.amount
            except:
                amount_available = 0

            # Skript ist nicht mehr vorhanden
            if amount_available < 1:
                skripte_to_reorder.append(skript)
            else:
                # Skript ist noch vorhanden
                skripte_available.append(skript)
                # Fachnummern ermitteln
                if skript.shelf_number:
                    for x in skript.shelf_number.split(","):
                        shelf_numbers += (x.strip()) + ","

        # Prüfen, wie viele Skripte der Student noch erhalten kann
        checked = True
        max = int(max_article_is())
        total = len(selected_skript_ids) + self.student_order.count()
        rest = max - self.student_order.count()
        if total > max:
            checked = False
            messages.error(request, "Der Student kann nur noch %s Skript(e) erhalten" % rest)

        context = {
            "skripte_available": skripte_available,
            "skripte_to_reorder": skripte_to_reorder,
            "shelf_numbers": shelf_numbers,
            "checked": checked,
            "student": self.student,
        }
        return context

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

    def move_to_reorder(self, request, available_skript_ids, reorder_skript_ids, skript_to_move):
        """
        Falls ein Skript doch nicht verfügbar ist, wird es mit dieser Funktion
        zur Nachbestellung verschieben
        """
        if skript_to_move in available_skript_ids:
            available_skript_ids.remove(skript_to_move)

        if skript_to_move not in reorder_skript_ids:
            reorder_skript_ids.append(skript_to_move)

        skripte_available = []
        skripte_to_reorder = []
        shelf_numbers = ""

        for id in available_skript_ids:
            skript = Skript.objects.get(pk=id)
            skripte_available.append(skript)
            # Fachnummern ermitteln
            if skript.shelf_number:
                for x in skript.shelf_number.split(","):
                    shelf_numbers += (x.strip()) + ","

        for id in reorder_skript_ids:
            skript = Skript.objects.get(pk=id)
            skripte_to_reorder.append(skript)

        # Prüfen, wie viele Skripte der Student noch erhalten kann
        checked = True
        max = int(max_article_is())
        total = len(skripte_available) + len(skripte_available) + self.student_order.count()
        rest = max - self.student_order.count()
        if total > max:
            checked = False
            messages.error(request, "Der Student kann nur noch %s Skript(e) erhalten" % rest)

        context = {
            "skripte_available": skripte_available,
            "skripte_to_reorder": skripte_to_reorder,
            "shelf_numbers": shelf_numbers,
            "checked": checked,
            "student": self.student,
        }
        return context
