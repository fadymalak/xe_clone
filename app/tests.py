from django.test import TestCase

# Create your tests here.
import pytest
from django.core.exceptions import ValidationError
from app.forms import SignUpForm
from app.models.user import User
from app.forms import LoginForm
from app.models.transaction import Transaction
from django.urls import reverse


@pytest.fixture
def user_data():
    return {'email': 'test@example.com', 'password': 'mypassword'}

@pytest.fixture
def transactions(db, user):
    Transaction.objects.create(user=user, detail='Transaction 1', amount=100)
    Transaction.objects.create(user=user, detail='Transaction 2', amount=200)
    return Transaction.objects.filter(user=user)

@pytest.mark.django_db
def test_signup_form_valid_data(user_data):
    form = SignUpForm(data=user_data)
    assert form.is_valid()
    user = form.save()
    assert User.objects.filter(email='test@example.com').exists()
    assert user.email == 'test@example.com'

@pytest.mark.django_db
def test_signup_form_email_already_exists(user_data):
    User.objects.create(email='test@example.com', password='oldpassword')
    form = SignUpForm(data=user_data)
    assert not form.is_valid()
    with pytest.raises(ValidationError):
        if form.is_valid():
            form.clean_email()

@pytest.mark.django_db
def test_signup_form_save_commit_false(user_data):
    form = SignUpForm(data=user_data)
    if form.is_valid():
        user = form.save(commit=False)
    assert not User.objects.filter(email='test@example.com').exists()
    assert user.email == 'test@example.com'

def test_login_form_valid_data(user_data):
    form = LoginForm(data=user_data)
    assert form.is_valid()
    assert form.cleaned_data['email'] == 'user@example.com'
    assert form.cleaned_data['password'] == 'mypassword'

def test_login_form_empty_input():
    form = LoginForm(data={})
    assert not form.is_valid()
    assert 'email' in form.errors
    assert 'password' in form.errors

@pytest.mark.django_db
def test_transaction_history_view_authenticated(client, user, transactions):
    client.login(username='user', password='testpass')
    url = reverse('transaction_history')  
    response = client.get(url)
    assert response.status_code == 200
    assert 'transactions' in response.context
    assert list(response.context['transactions']) == list(transactions)

@pytest.mark.django_db
def test_transaction_history_view_unauthenticated(client):
    url = reverse('transaction_history')
    response = client.get(url)
    assert response.status_code == 302