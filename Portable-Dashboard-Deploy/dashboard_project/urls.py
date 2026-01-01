"""
URL configuration for dashboard_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

# Customize admin site
admin.site.site_header = "KamFlow Admin"
admin.site.site_title = "KamFlow Admin Portal"
admin.site.index_title = "Welcome to KamFlow Admin Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('', RedirectView.as_view(url='dashboard/', permanent=True)),

    # AI Agent URLs
    path('ai/', include('ai_agent.urls')),

    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login', http_method_names=['get', 'post']), name='logout'),
]
