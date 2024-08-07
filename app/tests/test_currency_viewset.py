import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_currency_list(api_client, currency_prices):
    url = reverse("currencies-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.data


@pytest.mark.django_db
def test_currency_detail(api_client, currency_prices):
    currency_eg = currency_prices[0]
    url = reverse("currencies-detail", kwargs={"pk": currency_eg.pk})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == currency_eg.name
    assert response.data["symbol"] == currency_eg.symbol
