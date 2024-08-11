from django.db import models
from app.models.user import user

class Transfer(models.Model):
    from_user = models.ForeignKey(user, related_name='transfers_made', on_delete=models.CASCADE)
    to_user = models.ForeignKey(user, related_name='transfers_received', on_delete=models.CASCADE)
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transfer from {self.from_user} to {self.to_user} amount {self.amount}"


