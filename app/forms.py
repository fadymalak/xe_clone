from django import forms
from app.models.User import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
import re


class CurrencyConverterForm(forms.Form):
    from_currency = forms.CharField(label="From", max_length=3)
    to_currency = forms.CharField(label="To", max_length=3)
    amount = forms.FloatField(label="Amount", min_value=0)

    def clean_from_currency(self):
        from_currency = self.cleaned_data.get('from_currency')

        if re.search(r'<.*?>', from_currency):
            raise forms.ValidationError("Invalid input: HTML tags are not allowed.")
        if not from_currency.isalpha():
            raise forms.ValidationError("Invalid input: Only alphabetic characters are allowed.")

        return from_currency

    def clean_to_currency(self):
        to_currency = self.cleaned_data.get('to_currency')

        if re.search(r'<.*?>', to_currency):
            raise forms.ValidationError("Invalid input: HTML tags are not allowed.")
        if not to_currency.isalpha():
            raise forms.ValidationError("Invalid input: Only alphabetic characters are allowed.")

        return to_currency

class SignUpForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ('email', 'password')
        widgets = {
            'email' : forms.TextInput(attrs={'class': 'form_control'}),
            'password' : forms.TextInput(attrs={'class': 'form_control'}),
        }
    def verify_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email is already in use.")
        return email

    def save(self, commit=True):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        self.verify_email()
        user = User(username=email,email=email)
        user.set_password(password)
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Incorrect email or password.")
        return cleaned_data
