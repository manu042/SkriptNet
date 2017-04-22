# SkriptNet
* SkriptNet ist eine Webapplikation zur Ausgabe, Bestellung und Verwaltung von Skripten
* SkriptNet wurde mit dem Web Framework Django und Python 3 entwickelt

# Installation
* Folgt noch

# Entwicklungsumgebung einrichten
1. Aktuelle Projekt Dateien downloaden
```shell
$ git clone https://git.fs04.de/root/SkriptNet.git
```

2. Branch wechseln (z.B. Develop oder fcome_fserved ) oder neu anlegen

    Wichtig!!! In der Branch **Master** wird nicht entwickelt
    ```shell
    $ git checkout develop
    ```
3. Python Pakete installieren

    Die benötigten Python Pakete findet man in der Datei requirements.txt
    ```shell
    $ pip install -r requirements.txt
    ```
    Für Python Projekte ist es sinnvoll, eine Virutal Envivroment einzurichten. Eine Anleitung dazu findet man
    [hier](http://docs.python-guide.org/en/latest/dev/virtualenvs/). (Zum Entwickeln wurde Pyton 3.6)

4. SQLite Datenbank anlegen
```shell
$ python manage.py makemigrations
$ python manage.py migrate
```

5. Admin User erstellen

    ```shell
    $ python manage.py createsuperuser
    ```
    Damit sich der User auf der Startseite von SkriptNet anmelden kann, sollte der Username wie eine Email-Adresse aufgebaut sein

6. Development Server starten
    
    Um änderungen im Browser testen zu können, kann Lokal ein Development Server gestartet werden
    ```shell
    $ python manage.py createsuperuser
    ```
    Die Webseite kann dann über die URL **http://127.0.0.1:8000/** aufgerufen werden



# Projekt Struktur
* [Google Drive](https://drive.google.com/drive/folders/0BwRnCXKlxFwISnRRLUVGQkRUQ2c)

# Quellen
* [Django documentation](https://docs.djangoproject.com/en/dev/)
* [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
* [Code Style](http://docs.python-guide.org/en/latest/writing/style/)
* [Django Code Style](https://docs.djangoproject.com/en/1.10/internals/contributing/writing-code/coding-style/)