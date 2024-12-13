from django.urls import path

from main.views import DashboardView

app_name = 'main'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),  # 'dashboard' 이름 부여
]
