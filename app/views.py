from typing import Any
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.views.generic.edit import CreateView
from app.models.user import User
from django.urls import reverse_lazy
from app.forms import SignUpForm, LoginForm
from app.models.Transiction import Transaction
from django.views import View
from django.views.generic import TemplateView

# Create your views here.

class SignUpView(CreateView):
    template_name = 'signup.html'
    model = User
    from_class = SignUpForm
    success_url = reverse_lazy('login')

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
        return render(request, 'login.html', {'form': form})

class TransactionHistoryView(TemplateView):
    template_name = 'transaction_history.html'
    model = Transaction
    def get_context_data(self, **kwargs):
        context = {}
        context.update(kwargs)
        context['transactions'] = Transaction.objects.filter(user=self.request.user)
        return context



