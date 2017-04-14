# Django Packages
from django import template

# My Packages
from skripten_shop.utilities import ShopSettingsObject

register = template.Library()


@register.simple_tag
def membership_fee():
    return ShopSettingsObject.membership_fee_is()
