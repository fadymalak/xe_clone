import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_converter_view_valid_currency(client, currency_prices):
    currency_eg, currency_us, _ = currency_prices
    url = reverse("convert")
    data = {
        "from_currency": currency_us.symbol,
        "to_currency": currency_eg.symbol,
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


@pytest.mark.django_db
def test_converter_view_post_form_validation1(client):
    url = reverse("convert")
    data = {"from_currency": "<h>", "to_currency": "EGP", "amount": 100}
    response = client.post(url, data)

    assert response.context['form'].errors['from_currency'] == ["Invalid input: HTML tags are not allowed."]


@pytest.mark.django_db
def test_converter_view_post_form_validation2(client):
    url = reverse("convert")
    data = {"from_currency": "!!!", "to_currency": "EGP", "amount": 100}
    response = client.post(url, data)

    assert response.context['form'].errors['from_currency'] == [
        "Invalid input: Only alphabetic characters are allowed."
    ]
