import requests
from django.core.management.base import BaseCommand

from app.models import Currency


class Command(BaseCommand):
    help = "Seeds the database with initial currency data"

    def handle(self, *args, **options):
        response = requests.get("https://api.currencyfreaks.com/v2.0/supported-currencies")

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Failed to fetch data from API"))
            return

        data = response.json().get("supportedCurrenciesMap")

        if not data:
            self.stdout.write(self.style.ERROR("No data found in the API response"))
            return

        currency_list = []
        for _key, value in data.items():
            currency_list.append(
                {
                    "name": value["currencyName"],
                    "symbol": value["currencyCode"],
                    "country": value["countryName"],
                }
            )

        currencies = []
        for currency_data in currency_list:
            try:
                if len(currency_data["symbol"]) == 3 and currency_data["name"]:
                    currencies.append(Currency(**currency_data))
            except TypeError as e:
                self.stdout.write(self.style.ERROR(f"Error creating Currency object: {e}"))

        Currency.objects.bulk_create(currencies)
        self.stdout.write(self.style.SUCCESS("Successfully seeded the database with currencies"))
