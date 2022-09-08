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
    path('view/<issue_id>',views.view_issue, name='view_issue'),
    path('log-issue',views.log_issue,name='log-issue'),
    path('all_task/',views.all_task,name='all_task'),
    path('mark_esc/',views.mark_esc,name='mark-esc'),
    path('escalate/',views.to_scalate,name='to_escalate'),
    path('escalate/<provider>',views.escalate_detail,name='escalate_detail'),
    path('send-to-provider/',views.send_to_provider,name='send-to-provider'),
    path('accessories/',views.accessories, name='accessories'),
    path('save-provider',views.new_provider,name='save-provider'),
    path('save-tag',views.new_tag,name='save-tag'),
    path('add_to_task',views.add_to_task, name='add_to_task'),
    path('view_task/<task_id>/', views.view_task,name='view_task'),
    path('add_task_update',views.add_task_update, name='add_task_update'),
    path('new_task',views.new_task,name='new_task'),
    path('update_task/<entry_uni>',views.update_task,name='update_task'),
    path('close_task/',views.close_task,name='close_task'),
    path('export_task/', views.export_task,name='export_task'),
    path('search/', views.finder,name='search'),
    path('change_domain/',views.change_domain,name='change_domain'),
    path('test_suolution/',views.test_suolution,name='test_suolution')





]

# handler404 = 'blog.views.handler404'
