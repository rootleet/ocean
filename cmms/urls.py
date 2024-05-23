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
from . import views, cmms_api

urlpatterns = [
    path('', views.base, name='cmms'),
    path('car-jobs/', views.carjobs, name='car-jobs'),
    path('tools/', views.tools, name='cmms-tools'),
    path('api/', cmms_api.api, name='cmms_api'),
    path('stock/', views.stock, name='stock'),
    path('stock/count/', views.view_stock_count, name='stock-count'),
    path('stock/frozen/new/', views.new_frozen, name='new-frozen'),
    path('stock/count/new/<frozen>/', views.new_count, name='new_count'),
    path('compare/<pk>/<as_of>/<group>/', views.compare, name='compare'),
    path('stock/new/', views.new_stock_count, name='new-stock-count'),
    path('stock/frozen/', views.forezen, name='frozen-stock'),
    path('stock/count/edit/<pk>/', views.edit_stock_count, name='edit_stock_count'),

    path('sales/', views.sales, name='sales'),
    path('sales/assets/', views.sales_assets, name='sales_assets'),
    path('sales/assets/new/', views.new_sales_asset, name='new_sales_assets'),
    path('sales/customers/', views.customer_sales, name='customer_sales'),
    path('sales/new-customer/', views.new_sales_customer, name='new_sales_customer'),
    path('sales/save-customer/', views.save_sales_customer, name='save_sales_customer'),
    # path('sales/<customer>/', views.sales_customer_transactions, name='sales_customer_transactions'),
    path('sales/spec/<model_pk>/', views.model_spec, name='model_spec'),
    path('sales/save-transaction/', views.save_sales_transaction, name='save_sales_transaction'),
    path('sales/deals/<customer>/', views.sales_deal, name='sales-deal'),
    path('sales/adons/', views.sales_tools, name='sales_tools'),
    path('sales/approval_request/',views.proforma_approval_requests,name='prod_appr_req'),

    path('servicing/', views.service_customers, name='service_customers'),
    path('servicing/customer/<customer_code>/', views.service_customer, name='service_customer')

]

# handler404 = 'blog.views.handler404'
