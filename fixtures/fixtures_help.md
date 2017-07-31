# https://docs.djangoproject.com/en/1.10/howto/initial-data/
# Bsp: Datenbank in fixture Datei kopieren:
# python3 manage.py dumpdata auth.Group --format=yaml > fixtures/groups.yaml
# !!! Vorher über Django Admin Objekte in der Datenbank erstellen
# Mit dem Befehl
# python manage.py loaddata groups.yaml
# werden die Daten in die Datenbank geladen

* python3 manage.py loaddata groups.yaml
* python3 manage.py loaddata settings.yaml
* python3 manage.py loaddata study_groups.yaml
* python3 manage.py loaddata user.yaml
* python3 manage.py loaddata professor.yaml
* python3 manage.py loaddata article.yaml
* python3 manage.py loaddata skripte.yaml