from django import forms

from appscenter.models import App, VersionControl


class NewApp(forms.ModelForm):
    class Meta:
        model = App
        exclude = ['created_time', 'created_date', 'status', 'version','containers']


class NewVersion(forms.ModelForm):
    class Meta:
        model = VersionControl
        exclude = ['created_on', 'created_time', 'status']
