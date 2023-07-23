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
    path('', views.base, name='cmms'),
    path('car-jobs/', views.carjobs, name='car-jobs'),
    path('tools/', views.tools, name='cmms-tools'),
    path('api/', views.api, name='cmms_api'),
    path('stock/', views.stock, name='stock'),
    path('stock/count/', views.view_stock_count, name='stock-count'),
    path('stock/count/new/', views.new_stock_count, name='stock-count-new'),
    path('stock/count/new/<frozen>/', views.new_count, name='new_count'),
    path('compare/<pk>/<as_of>/<group>/', views.compare, name='compare'),
    path('stock/new/', views.new_stock_count, name='new-stock-count'),
    path('stock/frozen/', views.forezen, name='frozen-stock'),
    path('stock/count/edit/<pk>/', views.edit_stock_count, name='edit_stock_count')

]

# handler404 = 'blog.views.handler404'
