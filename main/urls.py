from django.urls import path

from main.uart_human_count import send_human
from main.views import DashboardView, DashboardMapView, ObjectDetectionView

app_name = 'main'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/map/', DashboardMapView.as_view(), name='dashboard_map'),
    path('detect/', ObjectDetectionView.as_view(), name='object_detection'),
    path('send-human/', send_human, name='send_human'),

]
