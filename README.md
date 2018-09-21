# SkriptNet
* SkriptNet ist eine Webapplikation zur Ausgabe, Bestellung und Verwaltung von Skripten
* SkriptNet wurde mit dem Web Framework Django und Python 3 entwickelt

# Installation
* Folgt noch

# Entwicklungsumgebung einrichten
1. Aktuelle Projekt Dateien downloaden
```shell
$ git clone https://github.com/manu042/SkriptNet.git
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
    Für Python Projekte ist es sinnvoll, eine Virtual Envivroment einzurichten. Eine Anleitung dazu findet man
    [hier](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

4. SQLite Datenbank anlegen
```shell
$ python manage.py makemigrations
$ python manage.py migrate
```
5. Fixtures laden

    ```shell
    python manage.py loaddata groups.yaml
    python manage.py loaddata settings.yaml
    python manage.py loaddata study_groups.yaml
    python manage.py loaddata user.yaml
    python manage.py loaddata professor.yaml
    python manage.py loaddata article.yaml
    python manage.py loaddata skripte.yaml
    ```

weitere Infos dazu in der fixtures_help.md


6. Admin User erstellen

    ```shell
    $ python manage.py createsuperuser
    ```
    Damit sich der User auf der Startseite von SkriptNet anmelden kann, sollte der Username wie eine Email-Adresse aufgebaut sein
    
    [DAS STANDARD PASSWORT FÜR DEN ADMIN WÄHRE MAL INTERESSANT AN DIESER STELLE]

7. Development Server starten
    
    Um änderungen im Browser testen zu können, kann Lokal ein Development Server gestartet werden
    ```shell
    $ python manage.py runserver
    ```
    Die Webseite kann dann über die URL **http://127.0.0.1:8000/** aufgerufen werden

# Neue Version auf Server starten 
Um den Server auf den Stand des Git-Repos
zu aktualisieren müssen folgende Schritte durchgeführt werden.
1. Snapshot erstellen

2. Aktuelle Version des SkriptNets ins Home Verzeichnis holen.\
   Dazu, falls noch nicht geschehen, zuerst das Git-Repo hinzufügen:
   ```
   ~$ git clone https://github.com/manu042/SkriptNet.git
   ```
   Sonst nur die Dateien auf aktuelle Version aktualisieren:
   ```
   ~$ git fetch                         # Get latest version from Github
   ~$ git clean -f                      # Clear working directory
   ~$ git reset --hard origin/master    # Reset files to remote master
   ```
3. Neue und geänderte Dateien aus Home-Verzeichnis in Server-Verzeichnis kopieren:
   ```
   $ cd /var/www/html/SkriptNet/
   $ sudo cp -r ~/SkriptNet/SomeFolder/SourceFile ./SomeFolder/
   ```
   Statische Dateien müssen in das Verzeichnis ```X``` kopiert werden:
   ``` 
   $ sudo cp -r todo wohin?             # Statische Dateien kopieren
   $ python3 manage.py collectstatic    # Änderungen dem Server mitteilen
   ```
4. Benutzer der Gruppe ```www-data``` hinzufügen
   ```
   $ sudo usermod -a -G www-data myusername   # Neu einloggen um Änderung zu übernehmen 
   ```

   Für neue und geänderte Dateien den Benutzer und die Gruppe auf ```www-data``` ändern:
   ```
   $ sudo chown -R www-data:www-data ./SomeFolderOrFile
   ```
5. Bei Änderungen von Feldern in der Datenbank:
   ``` 
   $ python3 manage.py makemigrations
   $ python3 manage.py migrate
   ```
6. Services neu starten:
   ```
   $ sudo systemctl restart gunicorn 
   $ sudo systemctl restart nginx
   ```


# Projekt Struktur
* [Google Drive](https://drive.google.com/drive/folders/0BwRnCXKlxFwISnRRLUVGQkRUQ2c)

# Quellen
* [Django documentation](https://docs.djangoproject.com/en/dev/)
* [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
* [Code Style](http://docs.python-guide.org/en/latest/writing/style/)
* [Django Code Style](https://docs.djangoproject.com/en/1.10/internals/contributing/writing-code/coding-style/)
