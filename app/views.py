import os

import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView, ListView

from .forms import CurrencyConverterForm
from .models import Currency, CurrencyPrice


class ConverterView(View):
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
            key = f"{from_currency} to {to_currency}"
            response = self.get_conversion_rate(from_currency, to_currency, key)

            if response is None or not response.get("to"):
                context["res"] = "Invalid currency code"
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
    # TODO Finish login view and template
    def get(self, request, *args, **kwargs):
        username = request.user.username
        return render(request, "display_username.html", {"username": username})


class CurrencyListView(ListView):
    model = Currency
    template_name = "app/currency_list.html"
    context_object_name = "currencies"


class CurrencyDetailView(DetailView):
    model = Currency
    template_name = "app/currency_detail.html"
    context_object_name = "currency"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        currency = self.object
        current_price = CurrencyPrice.objects.filter(currency=currency).order_by("-created_at").first()
        context["current_price"] = current_price
        return context
