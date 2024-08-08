from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class user(models.Model):  
    user = models.OneToOneField(User,related_name="user_info", on_delete=models.CASCADE)
    preferred_currency = models.CharField(max_length=3)
    iban = models.CharField(max_length=30)
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    password_updated_at = models.DateTimeField(default=timezone.now)  
    balance = models.FloatField(default=10.00)
    otp = models.CharField(max_length=6, blank=True, null=True)

    def add_balance(self, amount):
        if amount > 0:
            self.balance += amount
            self.save()
        else:
            raise ValueError("Amount must be positive")
    def subtract_balance(self, amount):
        if amount > 0:
            self.balance -= amount
            self.save()


    def __str__(self):
        return self.user.username
