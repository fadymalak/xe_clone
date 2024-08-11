import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_currency_list_view(client, currency_prices):
    url = reverse("currency-list")
    response = client.get(url)

    assert response.status_code == 200
    assert "currencies" in response.context
    assert len(response.context["currencies"]) == 2


@pytest.mark.django_db
def test_currency_detail_view(client, currency_prices):
    currency, _, __ = currency_prices
    url = reverse("currency-detail", args=[currency.id])
    response = client.get(url)

    assert response.status_code == 200
    assert "currency" in response.context
    assert response.context["currency"].id == currency.id
