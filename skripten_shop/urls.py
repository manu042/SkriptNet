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

    # TODO: shop entfernen
    # Shop Urls
    # url(r'^shop/$', views.skriptenshopview, name='skripten-list'),
    # url(r'^warenkorb/$', views.cartView, name='warenkorb'),
    # url(r'^bestellung/$', views.orderView, name='bestellung'),
    # url(r'^ajax/addtocart/$', views.addtocart),

    # Ausgabe Urls
    url(r'^scan_legic/$', views.scan_legic_view, name='scan-legic'),
    url(r'^ausgabe/$', views.ausgabe_view, name='ausgabe'),
    url(r'^individualbetreuung/$', views.individual_assistance_view, name='individualbetreuung'),
    url(r'^reorder/$', views.reorder_view, name='reorder'),
    url(r'^aktivierung/$', views.activation_view, name='aktivierung'),
    url(r'^reaktivierung/$', views.reactivation_view, name='reaktivierung'),
    url(r'^newlegic/$', views.newlegic_view, name='newlegic'),

    # Settings Urls
    url(r'^settings/$', views.shop_settings_view, name='shop-settings'),

    # Warehouse Urls
    url(r'^lager/$', views.stock_overview, name='lager'),
    url(r'^lager/reorder/$', views.show_reorder_view, name='reorder_overview'),
    url(r'^lager/enter_reorder/$', views.enter_reorder_view, name='enter_reorder'),

    # TODO: anpassen
    # Association Urls
    url(r'^verein/einstellungen/$', views.show_reorder_view, name='association-settings'),
    url(r'^verein/mitglieder/$', views.show_reorder_view, name='association-members'),
    url(r'^verein/mitglieder_aktiv/$', views.show_reorder_view, name='association-members-active'),
    url(r'^verein/sendmail/$', views.show_reorder_view, name='association-mail'),

]
