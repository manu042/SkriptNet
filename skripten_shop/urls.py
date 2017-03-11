from django.conf.urls import url, include

from . import views

app_name = 'skripten_shop'
urlpatterns = [
    url(r'^$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^home/$', views.HomeView.as_view(), name='home'),
    url(r'^registrierung/$', views.registration_view, name='registrierung'),
]