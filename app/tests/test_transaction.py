from django.test import TestCase

# Create your tests here.
import pytest
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from app.forms import SignUpForm
from app.models.user import user as user_info
from app.forms import LoginForm
from app.models.transaction import Transaction
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from datetime import datetime

@pytest.fixture
def user_data():
    return {'email': 'shahd@paymob.com', 'password': 'user123'}

@pytest.fixture
def user(db):
    User = get_user_model()
    user = User.objects.create_user(username='testuser', email='shahd@paymob.com', password='user123')
    user_info.objects.create(user = user, preferred_currency = 'EGP', iban ='123456', otp = '0000') 
    return user

@pytest.fixture
def transactions(user):
    Transaction.objects.create(user=user, amount=100, type = 'Debit', success=True)
    Transaction.objects.create(user=user, amount=200, type = 'Debit', success=True)
    return Transaction.objects.filter(user=user)

@pytest.mark.django_db
def test_login_form_valid_data(user_data):
    form = LoginForm(data=user_data)
    assert form.is_valid()
    assert form.cleaned_data['email'] == 'shahd@paymob.com'
    assert form.cleaned_data['password'] == 'user123'

@pytest.mark.django_db
def test_login_form_empty_input():
    form = LoginForm(data={})
    assert not form.is_valid()
    assert 'email' in form.errors
    assert 'password' in form.errors


@pytest.mark.django_db
def test_transaction_history(user, transactions):
    client = APIClient()
    client.force_authenticate(user)

    response = client.get(reverse('api-transaction-history'))
    
    assert response.status_code == 200

    response_ids = [transaction['id'] for transaction in response.data]
    expected_ids = [transaction.id for transaction in transactions]

    assert sorted(response_ids) == sorted(expected_ids), f"Expected IDs: {expected_ids}, but got: {response_ids}"


@pytest.mark.django_db
def test_reset_password(user):
    client = APIClient()
    client.force_authenticate(user)
    # import pdb
    # pdb.set_trace()
    user_data = user_info.objects.filter(user = user).get()
    user_data.otp = '0000'
    user_data.save()
    reset_data = {
        'email': user.email,
        'otp': '0000',
        'new_password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }
    
    response = client.post(reverse('api-reset-password'), reset_data)
    # import pdb
    # pdb.set_trace()
    assert response.status_code == 200
    assert response.data['success'] == 'Password has been reset successfully'
    
    user.refresh_from_db()
    assert user_data.otp == '0000'
    
    assert user.check_password('newpassword123')

# @pytest.mark.django_db
# def test_signup_form_valid_data(user_data):
#     form = SignUpForm(data=user_data)
#     assert form.is_valid()
#     user = form.save()
#     assert User.objects.filter(email='shahd@paymob.com').exists()
#     assert user.email == 'shahd@paymob.com'

# @pytest.mark.django_db
# def test_signup_form_email_already_exists(user_data):
#     User.objects.create(email='shahd@paymob.com', password='oldpassword')
#     form = SignUpForm(data=user_data)
#     assert not form.is_valid()
#     with pytest.raises(IntegrityError):
#         form.save()

# @pytest.mark.django_db
# def test_signup_form_save_commit_false(user_data):
#     form = SignUpForm(data=user_data)
#     if form.is_valid():
#         user = form.save(commit=False)
#     assert not User.objects.filter(email='shahd@paymob.com').exists()
#     assert user.email == 'shahd@paymob.com'


