from django.contrib import admin

from .models import Currency, CurrencyPrice

# Register your models here.


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("name", "symbol")


@admin.register(CurrencyPrice)
class CurrencyPriceAdmin(admin.ModelAdmin):
    list_display = ("currency", "current_price", "created_at")
    list_select_related = ("currency",)
    search_fields = ("currency__name",)
