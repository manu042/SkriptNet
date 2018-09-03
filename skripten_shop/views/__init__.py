from .admin_views import LogfileView
from .ausgabe_views import scan_legic_view, individual_assistance_view, activation_view, reactivation_view, newlegic_view, AusgabeView
from .home_views import HomeView, LoginView, LogoutView, RegistrationView, ConfirmationView, policy_view, confirm_policy_view
from .skriptenadmin_views import shop_settings_view, edit_info_text_view, enter_reorder_view, show_reorder_view, StatisticView, generate_cover_view
from .shop_views import skriptenshopview, addtocart, cartView, orderView, stock_overview
from .association_views import *

__all__ = ['scan_legic_view', 'individual_assistance_view', 'activation_view',
           'reactivation_view', 'newlegic_view',

            "HomeView", "LoginView", "LogoutView", "RegistrationView", "ConfirmationView",

           'HomeView', 'shop_settings_view', 'skriptenshopview', 'addtocart', 'cartView', 'orderView', 'stock_overview',
           'show_reorder_view', 'enter_reorder_view',
           'LogfileView']
