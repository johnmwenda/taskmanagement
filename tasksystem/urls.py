"""tasksystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from tasksystem.accounts.api import (
    views as accounts_api_views
)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v2/login/', accounts_api_views.UserSignInView.as_view(), name='login'),
    url(r'^api/v2/logout/', accounts_api_views.UserSignInView.as_view(), name='logout'),
    url(r'^api-auth/', include('rest_framework.urls')),
]
