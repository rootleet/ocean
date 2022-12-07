from django import forms

from inventory.models import AssetGroup, Assets


class NewAssetGroup(forms.ModelForm):
    class Meta:
        model = AssetGroup
        exclude = ['created_on']


class NewAsset(forms.ModelForm):
    class Meta:
        model = Assets
        exclude = ['created_on']
