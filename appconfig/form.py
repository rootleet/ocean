from django import forms

from appscenter.models import App, VersionControl


class NewApp(forms.ModelForm):
    class Meta:
        model = App
        exclude = ['created_on', 'created_time', 'status', 'version']


class NewVersion(forms.ModelForm):
    class Meta:
        model = VersionControl
        exclude = ['created_on', 'created_time', 'status']
