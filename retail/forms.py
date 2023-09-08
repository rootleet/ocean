from django import forms

from retail.models import Clerk


class NewClerk(forms.ModelForm):
    class Meta:
        model = Clerk
        exclude = ['flag_dwn','flag_disable','created_on','edited_on']