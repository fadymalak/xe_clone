import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_currency_converter_valid(api_client, currency_prices):
    currency_eg, currency_us, _ = currency_prices
    url = reverse("converter")
    data = {
        "from_currency": currency_eg.symbol,
        "to_currency": currency_us.symbol,
        "amount": 10,
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "converted_amount" in response.data
    assert response.data["converted_amount"] == 485.0


@pytest.mark.django_db
def test_currency_converter_invalid_currency(api_client):
    url = reverse("converter")
    data = {
        "from_currency": "uuu",
        "to_currency": "EGP",
        "amount": 100,
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data
    assert response.data["error"] == "Unknown currency symbol"


@pytest.mark.django_db
def test_currency_converter_missing_field(api_client):
    url = reverse("converter")
    data = {
        "from_currency": "EGP",
        "amount": 100,
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "to_currency" in response.data
    assert response.data["to_currency"][0] == "This field is required."


@pytest.mark.django_db
def test_currency_converter_validation_error1(api_client):
    url = reverse("converter")
    data = {
        "from_currency": "<h1>",
        "amount": 100,
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_currency_converter_validation_error2(api_client):
    url = reverse("converter")
    data = {
        "from_currency": "!!!",
        "amount": 100,
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
