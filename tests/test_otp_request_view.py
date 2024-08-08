import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models.user import user

User = get_user_model()

@pytest.mark.django_db
def test_otp_request_view(api_client, create_user):
    user = create_user(email='test@example.com', username='testuser', password='testpassword')
    url = reverse('forget-password')
    data = {'email': 'test@example.com'}
    response = api_client.post(url, data, format='json')
    assert response.status_code == 200
    user.refresh_from_db()

