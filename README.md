# SkriptNet
* SkriptNet ist eine Webapplikation zur Ausgabe, Bestellung und Verwaltung von Skripten
* SkriptNet wurde mit dem Web Framework Django und Python 3 entwickelt

# Installation
* Folgt noch

# Entwicklungsumgebung einrichten
1. [Virtual Environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) mit Pyton 3.6 einrichten
2. Python Pakete installieren 
    * siehe requirements.txt
3. Dieses Git Repository clonen
4. Befehl ```python manage.py makemigrations``` ausführen
5. Befehl ```python manage.py migrate``` ausführen
6. Server schneller starten: [Optional] 
    * oben rechts auf ```Edit Configurations...```
        * oben links auf ```+```, dann in der Liste (Add New Configuration) auf ```Django server```
        * als Name z. B. ```start_server```
        * Bei Environment Variables auf ```...``` und unter ```DJANGO_SETTINGS_MODULE``` in Value ```SkriptNet.settings``` eintragen
    * In den Einstellungen (```Str``` + ```Alt``` + ```S```) unter ```Language & Frameworks``` -> ```Django``` ...
        * Haken bei  ```Enable Django Support``` setzen
        * Django project root: ```...\PycharmProjects\SkriptNet```
        * Settings: ```SkriptNet\settings.py```
        * Manage script:  ```manage.py```

# Quellen
* [Django documentation](https://docs.djangoproject.com/en/dev/)
* [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
* [Code Style](http://docs.python-guide.org/en/latest/writing/style/)
* [Django Code Style](https://docs.djangoproject.com/en/1.10/internals/contributing/writing-code/coding-style/)