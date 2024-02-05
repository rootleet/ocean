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

from maintenance import api, views

urlpatterns = [

    path('api/', api.interface, name='interface'),
    path('',views.landing_page, name='maintenance'),
    path('preview/<uni>/',views.maintenance,name='maintenance_preview'),
    path('asset-groups/',views.asset_groups,name='maint_asset_groups'),
    path('new-asset/',views.new_maintenance_asset,name='new_maintenance_asset'),
    path('assets/',views.assets,name='maint_assets'),
    path('upload_asset_image/',views.upload_asset_image,name='upload_asset_image'),
    path('work-request/',views.new_maintain,name='new_maintain'),
    path('upload_evidence/',views.upload_evidence,name='upload_evidence'),
    path('word-order/',views.work_order,name='work_order'),
    path('upload-wo-attachment/',views.upload_wo_attachment,name='upload-wo-attachment'),
    path('wo-track/<wo_no>/',views.wo_tracing,name='wo_trackinh'),
    path('save_trans/',views.save_trans,name='save_trans')

]
