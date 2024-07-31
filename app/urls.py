from django.urls import path

from . import views

urlpatterns = [
    path("convert/", views.ConverterView.as_view(), name="convert"),
]
