import os

import requests
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

from app.models import Currency, CurrencyPrice


class Command(BaseCommand):
    help = "Fetch and seed the currency prices from Currency Freaks API"

    def handle(self, *args, **kwargs):
        load_dotenv()
        api_key = os.getenv("CURRECNYFREAKS_API_KEY")
        response = requests.get(f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={api_key}")

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Failed to fetch data from API"))
            return

        data = response.json()
        rates = data["rates"]
        date = data["date"].split(" ")[0]

        currency_prices = []
        for symbol, price in rates.items():
            try:
                if len(symbol) == 3:
                    currency = Currency.objects.get(symbol=symbol)
                    currency_price = CurrencyPrice(
                        currency=currency,
                        current_price=float(price),
                        created_at=date,
                    )
                    currency_prices.append(currency_price)
            except Currency.DoesNotExist:
                pass

        CurrencyPrice.objects.bulk_create(currency_prices)
        self.stdout.write(self.style.SUCCESS("Successfully seeded currency prices"))
