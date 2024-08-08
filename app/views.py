from django.shortcuts import render

# Create your views here.
from typing import Any
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.views.generic.edit import CreateView
from app.models.User import User
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
from app.models.User import User
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

