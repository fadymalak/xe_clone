import os

import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView, ListView

from .forms import CurrencyConverterForm
from .models import Currency, CurrencyPrice

from rest_framework import generics, status
from django.contrib.auth import get_user_model
from .serializers import SignupSerializer, OTPRequestSerializer, SendMoneySerializer
from django.shortcuts import redirect
from rest_framework.response import Response
import random
from .models.transaction import Transaction
from .models.transfer import Transfer
from .models.user import user

User = get_user_model()

class HomeView(View):
    """
    A view class for the home page.
    Methods:
    - get: Handles GET requests and renders the home page template.
    """

    def get(self, request, *args, **kwargs):
        return render(request, "app/home.html")


class ConverterView(View):
    """
    A view class for currency conversion.
    Methods:
    - get: Handles GET requests and renders the currency converter form.
    - post: Handles POST requests and performs the currency conversion.
    - get_conversion_rate: It's a helper function retrieves the conversion rate API or from redis.
    """

    def get(self, request, *args, **kwargs):
        form = CurrencyConverterForm()
        return render(request, "app/converter.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = CurrencyConverterForm(request.POST)
        context = {}

        if form.is_valid():
            from_currency = form.cleaned_data["from_currency"].upper()
            to_currency = form.cleaned_data["to_currency"].upper()
            amount = int(form.cleaned_data["amount"])

            from_currency = CurrencyPrice.objects.filter(currency__symbol=from_currency).order_by("-created_at").first()
            to_currency = CurrencyPrice.objects.filter(currency__symbol=to_currency).order_by("-created_at").first()
            if from_currency is None or to_currency is None:
                context["error"] = "Unknown currency symbol"
            else:
                context["res"] = to_currency.price / from_currency.price * amount
        else:
            context["error"] = form.errors
        return render(request, "app/converter.html", {"form": form, "context": context})

    # Deprecated
    def post_old(self, request, *args, **kwargs):
        """This post method is not used because it uses the free XE API which
        is returning dummy data."""
        form = CurrencyConverterForm(request.POST)
        context = {}

        if form.is_valid():
            from_currency = form.cleaned_data["from_currency"].upper()
            to_currency = form.cleaned_data["to_currency"].upper()
            amount = int(form.cleaned_data["amount"])
            key = f"{from_currency} to {to_currency}"
            response = self.get_conversion_rate(from_currency, to_currency, key)

            if response is None or not response.get("to"):
                context["res"] = "Unknown currency symbol"
            else:
                context["res"] = response.get("to")[0]["mid"] * amount

        return render(request, "app/converter.html", {"form": form, "context": context})

    def get_conversion_rate(self, from_currency, to_currency, key):
        if os.environ.get("REDIS_ACTIVE") == "True" and cache.get(key):
            return cache.get(key)
        AUTH_HEADER = os.environ.get("XE_AUTH_HEADER")
        url = f"https://xecdapi.xe.com/v1/convert_from.json/?from={from_currency}&to={to_currency}&amount=1"
        headers = {"Authorization": AUTH_HEADER}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return None

        response_data = response.json()
        if os.environ.get("REDIS_ACTIVE") == "True":
            cache.set(key, response_data, 3600)

        return response_data


class DisplayUsernameView(LoginRequiredMixin, View):
    """
    View class that displays the username of the current user that enables him receive money.
    Methods:
    - get: Handles GET requests and renders the username template.
    """

    # TODO Finish login view and template
    def get(self, request, *args, **kwargs):
        username = request.user.username
        return render(request, "display_username.html", {"username": username})


class CurrencyListView(ListView):
    """A view that displays a list of currencies."""

    model = Currency
    template_name = "app/currency_list.html"
    context_object_name = "currencies"
    paginate_by = 30

    def get_queryset(self):
        search_query = self.request.GET.get("search")
        if search_query:
            return Currency.objects.filter(name__icontains=search_query)
        return Currency.objects.all()


class CurrencyDetailView(DetailView):
    """A view for displaying detailed information about a currency."""

    model = Currency
    template_name = "app/currency_detail.html"
    context_object_name = "currency"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        currency = self.object
        all_prices = CurrencyPrice.objects.filter(currency=currency).order_by("-created_at")
        context["all_prices"] = all_prices
        return context


class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def perform_create(self, serializer):
        user = serializer.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            return redirect('/login/')
        return response

class OTPRequestView(generics.GenericAPIView):
    serializer_class = OTPRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.save()

        return Response({'message': 'If an account with that email exists, an OTP has been generated and saved.'}, status=status.HTTP_200_OK)

class SendMoneyView(generics.GenericAPIView):
    serializer_class = SendMoneySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        from_user_profile = user.objects.get(user=request.user)
        to_user_profile = serializer.validated_data['to_user']
        amount = serializer.validated_data['amount']

        if from_user_profile.balance < amount:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        from_user_profile.subtract_balance(amount)
        to_user_profile.add_balance(amount)

        Transfer.objects.create(from_user=from_user_profile, to_user=to_user_profile, amount=amount)
        Transaction.objects.create(user=from_user_profile.user, amount=amount)
        Transaction.objects.create(user=to_user_profile.user, amount=amount)

        return Response({'message': 'Money sent successfully'}, status=status.HTTP_200_OK)
from typing import Any
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.views.generic.edit import CreateView
from app.models.user import User
from django.urls import reverse_lazy
from app.forms import SignUpForm, LoginForm
from app.models.transaction import Transaction
from django.views import View
from django.views.generic import TemplateView
from rest_framework import generics
from app.serializers import TransactionSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.serializers import ResetPasswordSerializer
from django.core.mail import send_mail
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from typing import Any
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.views.generic.edit import CreateView
from app.models.user import User
from django.urls import reverse_lazy
from app.forms import SignUpForm, LoginForm
from app.models.transaction import Transaction
from django.views import View
from django.views.generic import TemplateView
from rest_framework_simplejwt.authentication import JWTAuthentication

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



    
class ResetPasswordAPI(APIView):
    permission_classes = [permissions.AllowAny]  
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        uid = request.user.id
        new_password = request.data.get('new_password')
        
        valid_data = TokenVerifyView.as_view()(request._request).data

        try:
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.user_info.otp = None
        user.save()
        return Response({'success': 'Password has been reset successfully'})

class TransactionHistoryViewAPI(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class LoginViewAPI(TokenObtainPairView):
    serializer_class = LoginSerializer

