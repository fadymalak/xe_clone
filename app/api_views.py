from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Currency, CurrencyPrice
from .pagination import CurrencyPagination
from .serializers import (
    CurrencyConverterSerializer,
    CurrencyDetailSerializer,
    CurrencySerializer,
)


class CurrencyConverterView(APIView):
    """
    API view for currency conversion.
    Methods:
    - post: Handles POST requests and performs the currency conversion.
    """

    @extend_schema(request=CurrencyConverterSerializer, responses={200: 'converted_amount: float'})
    def post(self, request, *args, **kwargs):
        serializer = CurrencyConverterSerializer(data=request.data)
        if serializer.is_valid():
            from_currency = serializer.validated_data["from_currency"].upper()
            to_currency = serializer.validated_data["to_currency"].upper()
            amount = serializer.validated_data["amount"]

            from_currency = CurrencyPrice.objects.filter(currency__symbol=from_currency).order_by("-created_at").first()
            to_currency = CurrencyPrice.objects.filter(currency__symbol=to_currency).order_by("-created_at").first()

            if from_currency is None or to_currency is None:
                return Response(
                    {"error": "Unknown currency symbol"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            converted_amount = to_currency.price / from_currency.price * amount
            return Response({"converted_amount": converted_amount}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsernameView(APIView):
    """
    A view that returns the username of the current authenticated user.
    Methods:
    - get: Handle GET request to return the current user's username.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"username": request.user.username})


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """A viewset that make retrieve and list actions for Currency."""

    queryset = Currency.objects.all()
    pagination_class = CurrencyPagination
    filter_backends = [SearchFilter]
    search_fields = ["name", "symbol"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CurrencyDetailSerializer
        return CurrencySerializer
