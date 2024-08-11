from django.db import models


class Currency(models.Model):
    """A model containing a currency with name and symbol."""

    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=3)
    country = models.CharField(max_length=100)
    image_url = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name
