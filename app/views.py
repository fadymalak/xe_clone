import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import render
from django.views import View
from xecd_rates_client import XecdClient

from .forms import CurrencyConverterForm


class ConverterView(View):
    def get(self, request, *args, **kwargs):
        form = CurrencyConverterForm()
        return render(request, "converter.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = CurrencyConverterForm(request.POST)
        context = {}

        if form.is_valid():
            from_currency = form.cleaned_data["from_currency"].upper()
            to_currency = form.cleaned_data["to_currency"].upper()
            amount = int(form.cleaned_data["amount"])
            key = f"{from_currency} to {to_currency}"

            if cache.get(key):
                response = cache.get(key)

            else:
                ACCOUNT_ID = os.environ.get("XE_ACCOUNT_ID")
                API_KEY = os.environ.get("XE_API_KEY")
                xecd = XecdClient(ACCOUNT_ID, API_KEY)
                response = xecd.convert_from(from_currency, to_currency, 1)
                cache.set(key, response, 3600)

            if response.get("code") == 7 or len(response.get("to")) == 0:
                context = {
                    "res": "Invalid currency code",
                }
            else:
                context = {
                    "res": response.get("to")[0]["mid"] * amount,
                }

        return render(request, "converter.html", {"form": form, "context": context})


class DisplayUsernameView(LoginRequiredMixin, View):
    # TODO Finish login view and template

    def get(self, request, *args, **kwargs):
        username = request.user.username
        return render(request, "display_username.html", {"username": username})
