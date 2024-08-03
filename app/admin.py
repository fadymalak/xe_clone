from django.contrib import admin

from .models import Currency, CurrencyPrice

# Register your models here.

admin.site.register(Currency)
admin.site.register(CurrencyPrice)
