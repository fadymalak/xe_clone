from unittest.mock import Mock, patch

import pytest
from django.urls import reverse


@pytest.mark.skip
@patch("app.views.requests.get")
def test_converter_view_success(mock_requests_get, client):
    mock_response = Mock()
    mock_response.json.return_value = {"to": [{"mid": 48.5}]}
    mock_response.status_code = 200
    mock_requests_get.return_value = mock_response
    data = {"from_currency": "USD", "to_currency": "EGP", "amount": 100}
    url = reverse("convert")
    response = client.post(url, data)

    assert "context" in response.context
    assert response.context["context"]["res"] == 4850


@pytest.mark.skip
@patch("app.views.requests.get")
def test_converter_view_fail_1(mock_requests_get, client):
    mock_response = Mock()
    mock_response.json.return_value = {"to": []}
    mock_response.status_code = 200
    mock_requests_get.return_value = mock_response

    data = {"from_currency": "USD", "to_currency": "EEE", "amount": 1}

    url = reverse("convert")
    response = client.post(url, data)

    assert "context" in response.context
    assert response.context["context"]["res"] == "Invalid currency code"


@pytest.mark.skip
@patch("app.views.requests.get")
def test_converter_view_fail_2(mock_requests_get, client):
    mock_response = Mock()
    mock_response.status_code = 400
    mock_requests_get.return_value = mock_response
    data = {"from_currency": "UUU", "to_currency": "EEE", "amount": 1}

    url = reverse("convert")
    response = client.post(url, data)

    assert "context" in response.context
    assert response.context["context"]["res"] == "Invalid currency code"
