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
from . import views, invento

urlpatterns = [
    path('', views.inventory, name='inventory'),
    path('api/', invento.interface, name='interface'),
    path('assets/', views.assets, name='assets'),
    path('assets/newgroup/', views.newgroup, name='newgroup'),
    path('assets/save-new', views.assets_new, name='assets_new'),
    path('purchasing/', views.purchasing, name='purchasing'),
    path('purchasing/new/', views.new_purchasing_order, name='new_purchasing_order'),
    path('grn/', views.grn, name='grn'),
    path('grn/new/', views.new_grn, name='new-grn'),
    path('workstation/', views.workstation, name='workstation'),
    path('workstation/save_workstation/', views.save_workstation, name='save_workstation'),
    path('workstation/view/<mac_addr>/', views.view_workstation, name='view_workstation'),

    path('products/new/', views.new_products, name='new-product'),

    path('transfer/',views.transfer,name='transfer'),
    path('transfer/new/',views.transfer_new,name='new_transfer'),
    path('transfer/edit/<entry_no>/',views.transfer_edit,name='edit_transfer')

]

# handler404 = 'blog.views.handler404'
