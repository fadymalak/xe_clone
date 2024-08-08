from rest_framework import serializers
from django.contrib.auth.models import User
from app.models.user import user
from app.models.transfer import transfer


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
        user_custom = user(user=user_default, preferred_currency=validated_data["preferred_currency"], iban=validated_data["iban"])
        return user_default
    


class SendMoneySerializer(serializers.ModelSerializer):
    to_user_username = serializers.CharField()

    class Meta:
        model = transfer
        fields = ['to_user_username', 'amount']

    def validate(self, data):
        from_user = user.objects.get(user=self.context['request'].user)
        to_user = user.objects.filter(user__username=data['to_user_username']).first()

        if not to_user:
            raise serializers.ValidationError("Receiver not found")
        if from_user == to_user:
            raise serializers.ValidationError("You cannot send money to yourself")
        if from_user.balance < data['amount']:
            raise serializers.ValidationError("Insufficient balance")

        data['to_user'] = to_user
        return data

    def create(self, validated_data):
        from_user = user.objects.get(user=self.context['request'].user)
        to_user = validated_data['to_user']
        amount = validated_data['amount']

        from_user.subtract_balance(amount)

        to_user.add_balance(amount)

        transfer = transfer.objects.create(
            from_user=from_user.user,
            to_user=to_user.user,
            amount=amount
        )

        return transfer