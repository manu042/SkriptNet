# Django Packages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError

# Third party packages
import hashlib

# My Packages
from skripten_shop.forms import ScanLegicForm, ActivateStudentForm, NewLegicCardForm
from skripten_shop.models import Article, Order, Student, BezahltStatus, CurrentSemester, AritcleInStock
from skripten_shop.utilities import has_permisson_skriptenausgabe
from skripten_shop.utilities import ShopSettingsObject


# TODO: legic id aus session löschen (an geeigneter stelle)

@login_required
@user_passes_test(has_permisson_skriptenausgabe)
def scan_legic_view(request):
    """
    View für Skripten Ausgabe, zeigt beim Aufrufen eine Form zur Eingabe der Ledic ID
    """
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

                # Holt sich den letzeten BezahltStatus des Studenten und das aktuelle Semester
                last_semester_paid = BezahltStatus.objects.filter(student=student).latest('date')
                current_semester = CurrentSemester.objects.get(pk=1).current_semester

                # Prüft ob der Student in diesem Semester bereits bezahlt hat
                # Falls nicht wird die Ausgabe weitergeleitet zur reaktivierungsview
                if not last_semester_paid.semester == current_semester:
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
def ausgabe_view(request):
    # Hashwert der Legic-ID berechnen
    legic_id_hash_value = hashlib.sha256(request.session['current_legic'].encode('utf-8')).hexdigest()
    student = Student.objects.get(legic_id=legic_id_hash_value)
    student_order = Order.objects.filter(student=student)

    if request.method == 'POST':

        selected_articels_id = request.POST.getlist('selected_articel[]')

        for selected_articel_id in selected_articels_id:
            try:
                article_in_stock = AritcleInStock.objects.get(pk=selected_articel_id)
                article_in_stock.amount -= 1

                served_article = Order(student=student, status=Order.DELIVERD_STATUS)
                served_article.article = article_in_stock.article
                served_article.save()
                article_in_stock.save()

            except IntegrityError:
                messages.error(request, 'Das Skript %s kann nicht ausgegeben werden!' % Article.objects.get(
                    pk=selected_articel_id).article_number)

        if messages:
            return redirect(reverse('skripten_shop:ausgabe'))

        return redirect(reverse('skripten_shop:scan-legic'))

    # Requst method Get
    articles = Article.objects.filter(active=True)

    stock_infos = []
    for article in articles:

        try:
            amount_available = AritcleInStock.objects.get(article=article).amount
        except AritcleInStock.DoesNotExist:
            amount_available = 0

        amount_reserved = Order.objects.filter(status=Order.RESERVED_STATUS).filter(article=article).count()
        stock_infos.append({
            'article': article,
            'amount_available': amount_available,
            'amount_reserved': amount_reserved,
        })

    context = {
        'student': student,
        'student_order': student_order,
        'stock_infos': stock_infos,
    }

    return render(request, 'skripten_shop/ausgabe_templates/ausgabe.html', context)


@login_required
@user_passes_test(has_permisson_skriptenausgabe)
def individual_assistance_view(request):
    # Hashwert der Legic-ID berechnen
    legic_id_hash_value = hashlib.sha256(request.session['current_legic'].encode('utf-8')).hexdigest()
    student = Student.objects.get(legic_id=legic_id_hash_value)
    student_order = Order.objects.filter(student=student)

    if request.method == 'POST':

        selected_orders_id = request.POST.getlist('selected_reserved[]')

        for selected_order_id in selected_orders_id:
            order = Order.objects.get(pk=selected_order_id)
            order.status = Order.DELIVERD_STATUS
            order.save()

    student_order = Order.objects.filter(student=student)

    context = {
        'student': student,
        'student_order': student_order,
    }

    return render(request, 'skripten_shop/ausgabe_templates/individual_assistance.html', context)


@login_required
@user_passes_test(has_permisson_skriptenausgabe)
def reorder_view(request):
    # Hashwert der Legic-ID berechnen
    legic_id_hash_value = hashlib.sha256(request.session['current_legic'].encode('utf-8')).hexdigest()
    student = Student.objects.get(legic_id=legic_id_hash_value)

    if request.method == 'POST':

        selected_articels_id = request.POST.getlist('selected_articel[]')

        for selected_articel_id in selected_articels_id:
            try:
                article = Article.objects.get(pk=selected_articel_id)
                order = Order(article=article, student=student)
                order.save()
            except IntegrityError:
                messages.error(request, 'Das Skript %s kann nicht bestellt werden!' % Article.objects.get(
                    pk=selected_articel_id).article_number)

    articles = Article.objects.filter(active=True)

    context = {
        'student': student,
        'articles': articles,
    }

    return render(request, 'skripten_shop/ausgabe_templates/reorder.html', context)


@login_required
@user_passes_test(has_permisson_skriptenausgabe)
def aktivierungs_view(request):
    """
    View zum Aktivieren eines Studenten, d.h. die Legic ID wird mit einem Account verknüpft
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

                # Es werden all Studenten mit dem Geburtsdatum gefiltert und die Anzahl zurückgeliefert
                quantity = Student.objects.filter(legic_id='').filter(birth_date=birth_date).count()

                if quantity < 1:

                    context = {
                        'form': form,
                        'search': True,
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
            bezahlt_status.semester = ShopSettingsObject.current_semester_is()
            bezahlt_status.paid = True
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
        'search': True,
    }

    return render(request, 'skripten_shop/ausgabe_templates/aktivierung.html', context)


@login_required
@user_passes_test(has_permisson_skriptenausgabe)
def reaktivierungs_view(request):
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
        paid.semester = CurrentSemester.objects.get(pk=1).current_semester
        paid.paid = True
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
