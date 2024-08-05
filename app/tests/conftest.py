import pytest

from app.models import Currency, CurrencyPrice


@pytest.fixture
def currency_prices():
    currency_eg = Currency.objects.create(name="Egyptian pound", symbol="EGP", country="Egypt")
    currency_us = Currency.objects.create(name="US Dollar", symbol="USD", country="USA")

    prices = [
        CurrencyPrice.objects.create(currency=currency_eg, price=30),
        CurrencyPrice.objects.create(currency=currency_eg, price=34),
        CurrencyPrice.objects.create(currency=currency_eg, price=48.5),
        CurrencyPrice.objects.create(currency=currency_us, price=1),
    ]

    return currency_eg, currency_us, prices
