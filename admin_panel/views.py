from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.sites import requests

# Create your views here.
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def all_issues(request):
    return render(request, 'all_issues.html')


def view_issue(request,issue_id):
    return render(request, 'view_issue.html')