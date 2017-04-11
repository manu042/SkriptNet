# Django packages
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.utils import timezone
from django.db.utils import IntegrityError
from django.forms import formset_factory

# My Packages
from skripten_shop.models import AritcleInStock, Article, Order

def stock_overview(request):
    article_in_stock = AritcleInStock.objects.all()

    context = {
        'article_in_stock': article_in_stock,
    }

    return render(request, 'skripten_shop/warehouse_templates/stock_overview.html', context)


def show_reorder_view(request):
    # Following relationships “backward”
    # https://docs.djangoproject.com/en/1.11/topics/db/queries/#following-relationships-backward

    articles = Article.objects.filter(active=True)

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
    print(orders)

    return render(request, 'skripten_shop/warehouse_templates/reorder_overview.html', context)


def enter_reorder_view(request):
    articles = Article.objects.filter(active=True)

    if request.method == 'POST':

        selected_articels_id = request.POST.getlist('selected_articel[]')

        for article_id, amount in zip(selected_articels_id[::2], selected_articels_id[1::2]):
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
