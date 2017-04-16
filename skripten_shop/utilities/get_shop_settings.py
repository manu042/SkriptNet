from skripten_shop.models import ShopSettings


def current_semester_is():
    return ShopSettings.objects.get(pk=1).current_semester


def membership_fee_is():
    return ShopSettings.objects.get(pk=1).membership_fee


def max_article_is():
    return ShopSettings.objects.get(pk=1).max_article
