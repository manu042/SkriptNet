# Django Packages
from django import template
from django.contrib.auth.models import Group

# My Packages
from skripten_shop.utilities import get_current_semester, membership_fee_is

register = template.Library()


@register.simple_tag
def current_semester():
    return get_current_semester()


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