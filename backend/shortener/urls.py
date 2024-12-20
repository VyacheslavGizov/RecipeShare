from django.urls import path

from . import views

app_name = 'shortener'


urlpatterns = [
    path('<str:url_key>', views.RedirectView.as_view(), name='urlpath_change'),
]