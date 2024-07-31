from django import forms
from app.models.user import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate


class SignUpForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ('email', 'passwrod')
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