from django.conf.urls import url

from . import views

app_name = 'skripten_shop'
urlpatterns = [

    # Home URLs
    url(r'^$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^home/$', views.HomeView.as_view(), name='home'),
    url(r'^register/$', views.registration_view, name='register'),
    url(r'^register/confirm/(?P<activation_key>.+)$', views.confirm_mail_view, name='register_confirm'),

    # Ausgabe Urls
    url(r'^scan_legic/$', views.scan_legic_view, name='scan-legic'),
    url(r'^ausgabe/$', views.ausgabe_view, name='ausgabe'),
    url(r'^individualbetreuung/$', views.individual_assistance_view, name='individualbetreuung'),
    url(r'^reorder/$', views.reorder_view, name='reorder'),
    url(r'^aktivierung/$', views.activation_view, name='aktivierung'),
    url(r'^reaktivierung/$', views.reactivation_view, name='reaktivierung'),
    url(r'^newlegic/$', views.newlegic_view, name='newlegic'),

    # Settings URLs
    url(r'^settings/$', views.shop_settings_view, name='shop-settings'),
    url(r'^settings/info_text/$', views.edit_info_text_view, name='info-text'),

    # Warehouse URLs
    url(r'^lager/$', views.stock_overview, name='lager'),
    url(r'^lager/reorder/$', views.show_reorder_view, name='reorder_overview'),
    url(r'^lager/enter_reorder/$', views.enter_reorder_view, name='enter_reorder'),

    # TODO: anpassen
    # Association URLs
    url(r'^verein/einstellungen/$', views.association_settings_view, name='association-settings'),
    url(r'^verein/mitglieder/$', views.association_members_view, name='association-members'),
    url(r'^verein/mitglieder_aktiv/$', views.active_association_members_view, name='association-members-active'),
    url(r'^verein/sendmail/$', views.mail_association_members_view, name='association-mail'),

    # Admin URLs
    url(r'^admin/logfile/$', views.show_logfile_view, name='admin-logfiles'),

]
