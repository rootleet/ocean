from django import forms

from cmms.models import SalesCustomers, SalesCustomerTransactions


class NewSalesCustomer(forms.ModelForm):
    class Meta:
        model = SalesCustomers
        exclude = ['created_date', 'created_time', 'updated_date', 'updated_time', 'status']


class NewSaleTransactions(forms.ModelForm):
    class Meta:
        model = SalesCustomerTransactions
        exclude = ['created_date', 'created_time', 'updated_date', 'updated_time', 'status']
