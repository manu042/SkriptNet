# Django packages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings

# My packages
from skripten_shop.models import ShopSettings, Order, Skript, BezahltStatus, Student
from skripten_shop.forms import SettingsForm, InfoTextForm
from skripten_shop.utilities import has_permisson_skriptenadmin
from skripten_shop.utilities import get_current_semester, SendStatusMailThread
from skripten_shop.utilities import current_semester_is, max_article_is

from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import subprocess


@login_required
@user_passes_test(has_permisson_skriptenadmin)
def shop_settings_view(request):
    try:
        # Lade Shopsettings aus der Datenbank
        shop_settings = ShopSettings.objects.get(pk=1)
    except:
        # Falls das Objekt (noch) nicht existiert, lege ein neues an
        shop_settings = ShopSettings.objects.create(pk=1, current_semester="WS 13/14", state=False, max_article=8,
                                                    days_reserved=14, membership_fee=3, info_text="Skriptenshop FS04")
        # Objekt speichern
        shop_settings.save()

    form = SettingsForm(instance=shop_settings)

    if request.method == 'POST':
        if 'start_new_semester' in request.POST:
            # Todo: Funktion überarbeiten
            shop_settings.current_semester = get_current_semester()
            shop_settings.save()

        if 'save_settings' in request.POST:
            form = SettingsForm(request.POST)

            if form.is_valid():
                shop_settings.state = form.cleaned_data.get('state')
                shop_settings.max_article = form.cleaned_data.get('max_article')
                shop_settings.days_reserved = form.cleaned_data.get('days_reserved')
                shop_settings.save()
                return redirect(reverse('skripten_shop:shop-settings'))

    context = {
        'current_semester': current_semester_is,
        'info_text': shop_settings.info_text,
        'form': form,
    }

    return render(request, 'skripten_shop/skriptenadmin/settings.html', context)


@login_required
@user_passes_test(has_permisson_skriptenadmin)
def edit_info_text_view(request):
    shop_settings = ShopSettings.objects.get(pk=1)

    if request.method == 'POST':

        form = InfoTextForm(request.POST)

        if form.is_valid():
            shop_settings.info_text = form.cleaned_data.get(('info_text'))
            shop_settings.save()
            return redirect(reverse('skripten_shop:shop-settings'))
    else:
        form = InfoTextForm(instance=shop_settings)

    context = {
        'form': form,
    }

    return render(request,
                  'skripten_shop/skriptenadmin/edit_info_text.html', context)


@login_required
@user_passes_test(has_permisson_skriptenadmin)
def show_reorder_view(request):
    # Following relationships “backward”
    # https://docs.djangoproject.com/en/1.11/topics/db/queries/#following-relationships-backward
    skripte = Skript.objects.filter(active=True)

    if request.method == 'POST':
        if 'print_order' in request.POST:
            orders = Order.objects.filter(status=Order.REQUEST_STATUS)

            # Bestellung speichern, um sie erneut anzuzeigen
            skripte_dict = {}
            for skript in skripte:
                amount = orders.filter(article=skript).count()
                skripte_dict[skript.article_number] = [skript.name, amount]

            # Status auf "im Druck ändern"
            for order in orders:
                order.status = Order.PRINT_STATUS
                order.last_modified_date = timezone.now()
                order.save()

            # Zu bestellende Skripten nochmal anzeigen
            return render(request, 'skripten_shop/skriptenadmin/reorder_overview.html', {'skripte_dict': skripte_dict})

    orders = []
    for skript in skripte:
        order = Order.objects.filter(article=skript).filter(status=Order.REQUEST_STATUS)

        if order.count() > 0:
            orders.append({
                'skript': skript,
                'order_amount': order.count()
            })
    context = {
        'orders': orders,
        'total': Order.objects.filter(status=Order.REQUEST_STATUS).count()
    }

    return render(request, 'skripten_shop/skriptenadmin/reorder_overview.html', context)


@login_required
@user_passes_test(has_permisson_skriptenadmin)
def enter_reorder_view(request):
    skripte = Skript.objects.filter(active=True)

    if request.method == 'POST':
        selected_articels_id = request.POST.getlist('selected_articel[]')

        for article_id, amount in zip(selected_articels_id[::2], selected_articels_id[1::2]):
            if amount == '':
                amount = 0
            orders = Order.objects.filter(status=Order.PRINT_STATUS).filter(article=article_id).order_by(
                "last_modified_date")[:int(amount):]
            for order in orders:
                order.status = Order.RESERVED_STATUS
                order.last_modified_date = timezone.now()
                order.save()

        # Lieferbenachrichtigung an Studenten versenden
        SendStatusMailThread()

    orders_in_print = []
    for skript in skripte:
        order = Order.objects.filter(article=skript).filter(status=Order.PRINT_STATUS)

        if order.count() > 0:
            orders_in_print.append({
                'skript': skript,
                'order_amount': order.count()
            })

    context = {
        'orders_in_print': orders_in_print,
        'total': Order.objects.filter(status=Order.PRINT_STATUS).count()
    }
    return render(request, 'skripten_shop/skriptenadmin/enter_reorder.html', context)


@method_decorator(login_required, name='dispatch')
class StatisticView(UserPassesTestMixin, TemplateView):
    """
    Startseite des Skripten-Shops (Nach dem Login)
    """
    template_name = 'skripten_shop/skriptenadmin/statistic.html'

    def test_func(self):
        """
        Prüfen, ob der User die Berechtigung für diese Seite hat
        """
        return self.request.user.groups.filter(name='Skriptenadmin').exists()

    def get_context_data(self, **kwargs):
        context = super(StatisticView, self).get_context_data(**kwargs)

        students = Student.objects.all()
        total_customers = 0
        ordered_max = 0
        # Ermittle wie viel Studenten min. 1 Skript abgeholt haben
        # und wie viele die Gesamtmenge abgeholt haben
        for student in students:
            student_order = Order.objects.filter(student=student)
            if student_order.count() > 0:
                total_customers += 1
            if student_order.count() >= int(max_article_is()):
                ordered_max += 1

        skripte = Skript.objects.filter(active=True)

        data = []
        for skript in skripte:
            orders = Order.objects.filter(article=skript).filter(status=Order.DELIVERD_STATUS)
            if orders.count() > 0:
                data.append([skript, orders.count()])

        total_deliverd = Order.objects.filter(status=Order.DELIVERD_STATUS).count()
        total_students = BezahltStatus.objects.filter(semester=current_semester_is()).count()

        context = {"data": data,
                   "total_deliverd": total_deliverd,
                   "total_customers": total_customers,
                   "ordered_max": ordered_max, }

        return context


@login_required
@user_passes_test(has_permisson_skriptenadmin)
def generate_skript_view(request):
    if request.method == 'POST':
        if request.POST.get('upload_cover') is not None:  # uploading new template
            if "file_cover" in request.FILES:
                fs = FileSystemStorage()
                fs.delete(SkriptGenerator.template_path)
                myfile = request.FILES['file_cover']
                fs.save(SkriptGenerator.template_path, myfile)
        if request.POST.get('upload_skript') is not None:  # uploading skript
            if "file_skript" in request.FILES:
                selected_skript = request.POST.get('dropdown')
                skript = Skript.objects.get(article_number=selected_skript)
                skript_path = SkriptGenerator.skript_dir + "SkriptFile_" + skript.article_number + ".pdf"
                fs = FileSystemStorage()
                fs.delete(skript_path)
                myfile = request.FILES['file_skript']
                fs.save(skript_path, myfile)
        if request.POST.get('generate_cover') is not None:  # generating single cover
            selected_skript = request.POST.get('dropdown')
            skript = Skript.objects.filter(article_number=selected_skript)[0]
            pdf_filename = SkriptGenerator.generate_cover(skript)
            pdf = open(SkriptGenerator.cover_dir + pdf_filename, 'rb')
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=' + pdf_filename;
            return response
        if request.POST.get('generate_skript') is not None:  # generating single skript
            selected_skript = request.POST.get('dropdown')
            skript = Skript.objects.filter(article_number=selected_skript)[0]
            pdf_filename = SkriptGenerator.generate_skript(skript)

            if pdf_filename == -1:
                skript_list = Skript.objects.all()
                context = {
                    'skript_list': skript_list,
                    'exists': FileSystemStorage.exists(SkriptGenerator.template_path),
                    'error_text': "Fehler beim Generieren von Skript " + skript.article_number
                                  + ". Drucke Skript als PDF und lade die neu Datei hoch",
                }
                return render(request, "skripten_shop/skriptenadmin/skript_generator_view.html", context)
            elif pdf_filename == None:
                skript_list = Skript.objects.all()
                context = {
                    'skript_list': skript_list,
                    'exists': FileSystemStorage().exists(SkriptGenerator.template_path),
                    'error_text': "Keine Skript-Datei zu " + skript.article_number
                                  + ". Lade eine Skript-Datei hoch",
                }
                return render(request, "skripten_shop/skriptenadmin/skript_generator_view.html", context)
            else:
                pdf = open(SkriptGenerator.finish_dir + pdf_filename, 'rb')
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=' + pdf_filename;
                return response
        if request.POST.get('generate_skripts') is not None:  # generating all skripts
            skript = SkriptGenerator.generate_all_skripts()
            if skript == None:
                zipfile = open(SkriptGenerator.finish_dir + "skripte.zip", 'rb')
                response = HttpResponse(zipfile.read(), content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename=skripte.zip';
                return response
            else:
                skript_list = Skript.objects.all()
                context = {
                    'skript_list': skript_list,
                    'exists': FileSystemStorage().exists(SkriptGenerator.template_path),
                    'error_text': "Fehler beim Generieren von Skript " + skript.article_number
                                  + ". Drucke Skript als PDF und lade die neu Datei hoch",
                }
            return render(request, "skripten_shop/skriptenadmin/skript_generator_view.html", context)

    # if no response returned in POST return GET
    skript_list = Skript.objects.all()
    context = {
        'skript_list': skript_list,
        'exists': FileSystemStorage().exists(SkriptGenerator.template_path),
    }
    return render(request, "skripten_shop/skriptenadmin/skript_generator_view.html", context)


class SkriptGenerator:
    static_dir = "."+settings.MEDIA_URL+"skripte/"
    cover_dir = static_dir + "cover/"
    skript_dir = static_dir + "skript/"
    finish_dir = static_dir + "finish/"

    template_path = static_dir + "VorlageDeckblatt_leer.pdf"

    @staticmethod
    def generate_cover(skript):
        # from http://allfont.de/download/comic-sans-ms-bold/ (not for commercial use)
        pdfmetrics.registerFont(TTFont('Comic', SkriptGenerator.static_dir + 'comic-sans-ms.ttf'))
        pdfmetrics.registerFont(TTFont('Comic bold', SkriptGenerator.static_dir + 'comic-sans-ms-bold.ttf'))
        packet = io.BytesIO()
        text1 = skript.name
        text2 = ""
        # splitting title appropriately
        pos = text1.find(':')
        if pos >= 20:  # split line after :
            text1 = skript.name[0:pos + 1]
            text2 = skript.name[pos + 1:].strip()
        elif len(text1) > 40:  # split line longer than 40 chars
            tokens = text1.split()
            text1 = ""
            text2 = ""
            for token in tokens:
                if len(text1) > 30:
                    text2 = text2 + " " + token
                else:
                    text1 = text1 + " " + token
        default_font = "Comic bold"
        id1 = {
            "text": skript.article_number,
            "font": default_font,
            "size": 28,
            "x-pos": 147 * mm,
            "y-pos": 262 * mm,
        }
        id2 = {
            "text": id1["text"],
            "font": default_font,
            "size": 28,
            "x-pos": 147 * mm,
            "y-pos": 34 * mm,
        }
        title = {
            "text": text1,
            "font": default_font,
            "size": 18,
            "x-pos": 34 * mm,
            "y-pos": 209 * mm,
        }
        title2 = {
            "text": text2,
            "font": title["font"],
            "size": title["size"],
            "x-pos": title["x-pos"],
            "y-pos": 201 * mm,
        }
        arrow = {
            "text": ">>",
            "font": title["font"],
            "size": title["size"],
            "x-pos": 23 * mm,
            "y-pos": title["y-pos"],
        }
        author = {
            "text": skript.author.last_name + ", " + skript.author.title + " " + skript.author.first_name,
            "font": "Comic",
            "size": 16,
            "x-pos": 34 * mm,
            "y-pos": 166 * mm,
        }
        insertions = [id1, id2, arrow, title, title2, author]
        can = canvas.Canvas(packet, pagesize=letter)
        for insert in insertions:
            can.setFont(insert["font"], insert["size"])
            can.drawString(insert["x-pos"], insert["y-pos"], insert["text"])
        can.save()
        # move to the beginning of the StringIO buffer
        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        # read PDF template
        existing_pdf = PdfFileReader(open(SkriptGenerator.template_path, "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page = new_pdf.getPage(0)
        page.mergePage(existing_pdf.getPage(0))
        output.addPage(page)
        # appending the following pages of cover template
        for i in range(1, existing_pdf.getNumPages()):
            output.addPage(existing_pdf.getPage(i))
        # finally, write "output" to a real file
        outputStream = open(SkriptGenerator.cover_dir + "Deckblatt_" + skript.article_number + ".pdf", "wb")
        output.write(outputStream)
        outputStream.close()
        return "Deckblatt_" + skript.article_number + ".pdf"

    @staticmethod
    def generate_skript(skript):  # appending skript file to cover
        # (re-)generate cover
        SkriptGenerator.generate_cover(skript)

        cover_path = SkriptGenerator.cover_dir + "Deckblatt_" + skript.article_number + ".pdf"
        skript_path = SkriptGenerator.skript_dir + "SkriptFile_" + skript.article_number + ".pdf"
        finish_path = SkriptGenerator.finish_dir + "Skript_" + skript.article_number + ".pdf"

        # remove old skript file
        FileSystemStorage().delete(finish_path)

        if not FileSystemStorage().exists(skript_path):  # no file available, abort
            return

        try:
            merger = PdfFileMerger()
            merger.append(PdfFileReader(open(cover_path, 'rb')))
            merger.append(PdfFileReader(open(skript_path, 'rb')))
            output_stream = open(finish_path, 'wb')
            merger.write(output_stream)
            output_stream.close()
        except:
            return -1  # error creating the skript

        return "Skript_" + skript.article_number + ".pdf"

    @staticmethod
    def generate_all_skripts():
        skripts = Skript.objects.all()

        for skript in skripts:
            if SkriptGenerator.generate_skript(skript) == -1:  # return skript whose generation failed
                return skript

        # pack skripts to zip file
        p = subprocess.Popen(
            "zip -FS -r " + SkriptGenerator.finish_dir + "skripte " + SkriptGenerator.finish_dir + "Skript*.pdf",
            stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
