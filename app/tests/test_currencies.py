import pytest
from django.urls import reverse

from app.models import Currency, CurrencyPrice


@pytest.mark.django_db
def test_currency_list_view(client):
    Currency.objects.create(name="US Dollar", symbol="USD")
    Currency.objects.create(name="Egyptian Pound", symbol="EGP")
    url = reverse("currency-list")
    response = client.get(url)

    assert response.status_code == 200
    assert "currencies" in response.context
    assert len(response.context["currencies"]) == 2


@pytest.mark.django_db
def test_currency_detail_view(client):
    currency = Currency.objects.create(name="Egyptian Pound", symbol="EGP")
    CurrencyPrice.objects.create(currency=currency, current_price=48.5)
    url = reverse("currency-detail", args=[currency.id])
    response = client.get(url)

    assert response.status_code == 200
    assert "currency" in response.context
    assert response.context["currency"].id == currency.id
    assert response.context["current_price"].current_price == 48.5
