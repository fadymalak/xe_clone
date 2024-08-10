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
