# Django Packages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse

# My Packages
from skripten_shop.forms import ScanLegicForm, ActivateStudentForm, NewLegicCardForm
from skripten_shop.models import Student, BezahltStatus
from skripten_shop.models import CurrentSemester
from skripten_shop.models import ArticleInOrder


@login_required
def ausgabeview(request):
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
                # Liefert Student mit zugehöriger Legic ID zurück
                student = Student.objects.get(legic_id=legic_id)

                # Holt sich den letzeten BezahltStatus des Studenten und das aktuelle Semester
                last_semester_paid = BezahltStatus.objects.filter(student=student).latest('date')
                current_semester = CurrentSemester.objects.get(pk=1).current_semester

                # Prüft ob der Student in diesem Semester bereits bezahlt hat
                # Falls nicht wird die Ausgabe weitergeleitet zur reaktivierungsview
                if not last_semester_paid.semester == current_semester:
                    return redirect(reverse('skripten_shop:aktivierung'))
                else:
                    try:
                        # TODO Ausgabe überdenken

                        articles = ArticleInOrder.objects.filter(customer=student.user)

                        context = {
                            'articles': articles,
                        }

                    except ArticleInOrder.DoesNotExist:

                        context = {
                            'error_message': 'Es existieren keine offenen Bestellungen',
                        }

                    return render(request, 'skripten_shop/ausgabe_templates/ausgabe.html', context)

            # Falls kein Student mit dieser Legic-ID gefunden wurde
            except Student.DoesNotExist:
                return redirect(reverse('skripten_shop:aktivierung'))

    # Die Seite wird mit der Request Methode Get aufgerufen
    else:
        form = ScanLegicForm()

    context = {
        'form': form
    }

    return render(request, 'skripten_shop/ausgabe_templates/ausgabe.html', context)


@login_required
def aktivierungsview(request):
    """
    View zum Aktivieren eines Studenten, d.h. die Legic ID wird mit einem Account verknüpft
    """
    current_semester = CurrentSemester.objects.get(pk=1)

    if request.method == 'POST':
        form = ActivateStudentForm(request.POST)
        print(request.POST)

        # Wenn Button Suchen gedrückt wurde
        if 'search' in request.POST:

            if form.is_valid():
                birth_date = form.cleaned_data.get('birth_date')
                legic_id = form.cleaned_data.get('legic_id')

                # Die Legic ID wird im Session Cookie gespeichert
                request.session['current_legic'] = legic_id

                # Es werden all Studenten mit dem Geburtsdatum gefiltert und die Anzahl zurückgeliefert
                quantity = Student.objects.filter(birth_date=birth_date).count()

                if quantity < 1:
                    pass
                    context = {
                        'form': form,
                        'search': True,
                        'error_message': 'Es wurde kein Student mit diesem Geburtsdatum gefunden.'
                    }
                    return render(request, 'skripten_shop/ausgabe_templates/aktivierung.html', context)
                else:
                    context = {
                        'students': Student.objects.filter(birth_date=birth_date),
                    }
                    return render(request, 'skripten_shop/ausgabe_templates/aktivierung.html', context)

        # Wenn Button Speichern gedrückt wurde
        if 'save' in request.POST:
            # User ID auslesen
            user_id = request.POST['optradio']
            student = Student.objects.get(user=user_id)
            # Dem Studenten die Legic-ID aus dem Session Cookie zuordnen
            student.legic_id = request.session['current_legic']

            # Das akutelle Semester aus der Datenbank auslesen
            current_semester = CurrentSemester.objects.get(pk=1)
            bezahlt_status = BezahltStatus()
            # Dem Studenten einen BezahltStatus für das aktuelle Semester zuordnen
            bezahlt_status.semester = current_semester.current_semester
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
def reaktivierungsview(request):
    """
    View zum kassieren des Mitgliedsbeitrags für das laufende Semester
    """
    # Auslesen der Legic-ID aus dem Session Cookie
    legic_id = request.session['current_legic']

    student = Student.objects.get(legic_id=legic_id)

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
def newlegicview(request):
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
                student.legic_id = new_legic_id
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
        form = NewLegicCardForm()

    context = {
        'form': form,
    }

    return render(request, 'skripten_shop/ausgabe_templates/newlegic.html', context)
