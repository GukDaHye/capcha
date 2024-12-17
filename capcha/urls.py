"""
URL configuration for capcha project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import path, include

from capcha import settings
from main.views import IndexView

admin.site.site_header = _("CMS 무당이 교통 혼잡도")  # Admin 페이지 상단 제목
admin.site.site_title = _("Bus Congestion Admin Portal")     # 브라우저 탭 제목
admin.site.index_title = _("Welcome to the Bus Congestion Admin Panel")  # Index 페이지 제목

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('detect/', detect_objects, name='detect_objects'),
    path('', include('main.urls')),
    path('', IndexView.as_view(), name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
