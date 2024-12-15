from django.urls import path

from main.views import DashboardView, DashboardMapView

app_name = 'main'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/map/', DashboardMapView.as_view(), name='dashboard_map'),
]
