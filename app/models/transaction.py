from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model() #dynamically retrieve the user 

class transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    amount = models.FloatField()
    type = models.CharField(
        max_length=6,
        choices=[('credit', 'Credit'), ('debit', 'Debit')],
        default='credit'
    )
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.type.capitalize()} transaction by {self.user} amount {self.amount}"