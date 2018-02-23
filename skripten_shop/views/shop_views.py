# Django packages
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.utils import IntegrityError


# My packages
from skripten_shop.models import Article, ArticleInCart, Order, AritcleInStock


@login_required
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
def skriptenshopview(request):
    """
    View zur Darstellung des Shops
    """
    articles = Article.objects.all()

    context = {
        'articles': articles,
    }

    return render(request, 'skripten_shop/shop_templates/skripten_list.html', context)


@login_required
def addtocart(request):
    """
    Hilfsfunktion, wird mittels ajax geladen
    """
    # User der den Request angeforder hat
    student = request.user

    # Ajax übergibt die ID des Artikels
    artikle_id = request.POST.get('artikel_id')

    # Falls der Artikel in der Datenbank nicht existiert, wird 404 zurückgegeben
    article = get_object_or_404(Article, pk=artikle_id)

    if request.method == 'POST':
        if Order.objects.filter(student=student, article=article):
            context = {
                "artikle_nr2": article.article_number
            }
            return render(request, 'skripten_shop/shop_templates/error_message.html', context)

        else:
            try:
                articleincart = ArticleInCart()
                articleincart.customer = student
                articleincart.article = article
                articleincart.save()
            except IntegrityError:
                # Falls sich der Artikel bereits im Warenkorb befindet wird eine Error Message mit der Artikel Nummer zurückgebeben
                article_nr = article.article_number
                context = {
                    'aritkel_nr': article_nr
                }
                return render(request, 'skripten_shop/shop_templates/error_message.html', context)

    return HttpResponse()


@login_required
def cartView(request):
    """
    Diese View stellt den Warenkorb eines Studenten dar
    """

    customer = request.user
    articles = ArticleInCart.objects.filter(customer=customer)

    if not articles:
        articles = False

    if request.method == 'POST':
        if 'bestellen' in request.POST:
            articles_in_cart = ArticleInCart.objects.filter(customer=customer)
            for article_in_cart in articles_in_cart:
                article_in_order = Order()
                article_in_order.student = article_in_cart.customer
                article_in_order.article = article_in_cart.article
                article_in_order.status = "to_order"
                article_in_order.save()
                article_in_cart.delete()

            context = {
                'bestellt': True
            }

            return render(request, 'skripten_shop/shop_templates/warenkorb.html', context)

        if 'delete' in request.POST:
            pk = request.POST['delete']
            article_in_cart = ArticleInCart.objects.get(pk=pk)
            article_in_cart.delete()

            articles = ArticleInCart.objects.filter(customer=customer)

            if not articles:
                articles = False

            context = {
                'articles': articles
            }

            return render(request, 'skripten_shop/shop_templates/warenkorb.html', context)

    context = {
        'articles': articles
    }

    return render(request, 'skripten_shop/shop_templates/warenkorb.html', context)


@login_required
def orderView(request):
    """
    Diese View stellt die Bestellung eines Studenten dar
    """

    student = request.user
    articles = Order.objects.filter(student=student)

    if not articles:
        articles = False

    context = {
        'articles': articles,
    }
    return render(request, 'skripten_shop/shop_templates/order_list.html', context)
