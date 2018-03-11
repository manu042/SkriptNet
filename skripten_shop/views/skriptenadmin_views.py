# Django packages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import View, TemplateView


# My packages
from skripten_shop.models import ShopSettings, Article, Order, Skript, SkriptInStock
from skripten_shop.forms import SettingsForm, InfoTextForm
from skripten_shop.utilities import has_permisson_skriptenadmin, current_semester_is
from skripten_shop.utilities import get_current_semester


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

    return render(request, 'skripten_shop/settings_templates/settings.html', context)


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

    return render(request, 'skripten_shop/settings_templates/edit_info_text.html', context)


@login_required
@user_passes_test(has_permisson_skriptenadmin)
def show_reorder_view(request):
    # Following relationships “backward”
    # https://docs.djangoproject.com/en/1.11/topics/db/queries/#following-relationships-backward

    articles = Article.objects.filter(active=True).order_by("article_number")

    if request.method == 'POST':
        if 'print_order' in request.POST:

            orders = Order.objects.filter(status=Order.REQUEST_STATUS)
            orders.status = Order.PRINT_STATUS

            for order in orders:
                order.status = Order.PRINT_STATUS
                order.save()

    orders = []
    for article in articles:
        order = Order.objects.filter(article=article).filter(status=Order.REQUEST_STATUS)
        orders.append({
            'article': article,
            'order_amount': order.count()
        })

    context = {
        'orders': orders,
    }

    return render(request,
                  'skripten_shop/skriptenadmin/reorder_overview.html', context)


@login_required
@user_passes_test(has_permisson_skriptenadmin)
def enter_reorder_view(request):
    articles = Article.objects.filter(active=True).order_by("article_number")

    if request.method == 'POST':

        selected_articels_id = request.POST.getlist('selected_articel[]')

        for article_id, amount in zip(selected_articels_id[::2], selected_articels_id[1::2]):
            if amount == '':
                amount = 0
            orders = Order.objects.filter(status=Order.PRINT_STATUS).filter(article=article_id).order_by(
                "last_modified_date")[:int(amount):]
            for order in orders:
                order.status = Order.RESERVED_STATUS
                order.save()

    orders_in_print = []
    for article in articles:
        order = Order.objects.filter(article=article).filter(status=Order.PRINT_STATUS)
        orders_in_print.append({
            'article': article,
            'order_amount': order.count()
        })

    context = {
        'orders_in_print': orders_in_print,
    }

    return render(request,
                  'skripten_shop/skriptenadmin/enter_reorder.html', context)


class InitiateStockView(UserPassesTestMixin, TemplateView):
    """
    Lager erstmalig im Semester anlegen

    Todo: View deaktivieren, wenn Shop offen ist.
    """
    template_name = "skripten_shop/skriptenadmin/initiate_stock.html"

    def test_func(self):
        """
        Prüfen, ob der User die Berechtigung für diese Seite hat
        """
        return self.request.user.groups.filter(name='Skriptenadmin').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["articles"] = Article.objects.filter(active=True)
        return context

    def post(self, request, *args, **kwargs):
        selected_articels_id = request.POST.getlist('selected_articel[]')

        for article_id, amount in zip(selected_articels_id[::2], selected_articels_id[1::2]):
            if amount is not "0":
                for x in range(int(amount)):
                    SkriptInStock.objects.create(skript=Skript.objects.get(pk=article_id))

        return super().get(request, *args, **kwargs)


class StudentOrderView(UserPassesTestMixin, TemplateView):
    """
    Bestellungen der Studenten anzeigen und an Druckdienstleister übergeben
    """
    template_name = "skripten_shop/skriptenadmin/student_orders.html"

    def test_func(self):
        """
        Prüfen, ob der User die Berechtigung für diese Seite hat
        """
        return self.request.user.groups.filter(name='Skriptenadmin').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        orders = []
        articles = Article.objects.filter(active=True)
        for article in articles:
            orders.append({
                "article": article,
                "amount_orders": Order.objects.filter(article=article, status=Order.REQUEST_STATUS).count()
            })
        context["orders"] = orders
        return context

    def post(self, request, *args, **kwargs):
        orders = Order.objects.filter(status=Order.REQUEST_STATUS)

        for order in orders:
            order.status = Order.PRINT_STATUS
            order.save()

        return super().get(request, *args, **kwargs)


class StockOverview(UserPassesTestMixin, TemplateView):
    """
    View zeigt das aktuelle Lager an, mit freien und reservierten Skripten
    """
    template_name = ""

    def test_func(self):
        """
        Prüfen, ob der User die Berechtigung für diese Seite hat
        """
        return self.request.user.groups.filter(name='Skriptenadmin').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
