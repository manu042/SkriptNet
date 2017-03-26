from django.conf.urls import url, include

from . import views

app_name = 'skripten_shop'
urlpatterns = [

    # Home Urls
    url(r'^$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^home/$', views.HomeView.as_view(), name='home'),
    url(r'^register/$', views.registration_view, name='register'),
    url(r'^register/confirm/(?P<activation_key>.+)$', views.confirm_mail_view, name='register_confirm'),

    # Shop Urls
    url(r'^shop/$', views.skriptenshopview, name='skripten-list'),
    url(r'^warenkorb/$', views.cartView, name='warenkorb'),
    url(r'^bestellung/$', views.orderView, name='bestellung'),
    url(r'ajax/addtocart/$', views.addtocart),

    # Ausgabe Urls
    url(r'^ausgabe/$', views.ausgabeview, name='ausgabe'),
    url(r'^aktivierung/$', views.aktivierungsview, name='aktivierung'),
    url(r'^reaktivierung/$', views.reaktivierungsview, name='reaktivierung'),
    url(r'^newlegic/$', views.newlegicview, name='newlegic'),

    # Settings Urls
    url(r'^settings/$', views.shop_settings, name='shop-settings'),
]
