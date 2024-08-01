from django.db import models


class Currency(models.Model):
    """A model containing a currency with name and symbol."""

    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=3)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.name
