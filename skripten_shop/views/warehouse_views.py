# Django packages
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.utils import IntegrityError
from django.forms import formset_factory

# My Packages
from skripten_shop.models import AritcleInStock, Article, Order
from skripten_shop.utilities import has_permisson_skriptenadmin


@login_required
@user_passes_test(has_permisson_skriptenadmin)
def stock_overview(request):
    articles = Article.objects.filter(active=True).order_by("article_number")

    stock_infos = []
    for article in articles:
        try:
            amount_available = AritcleInStock.objects.get(article=article).amount
        except AritcleInStock.DoesNotExist:
            amount_available = 0
        amount_reserved = Order.objects.filter(status=Order.RESERVED_STATUS).filter(article=article).count()
        stock_infos.append({
            'article': article,
            'amount_available': amount_available,
            'amount_reserved': amount_reserved,
        })

    context = {
        'stock_infos': stock_infos,
    }

    return render(request, 'skripten_shop/warehouse_templates/stock_overview.html', context)


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

    return render(request, 'skripten_shop/warehouse_templates/reorder_overview.html', context)


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

    return render(request, 'skripten_shop/warehouse_templates/enter_reorder.html', context)
