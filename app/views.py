# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views import View
from .forms import CustomUserCreationForm, CustomPasswordResetForm, TransferForm

class SignUpView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('to login page')
        return render(request, 'signup.html', {'form': form})

class ForgetPasswordView(View):
    def get(self, request):
        form = CustomPasswordResetForm()
        return render(request, 'forget_password.html', {'form': form})

    def post(self, request):
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            return redirect('password_reset_done')
        return render(request, 'forget_password.html', {'form': form})

class SendMoneyView(View):
    def get(self, request):
        form = TransferForm()
        return render(request, 'send_money.html', {'form': form})

    def post(self, request):
        form = TransferForm(request.POST)
        if form.is_valid():
            transfer = form.save()
            transfer.from_user.add_balance(-transfer.amount)
            transfer.to_user.add_balance(transfer.amount)
            return redirect('home')
        return render(request, 'send_money.html', {'form': form})
