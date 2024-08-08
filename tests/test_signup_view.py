import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models.user import user 
User = get_user_model()

@pytest.mark.django_db
def test_signup_view(api_client):
    url = reverse('signup')
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': '123456',
        'preferred_currency': 'EGP',
        'iban': '123456789'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 302  
    assert User.objects.filter(email='test@example.com').exists()


@pytest.mark.django_db
def test_signup_view_invalid_data(api_client):
    url = reverse('signup')
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword',
        'preferred_currency': 'USD' # incorrect currency
        # Missing 'iban' field
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 400
    assert not User.objects.filter(email='test@example.com').exists()
