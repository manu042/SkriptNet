# Django packages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test


# My packages
from skripten_shop.models import ShopSettings, Order, Skript, BezahltStatus, Student
from skripten_shop.forms import SettingsForm, InfoTextForm
from skripten_shop.utilities import has_permisson_skriptenadmin, current_semester_is
from skripten_shop.utilities import get_current_semester, SendStatusMailThread
from skripten_shop.utilities import current_semester_is, max_article_is


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

        total_deliverd= Order.objects.filter(status=Order.DELIVERD_STATUS).count()
        total_students = BezahltStatus.objects.filter(semester=current_semester_is()).count()

        context = {"data": data,
                   "total_deliverd": total_deliverd,
                   "total_customers": total_customers,
                   "ordered_max": ordered_max,}

        return context
