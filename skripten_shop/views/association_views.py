"""
In diesem Modul befinden sich alle Views, die für den Verein relevant sind.
"""
# Django Packages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

# My Packages
from skripten_shop.models import Student, BezahltStatus, ShopSettings
from skripten_shop.utilities import has_permisson_vorstand_verein
from skripten_shop.forms import SendAssociationMailForm, AssociationSettingsForm


@login_required
@user_passes_test(has_permisson_vorstand_verein)
def association_settings_view(request):
    try:
        shop_settings = ShopSettings.objects.get(pk=1)
    except:
        shop_settings = None

    if request.method == 'POST':

        form = AssociationSettingsForm(request.POST)

        if form.is_valid():
            shop_settings.membership_fee = form.cleaned_data.get('membership_fee')
            shop_settings.save()
    else:
        form = AssociationSettingsForm(instance=shop_settings)

    context = {
        'form': form,
    }

    return render(request, 'skripten_shop/association_templates/association_settings.html', context)


@login_required
@user_passes_test(has_permisson_vorstand_verein)
def association_members_view(request):
    try:
        current_semester = ShopSettings.objects.get(pk=1)
    except:
        current_semester = None

    total_paid = BezahltStatus.objects.filter(semester=current_semester.current_semester).count()
    students = Student.objects.all()
    total_income = total_paid * current_semester.membership_fee

    context = {
        'students': students,
        'total_paid': total_paid,
        'total_income': total_income,
    }

    return render(request, 'skripten_shop/association_templates/association_members.html', context)


@login_required
@user_passes_test(has_permisson_vorstand_verein)
def active_association_members_view(request):
    active_members = User.objects.filter(groups__name='aktive Vereinsmitglieder')

    context = {
        'active_members': active_members,

    }

    return render(request, 'skripten_shop/association_templates/active_association_members.html', context)


@login_required
@user_passes_test(has_permisson_vorstand_verein)
def mail_association_members_view(request):
    if request.method == 'POST':

        form = SendAssociationMailForm(request.POST)

        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            mail_text = form.cleaned_data.get('mail_text')
            # TODO: send mail
    else:
        form = SendAssociationMailForm()

    context = {
        'form': form,
    }

    return render(request, 'skripten_shop/association_templates/mail_association_members.html', context)
