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
    path('', views.index, name='admin_panel'),
    path('issues',views.all_issues, name='all-issues'),
    path('view/<issue_id>',views.view_issue, name='view-issue'),
    path('log-issue',views.log_issue,name='log-issue'),
    path('all_task/',views.all_task,name='all_task'),
    path('mark_esc/',views.mark_esc,name='mark-esc'),
    path('escalate/',views.to_scalate,name='to_escalate'),
    path('escalate/<provider>',views.escalate_detail,name='escalate_detail'),
    path('send-to-provider/',views.send_to_provider,name='send-to-provider')



]
