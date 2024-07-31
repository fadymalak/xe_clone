from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom user model that inherits from AbstractUser and includes
    additional fields."""

    preferred_currency = models.CharField(max_length=3, default="")
    iban = models.CharField()
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    password_updated_at = models.DateTimeField(timezone.now)
    balance = models.FloatField(default=0.00)

    def add_balance(self, amount):
        """Updates the user's balance by the specified amount.

        Args:
            amount = The amount to add to the balance.
        """
        if amount > 0:
            self.balance += amount
            self.save()
        else:
            raise ValueError("Amount must be positive")

    def __str__(self):
        return self.username
