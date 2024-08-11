import re

from django import forms


class CurrencyConverterForm(forms.Form):
    from_currency = forms.CharField(label="From", max_length=3)
    to_currency = forms.CharField(label="To", max_length=3)
    amount = forms.FloatField(label="Amount", min_value=0)

    def clean_from_currency(self):
        from_currency = self.cleaned_data.get('from_currency')

        if re.search(r'<.*?>', from_currency):
            raise forms.ValidationError("Invalid input: HTML tags are not allowed.")
        if not from_currency.isalpha():
            raise forms.ValidationError("Invalid input: Only alphabetic characters are allowed.")

        return from_currency

    def clean_to_currency(self):
        to_currency = self.cleaned_data.get('to_currency')

        if re.search(r'<.*?>', to_currency):
            raise forms.ValidationError("Invalid input: HTML tags are not allowed.")
        if not to_currency.isalpha():
            raise forms.ValidationError("Invalid input: Only alphabetic characters are allowed.")

        return to_currency
