# Django Packages
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError

# Third party packages
import hashlib

# My Packages
from skripten_shop.forms import ScanLegicForm, ActivateStudentForm, NewLegicCardForm
from skripten_shop.models import BezahltStatus, Order, Student, BezahltStatus, CurrentSemester, ShopSettings
from skripten_shop.utilities import has_permisson_vorstand_verein


@login_required
@user_passes_test(has_permisson_vorstand_verein)
def association_settings_view(request):
    membership_fee = ShopSettings.objects.get(pk=1).membership_fee

    context = {

    }

    return render(request, 'skripten_shop/association_templates/', context)


@login_required
@user_passes_test(has_permisson_vorstand_verein)
def association_members_view(request):
    current_semester = ShopSettings.objects.get(pk=1)
    paid_objects = BezahltStatus.objects.filter(semester=current_semester)
    students = Student.objects.all()

    context = {
        'students': students,
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
    context = {

    }

    return render(request, 'skripten_shop/association_templates/', context)
