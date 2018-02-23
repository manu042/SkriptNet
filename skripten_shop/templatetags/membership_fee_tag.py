# Django Packages
from django import template

# My Packages
from skripten_shop.utilities import membership_fee_is

register = template.Library()


@register.simple_tag
def membership_fee():
    return membership_fee_is()
