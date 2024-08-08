from django.test import TestCase

# Create your tests here.
import pytest
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from app.forms import SignUpForm
from app.models.user import User
from app.forms import LoginForm
from app.models.transaction import Transaction
from django.urls import reverse
from django.contrib.auth import get_user_model


@pytest.fixture
def user_data():
    return {'email': 'shahd@paymob.com', 'password': 'user123'}

@pytest.fixture
def user(db):
    User = get_user_model()
    user = User.objects.create_user(username='testuser', email='shahd@paymob.com', password='user123')
    return user

@pytest.fixture
def transactions(user):
    Transaction.objects.create(user=user, amount=100, type = 'Debit', success=True)
    Transaction.objects.create(user=user, amount=200, type = 'Debit', success=True)
    return Transaction.objects.filter(user=user)

@pytest.mark.django_db
def test_signup_form_valid_data(user_data):
    form = SignUpForm(data=user_data)
    assert form.is_valid()
    user = form.save()
    assert User.objects.filter(email='shahd@paymob.com').exists()
    assert user.email == 'shahd@paymob.com'

@pytest.mark.django_db
def test_signup_form_email_already_exists(user_data):
    User.objects.create(email='shahd@paymob.com', password='oldpassword')
    form = SignUpForm(data=user_data)
    assert not form.is_valid()
    with pytest.raises(IntegrityError):
        form.save()

@pytest.mark.django_db
def test_signup_form_save_commit_false(user_data):
    form = SignUpForm(data=user_data)
    if form.is_valid():
        user = form.save(commit=False)
    assert not User.objects.filter(email='shahd@paymob.com').exists()
    assert user.email == 'shahd@paymob.com'

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


# @pytest.mark.django_db
# def test_transaction_history(client, user, transactions):
#     client.login(username=user.username, password='user123')
#     # url = reverse('transaction_history')  
#     response = client.get('transaction_history.html')
#     assert response.status_code == 200
#     assert 'transactions' in response.context
#     assert list(response.context['transactions']) == list(transactions)

@pytest.mark.django_db
def test_transaction_history(client, user, transactions):
    client.login(username=user.username, password='user123')
    response = client.get('/transactions/history/')
    assert response.status_code == 200
    assert 'transactions' in response.context
    assert list(response.context['transactions']) == list(transactions)
