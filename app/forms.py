from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from .models.user import user
from django.contrib.auth.models import User
from .models.transfer import transfer


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username','password1','password2',"email")
class CustomPasswordResetForm(PasswordResetForm):
    class Meta:
        model = User
        fields = ('email',)

class TransferForm(forms.ModelForm):
    class Meta:
        model = transfer
        fields = ('from_user', 'to_user', 'amount')
