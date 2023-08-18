from django import forms

from taskmanager.models import Tasks, TaskTransactions


class NewTask(forms.ModelForm):
    class Meta:
        model = Tasks
        exclude = ['created_date', 'created_time', 'updated_date', 'updated_time', 'status']


class NewTaskTransaction(forms.ModelForm):
    class Meta:
        model = TaskTransactions
        exclude = ['created_date', 'created_time', 'updated_date', 'updated_time', 'status']