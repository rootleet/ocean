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
    path('', views.index, name='blog-home'),
    path('article/<title>', views.article, name='article'),
    path('search/<query>', views.search_result, name='search-result'),
    path('search/', views.search, name='search-article'),
    path('new-article/', views.new_article, name='new-article'),
    path('edit_article/<uni>', views.edit_article, name='edit_article'),
    path('edit_save/', views.edit_save, name='edit_save'),
    path('save-article', views.save_article, name='save_article'),
    path('category/<meta>', views.load_meta, name='load-meta'),
    path('login/', views.login, name='login'),
    path('register/', views.new_user, name='new-user'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('logout_view/', views.logout_view, name='logout'),
    path('login-process', views.login_process, name='login_process'),
    path('finder/', views.finder, name='finder'),

]
