# https://docs.djangoproject.com/en/dev/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test


def has_permisson_admin(user):
    return user.groups.filter(name='Admin').exists()


def has_permisson_skriptenadmin(user):
    return user.groups.filter(name='Skriptenadmin').exists()


def has_permisson_skriptenausgabe(user):
    return user.groups.filter(name='Skriptenausgabe').exists()


def has_permisson_vorstand_verein(user):
    return user.groups.filter(name='Vorstand Verein').exists()


def has_permisson_aktives_vereinsmitglied(user):
    return user.groups.filter(name='Vereinsmitglieder').exists()
