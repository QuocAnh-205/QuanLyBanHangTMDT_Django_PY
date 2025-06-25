"""myweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from django.conf.urls import include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',include('myshop.urls')),
    path('admin/', admin.site.urls),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    # Các route khác nếu có
    path('login/', auth_views.LoginView.as_view(template_name='shop/login.html'), name='login'),
    # path('login/', user_login,),
    # path('api/',include('myapi.urls')),
    # path('myapp/',include('myapp.urls')),
    
]
