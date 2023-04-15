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
    path('', views.index, name='home'),
    path('issues', views.all_issues, name='all-issues'),
    path('view/<issue_id>', views.view_issue, name='view_issue'),
    path('log-issue', views.log_issue, name='log-issue'),
    path('all_task/', views.all_task, name='all_task'),
    path('mark_esc/', views.mark_esc, name='mark-esc'),
    path('escalate/', views.to_scalate, name='to_escalate'),
    path('escalate/<provider>', views.escalate_detail, name='escalate_detail'),
    path('send-to-provider/', views.send_to_provider, name='send-to-provider'),
    path('accessories/', views.accessories, name='accessories'),
    path('save-provider', views.new_provider, name='save-provider'),
    path('save-tag', views.new_tag, name='save-tag'),
    path('add_to_task', views.add_to_task, name='add_to_task'),
    path('task/<task_id>/view/', views.view_task, name='view_task'),
    path('task/<task>/<br>/', views.issues_branch, name='view_branch'),
    path('add_task_update', views.add_task_update, name='add_task_update'),
    path('new_task', views.new_task, name='new_task'),
    path('update_task/<entry_uni>', views.update_task, name='update_task'),
    path('close_task/', views.close_task, name='close_task'),
    path('export_task/', views.export_task, name='export_task'),
    path('search/', views.finder, name='search'),
    path('change_domain/', views.change_domain, name='change_domain'),
    path('test_suolution/', views.test_suolution, name='test_suolution'),
    path('task_filter/', views.task_filter, name='task_filter'),
    path('emails/', views.emails, name='emails'),
    path('add_notification_mem/', views.add_notification_mem, name='add_notification_mem'),
    path('send_mail/<task_id>', views.send_mail, name='send_mail'),
    path('autos/<tool>', views.auto, name='autos'),
    path('save_email_group/', views.save_email_group, name='save_email_group'),

    # suppliers url
    path('inventory/tools/', views.inventory_tools, name='inventory_tools'),
    path('inventory/tools/save_suppler', views.save_supplier, name='save-supplier'),
    path('inventory/tools/save-group', views.save_group, name='save-group'),
    path('inventory/tools/save-sub-grop', views.save_sub_group, name='save-sub-group'),
    path('inventory/tools/save-packing', views.save_packing, name='save-packing'),

    # products master
    path('inventory/products/', views.products, name='products'),
    path('inventory/products/new/', views.new_products, name='new-product'),
    path('inventory/products/save-new/', views.save_new_product, name='save-new-product'),
    path('inventory/products/adjustment/<p>', views.adjust_product_qty, name='adjust_product_qty'),
    path('inventory/adjustment/', views.adjustment, name='adjustment'),
    path('inventory/adjustment/new/', views.new_adjustment, name='new_adjustment'),
    path('inventory/transfer/', views.transfer, name='transfer'),
    path('inventory/transfer/new/', views.new_transfer, name='new_transfer'),
    # path('inventory/receiving/', views.grn_entries, name='grn_entries'),
    # path('inventory/receiving/new/', views.new_grn, name='new_grn'),

    # accounts urls
    path('accounts/', views.accounts, name='accounts'),
    path('accounts/tax-master/', views.tax_master, name='tax_master'),
    path('accounts/bank-master/', views.bank_master, name='bank-master'),
    path('accounts/bank_master/post/', views.bank_posts, name='bank-post'),
    path('accounts/suppliers/', views.suppliers, name='suppliers'),

    # company setup
    path('company/locations/', views.loc_master, name='loc_master'),
    path('company/form_post/', views.post_form, name='post_form'),

    path('adminapi/<module>/<action>/', views.api, name='api'),
    path('profile/', views.profile, name='profile'),
    path('profile/restpwrod/<token>/', views.resetpasswordview, name='resetpasswordview'),
    path('profile/resetpword/',views.resetpassword,name='resetpassword'),
    path('logout_view/', views.logout_view, name='logout'),
    path('update_user_settings/', views.update_user_settings, name='update_user_settings'),

    path('login/', views.login, name='login'),
    path('register/', views.new_user, name='new-user'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('logout_view/', views.logout_view, name='logout'),
    path('login-process', views.login_view, name='login_process'),
    path('open-ticket/', views.ticket, name='open-ticket'),
    path('all-ticket/', views.all_tickets, name='all-ticket'),
    path('save-ticket/', views.make_ticket, name='save-ticket'),
    path('all-users/', views.all_users, name='all-users'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('save-ou/', views.save_ou, name='save_ou'),
    path('save_um/', views.save_um, name='save_um'),

    path('sms/', views.sms, name='sms'),
    path('sms/ew_sms_api/', views.new_sms_api, name='new_sms_api'),
    path('sms/bulk_sms/',views.bulk_sms,name='bulk_sms')

]

# handler404 = 'blog.views.handler404'
