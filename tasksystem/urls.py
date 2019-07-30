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
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from rest_framework import routers

from tasksystem.tasks.api import (
    views as tasks_api_views
)
from tasksystem.accounts.api import (
    views as accounts_api_views
)
# /api/v2 - django rest framework
router = routers.DefaultRouter()

# tasks app
router.register(r'tasks', tasks_api_views.TaskViewSet, base_name='tasks')


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v2/login/', accounts_api_views.UserSignInView.as_view(), name='login'),
    url(r'^api/v2/logout/', accounts_api_views.UserSignoutView.as_view(), name='logout'),
    url(r'^api/v2/signup', accounts_api_views.UserSignUpView.as_view(), name='signup'),
    url(r'^api/v2/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]