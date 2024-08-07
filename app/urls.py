from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .api_views import CurrencyConverterView, CurrencyViewSet, UsernameView

router = DefaultRouter()
# made it currencies to avoid conflict with the existing currency view
router.register(r"currencies", CurrencyViewSet, basename="currencies")

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

urlpatterns += [
    path("api/", include(router.urls)),
    path("api/username/", UsernameView.as_view(), name="username"),
    path("api/convert/", CurrencyConverterView.as_view(), name="converter"),
]
