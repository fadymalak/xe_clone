from django.urls import path

from . import views

urlpatterns = [
    path("convert/", views.ConverterView.as_view(), name="convert"),
    path(
        "display-username/",
        views.DisplayUsernameView.as_view(),
        name="display-username",
    ),
    path("currencies/", views.CurrencyListView.as_view(), name="currency-list"),
    path(
        "currencies/<int:pk>/",
        views.CurrencyDetailView.as_view(),
        name="currency-detail",
    ),
]
