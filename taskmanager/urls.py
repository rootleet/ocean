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
from . import views, api

urlpatterns = [
    path('', views.my_tasks, name='my_tasks'),
    path('view/<url>/', views.task, name='task'),
    path('update/<url>/', views.update_task, name='task_update'),
    path('new/',views.new_task,name='task_new'),
    path('save_new_task/',views.save_new_task,name='save_new_task'),
    path('new_task_tran/',views.new_task_tran,name='save_new_task_tran'),
    path('close_task/<uni>',views.close_task,name='close_task'),
    path('api/',api.index,name='api')
]
