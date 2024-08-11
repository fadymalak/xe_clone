from django.db import models

from .currency import Currency


class Converter(models.Model):
    """Model of currency converter.

    Fields:
        from_currency (Currency): The currency to convert from.
        to_currency (Currency): The currency to convert to.
        rate (Float): The conversion rate.
        created_at (DateTime): The date when the converter was created.
        updated_at (DateTime): The date when the converter was last updated.
        deleted_at (DateTime): The date when the converter was deleted.
    """

    from_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="from_currency")
    to_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="to_currency")
    # TODO: Change to DecimalField or IntegerField
    rate = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """String representation of the converter."""
        return f"{self.from_currency} to {self.to_currency}"
