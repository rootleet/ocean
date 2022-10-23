from django import forms

from admin_panel.models import ProductMaster, ProductPacking, Locations


class NewProduct(forms.ModelForm):
    class Meta:
        model = ProductMaster
        exclude  = ['created_on','edited_on','status','created_by']

class NewProductPacking(forms.ModelForm):
    class Meta:
        model = ProductPacking
        exclude = ['created_on', 'edited_on', 'status', 'created_by']

class NewLocation(forms.ModelForm):
    class Meta:
        model = Locations
        exclude = ['created_on', 'edited_on', 'status', 'created_by']