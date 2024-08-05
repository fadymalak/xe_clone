from django.db import models


class CurrencyPrice(models.Model):
    """Model of the price of a currency at a certain time.

    Fields:
        currency (ForeignKey): The currency associated with the price.
        price (DecimalField): The current price of the currency.
        created_at (DateTimeField): The date when the price was created.
        updated_at (DateTimeField): The date when the price was last updated.
    """

    currency = models.ForeignKey("Currency", on_delete=models.CASCADE)
    # TODO: Change to DecimalField or IntegerField
    price = models.FloatField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the currency representation."""
        return f"{self.currency}"
