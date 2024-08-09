# TODO: Import the User from django.conf.settings.AUTH_USER_MODEL if the base user model is changed
import re

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Currency, CurrencyPrice


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
