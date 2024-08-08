
from rest_framework import generics, status
from django.contrib.auth import get_user_model
from .serializers import SignupSerializer, OTPRequestSerializer, SendMoneySerializer
from django.shortcuts import redirect
from rest_framework.response import Response
import random
from .models.transaction import transaction
from .models.transfer import transfer
from .models.user import user

User = get_user_model()

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

        transfer.objects.create(from_user=from_user_profile, to_user=to_user_profile, amount=amount)
        transaction.objects.create(user=from_user_profile.user, amount=amount)
        transaction.objects.create(user=to_user_profile.user, amount=amount)

        return Response({'message': 'Money sent successfully'}, status=status.HTTP_200_OK)
