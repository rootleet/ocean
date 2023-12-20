"""ocean URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views, servicing_api

urlpatterns = [
    path('', views.base, name='service_master'),
    path('api/', servicing_api.interface, name='servicing_api'),
    path('services/', views.services, name='services'),
    path('service/<service_id>/', views.service, name='service'),
    path('newjob/', views.newjob, name='newjob'),
    path('jobcard/', views.jobcard, name='jobcard'),
    path('jobcard/tracking/<cardno>/', views.tracking, name='tracking'),
    path('main-to-provider/<job>/', views.mail_to_provider, name='mail_provider')

]

# handler404 = 'blog.views.handler404'
