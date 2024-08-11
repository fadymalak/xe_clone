from django.contrib.auth import get_user_model
from rest_framework import serializers
from app.models.transaction import Transaction
from app.models.transfer import Transfer
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                raise AuthenticationFailed('Invalid login credentials')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        refresh = self.get_token(user)

        data = {}
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        # Add extra responses here
        data['email'] = user.email

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  

class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'type', 'success', 'created_at', 'updated_at']

class TransferSerializer(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField(write_only=True)
    to_user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Transfer
        fields = ['id', 'from_user', 'to_user', 'from_user_id', 'to_user_id', 'amount', 'created_at', 'is_deleted', 'updated_at']
        read_only_fields = ['from_user', 'to_user']

    def create(self, validated_data):
        from_user = User.objects.get(id=validated_data['from_user_id'])
        to_user = User.objects.get(id=validated_data['to_user_id'])
        return Transfer.objects.create(from_user=from_user, to_user=to_user, **validated_data)

    def update(self, instance, validated_data):
        instance.from_user = User.objects.get(id=validated_data.get('from_user_id', instance.from_user_id))
        instance.to_user = User.objects.get(id=validated_data.get('to_user_id', instance.to_user_id))
        instance.amount = validated_data.get('amount', instance.amount)
        instance.is_deleted = validated_data.get('is_deleted', instance.is_deleted)
        instance.save()
        return instance


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_otp(self, value):
        user = User.objects.get(email=self.initial_data['email'])
        if not user.profile.otp == value:
            raise serializers.ValidationError("OTP is incorrect or has expired.")
        return value

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New Password and Confirm Password do not match."})
        return data
# TODO: Import the User from django.conf.settings.AUTH_USER_MODEL if the base user model is changed
import re

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Currency, CurrencyPrice
from app.models.user import user
from app.models.transfer import Transfer


class CurrencyConverterSerializer(serializers.Serializer):
    from_currency = serializers.CharField(max_length=3)
    to_currency = serializers.CharField(max_length=3)
    amount = serializers.FloatField(min_value=0)

    def validate_from_currency(self, value):
        if re.search(r'<.*?>', value):
            raise serializers.ValidationError("Invalid input: HTML tags are not allowed.")
        if not value.isalpha():
            raise serializers.ValidationError("Invalid input: Only alphabetic characters are allowed.")

        return value

    def validate_to_currency(self, value):
        if re.search(r'<.*?>', value):
            raise serializers.ValidationError("Invalid input: HTML tags are not allowed.")
        if not value.isalpha():
            raise serializers.ValidationError("Invalid input: Only alphabetic characters are allowed.")

        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ["id", "name", "symbol"]


class CurrencyPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyPrice
        fields = ["price", "created_at"]


class CurrencyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ["id", "name", "symbol", "country", "image_url", "all_prices"]

    all_prices = serializers.SerializerMethodField()

    def get_all_prices(self, obj):
        prices = CurrencyPrice.objects.filter(currency=obj).order_by("-created_at")
        return CurrencyPriceSerializer(prices, many=True).data


class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    preferred_currency = serializers.CharField(write_only=True, required=True)
    iban = serializers.CharField(write_only=True,required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'preferred_currency','iban']

    def create(self, validated_data):
        user_default = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user_default.set_password(validated_data['password'])
        user_default.save()
        user_custom = user.objects.create(user=user_default, preferred_currency=validated_data["preferred_currency"], iban=validated_data["iban"])
        return user_default
    


class SendMoneySerializer(serializers.ModelSerializer):
    to_user_username = serializers.CharField()

    class Meta:
        model = Transfer
        fields = ['to_user_username', 'amount']

    def validate(self, data):
        from_user = self.context['request'].user
        to_user = User.objects.filter(username=data['to_user_username']).first()

        from_user_info = user.objects.filter(user=from_user).first()
        to_user_info = user.objects.filter(user=to_user).first()

        if not to_user_info:
            raise serializers.ValidationError("Receiver not found")
        if from_user_info == to_user_info:
            raise serializers.ValidationError("You cannot send money to yourself")
        if from_user_info.balance < data['amount']:
            raise serializers.ValidationError("Insufficient balance")

        data['to_user'] = to_user
        return data

    def create(self, validated_data):
        from_user = self.context['request'].user
        from_user_info = user.objects.filter(user=from_user)
        to_user = User.objects.filter(username=validated_data['to_user_username']).first()
        to_user_info = user.objects.filter(user=to_user)
        amount = validated_data['amount']
        import pdb
        pdb.set_trace()
        from_user_info.subtract_balance(amount)

        to_user_info.add_balance(amount)

        transfer = Transfer .objects.create(
            from_user=from_user.user_info,
            to_user=to_user.user_info,
            amount=amount
        )

        return transfer