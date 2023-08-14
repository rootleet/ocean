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
from . import views

urlpatterns = [
    path('', views.meeting, name='meeting'),
    path('new/', views.new_meeting, name='new_meeting'),
    path('open/<meeting>/', views.meeting_config, name='open_meeting'),
    path('save_meeting', views.save_meeting, name='save_meeting'),
    path('config_meeting/<meeting>/', views.meeting_config, name='config_meeting'),
    path('add_participant/',views.add_participant,name='add_participant'),
    path('add_talking_point',views.add_talking_point,name='add_talking_point'),
    path('attach/',views.attach,name='attach'),
    path('remove_participant/<meet>/<pk>',views.remove_participant,name='remove_participant'),
    path('remove_point/<meet><pk>',views.remove_point,name='remove_point'),
    path('open/<meeting>/', views.end_meeting, name='end_meeting'),

]

# handler404 = 'blog.views.handler404'
