from skripten_shop.models import ShopSettings


def current_semester_is():
    """
    Aktuelles Semester ermitteln
    """
    return ShopSettings.objects.get(pk=1).current_semester


def membership_fee_is():
    """
    Mitgliedsbeitrag aus der Datenbank abrufen
    """
    return ShopSettings.objects.get(pk=1).membership_fee


def max_article_is():
    """
    Wert max. bestellbare Skripten, die ein Student pro Semester erhalten darf ermitteln
    """
    return ShopSettings.objects.get(pk=1).max_article
