"""
URL configuration for lifenet project.

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
from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('',views.homepage_view,name='homepage'),
    path("admin/", admin.site.urls),
    path('accounts/', include(("accounts.urls","accounts"), namespace="accounts")),
    path('bloodbanks/',include("bloodbanks.urls", namespace="bloodbanks")),
    path('core/', include("core.urls", namespace="core")),
    path('users/',include("users.urls", namespace="users")),
    path('donors/',include("donors.urls", namespace="donors")),
    path('patient/',include("patients.urls", namespace="patients")),
    path('camp/',include("camp.urls", namespace="camp")),
    path('organizations/',include("organizations.urls", namespace="organizations")),
    path('inventory/',include("inventory.urls", namespace="inventory")),
]
if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
