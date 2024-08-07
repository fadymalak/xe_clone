from django import forms


class CurrencyConverterForm(forms.Form):
    from_currency = forms.CharField(label="From", max_length=3)
    to_currency = forms.CharField(label="To", max_length=3)
    amount = forms.FloatField(label="Amount", min_value=0)
