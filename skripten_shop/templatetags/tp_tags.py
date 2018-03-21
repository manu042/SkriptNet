# Django Packages
from django import template
from django.contrib.auth.models import Group

# My Packages
from skripten_shop.utilities import membership_fee_is
from skripten_shop.models import BezahltStatus, ShopSettings

register = template.Library()


@register.filter(name="has_paid")
def check_paid_status(student):
    """
    Checken, ob der Student dieses Semester bezahlt hat
    """
    try:
        current_semester = ShopSettings.objects.get(pk=1).current_semester
        bs = BezahltStatus.objects.filter(student=student).latest("date")

        if bs.semester == current_semester:
            paid = True
        else:
            paid = False
    except Exception as e:
        paid = False
    return paid


@register.simple_tag
def membership_fee():
    return membership_fee_is()


@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Prüft, ob User sich in einer bestimmten Gruppe befindet.
    Damit wird geregelt, welche Elemente dem User in der Navbar angezeigt werden.
    """
    try:
        group = Group.objects.get(name=group_name)
        return True if group in user.groups.all() else False
    except:
        return False