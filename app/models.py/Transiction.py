from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model() #dynamically retrieve the user 

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    amount = models.FloatField()
    type = models.CharField(
        max_length=6,
        choices=[('credit', 'Credit'), ('debit', 'Debit')],
        default='credit'
    )
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.type.capitalize()} transaction by {self.user} amount {self.amount}"