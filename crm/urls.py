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
from . import views, crm_api

urlpatterns = [
    path('', views.base, name='crm'),
    path('api/',crm_api.api_interface,name='crm_api'),
    path('users/',views.crm_users,name='crm_users'),
    path('tools/',views.crm_tools,name='crm_tools'),
    path('follow-up/',views.follows,name='follows'),
    path('contacts/',views.contacts,name='crm_contacts'),
    path('campaigns/',views.campaigns,name='campaigns'),
    path('campaigns/new/',views.new_campaign,name='new_campaign')

]

# handler404 = 'blog.views.handler404'
