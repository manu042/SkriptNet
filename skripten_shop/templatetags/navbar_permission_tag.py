# Django Packages
from django import template
from django.contrib.auth.models import Group

register = template.Library()


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
