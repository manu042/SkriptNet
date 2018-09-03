# Django Packages
from django.urls import path, re_path

# My Packages
from . import views


app_name = 'skripten_shop'
urlpatterns = [

    # Home URLs
    path('', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('home/', views.HomeView.as_view(), name="home"),
    path('signup/', views.RegistrationView.as_view(), name="signup"),
    # activation_key wird der View als Parameter übergeben
    re_path('signup/confirm/(?P<activation_key>\w+)/$', views.ConfirmationView.as_view(), name="confirm_signup"),
    path('policy/', views.policy_view, name="policy"),
    path('confirm_policy/', views.confirm_policy_view, name="confirm-policy"),

    # Shop Urls
    path('lager/', views.stock_overview, name='lager'),
    # path('shop/', views.skriptenshopview, name='skripten-shop'),
    # path('warenkorb/', views.cartView, name='warenkorb'),
    # path('bestellung/', views.orderView, name='bestellung'),
    # path('ajax/addtocart/', views.addtocart),

    # Ausgabe URLs
    path('scan_legic/', views.scan_legic_view, name='scan-legic'),
    path('ausgabe/', views.AusgabeView.as_view(), name='ausgabe'),
    path('individualbetreuung/', views.individual_assistance_view, name='individualbetreuung'),
    path('aktivierung/', views.activation_view, name='aktivierung'),
    path('reaktivierung/', views.reactivation_view, name='reaktivierung'),
    path('newlegic/', views.newlegic_view, name='newlegic'),

    # Skriptenadmin URLs
    path('lager/reorder/', views.show_reorder_view, name='reorder_overview'),
    path('lager/enter_reorder/', views.enter_reorder_view, name='enter_reorder'),
    path('settings/', views.shop_settings_view, name='shop-settings'),
    path('settings/info_text/', views.edit_info_text_view, name='info-text'),
    path('skriptenadmin/statistics', views.StatisticView.as_view(), name='statistic'),
    path('generate_cover/', views.generate_cover_view, name='generate-cover'),

    # Association URLs
    path('verein/einstellungen/', views.association_settings_view, name='association-settings'),
    path('verein/mitglieder/', views.association_members_view, name='association-members'),
    path('verein/mitglieder_aktiv/', views.active_association_members_view, name='association-members-active'),
    path('verein/sendmail/', views.mail_association_members_view, name='association-mail'),
    path('verein/policy/', views.edit_policy_text_view, name='policy-text'),

    # Admin URLs
    path('admin/logfile/', views.LogfileView.as_view(), name='admin-logfiles'),
]
