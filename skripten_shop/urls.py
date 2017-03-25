from django.conf.urls import url, include

from . import views

app_name = 'skripten_shop'
urlpatterns = [
    url(r'^$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^home/$', views.HomeView.as_view(), name='home'),
    url(r'^register/$', views.registration_view, name='register'),
    url(r'^register/confirm/(?P<activation_key>.+)$', views.confirm_mail_view, name='register_confirm')
]