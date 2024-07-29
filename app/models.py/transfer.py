from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model() #dynamically retrieve the user 

class Transfer(models.Model):
    from_user = models.ForeignKey(User, related_name='transfers_from', on_delete=models.DO_NOTHING)
    to_user = models.ForeignKey(User, related_name='transfers_to', on_delete=models.DO_NOTHING)
    amount = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Transfer from {self.from_user} to {self.to_user} amount {self.amount}"


