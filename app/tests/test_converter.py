import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_converter_view_valid_currency(client, currency_prices):
    currency_eg, currency_us, _ = currency_prices
    url = reverse("convert")
    data = {
        "from_currency": currency_eg.symbol,
        "to_currency": currency_us.symbol,
        "amount": 10,
    }
    response = client.post(url, data)
    assert response.status_code == 200
    assert "context" in response.context
    assert "res" in response.context["context"]
    assert response.context["context"]["res"] == 485.0


@pytest.mark.django_db
def test_converter_view_post_invalid_currency(client):
    url = reverse("convert")
    data = {"from_currency": "uty", "to_currency": "EGP", "amount": 100}
    response = client.post(url, data)

    assert "context" in response.context
    assert "error" in response.context["context"]
    assert response.context["context"]["error"] == "Unknown currency symbol"
