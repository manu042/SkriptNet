# Django packages
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.utils import timezone
from django.db.utils import IntegrityError

# My Packages
from skripten_shop.models import AritcleInStock, ArticleToOrder


def stock_overview(request):
    article_in_stock = AritcleInStock.objects.all()

    context = {
        'article_in_stock': article_in_stock,
    }

    return render(request, 'skripten_shop/warehouse_templates/stock_overview.html', context)
