import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from app.models.user import user 

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(email, username, password, preferred_currency='USD', iban='123456789', balance=1000):
        user_default = User.objects.create_user(email=email, username=username, password=password)
        custom_user = user.objects.create(user=user_default, preferred_currency=preferred_currency, iban=iban, balance=balance)
        return custom_user
    return _create_user
