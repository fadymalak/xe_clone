import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models.user import user 
from app.models.transfer import Transfer

User = get_user_model()

@pytest.fixture
def authenticated_client(api_client, create_user):
    user = create_user(email='from_user@example.com', username='from_user', password='123456', balance=1000)
    api_client.force_authenticate(user=user.user)
    return api_client

@pytest.mark.django_db
def test_send_money_view(authenticated_client, create_user):
    from_user = user.objects.get(user__email='from_user@example.com')
    to_user = create_user(email='to_user@example.com', username='to_user', password='123456', balance=500)

    url = reverse('send-money')
    data = {
        'to_user_username': 'to_user',
        'amount': 100
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == 200
    from_user.refresh_from_db()
    to_user.refresh_from_db()
    assert from_user.balance == 900
    assert to_user.balance == 600
    assert Transfer.objects.filter(from_user=from_user, to_user=to_user, amount=100).exists()

@pytest.mark.django_db
def test_send_money_view_insufficient_balance(authenticated_client, create_user):
    from_user = user.objects.get(user__email='from_user@example.com')
    to_user = create_user(email='to_user@example.com', username='to_user', password='123456', balance=500)

    url = reverse('send-money')
    data = {
        'to_user_username': 'to_user',
        'amount': 1500  
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == 400
    from_user.refresh_from_db()
    to_user.refresh_from_db()
    assert from_user.balance == 1000 
    assert to_user.balance == 500  
