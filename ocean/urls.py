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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('admin_panel.urls')),
    path('community/', include('community.urls')),
    path('stream/', include('stream.urls')),
    path('api/', include('api.urls')),
    path('meeting/', include('meeting.urls')),
    path('inventory/', include('inventory.urls')),
    path('dolphine/', include('dolphine.urls')),
    path('cmms/', include('cmms.urls')),
    path('apiv2/', include('apiv2.urls')),
    path('blog/', include('blog.urls')),
    path('appscenter/', include('appscenter.urls')),
    path('reports/', include('reports.urls')),
    path('taskmanager/', include('taskmanager.urls')),
    path('retail/', include('retail.urls')),
    path('crm/', include('crm.urls')),
    path('servicing/', include('servicing.urls')),
    path('maintainance/', include('maintenance.urls'))

]
