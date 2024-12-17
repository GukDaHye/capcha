from django.urls import path

from main.uart_human_count import send_human_view
from main.uart_led_controlled import send_uart_sequence
from main.views import DashboardView, DashboardMapView, ObjectDetectionView

app_name = 'main'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/map/', DashboardMapView.as_view(), name='dashboard_map'),
    path('detect/', ObjectDetectionView.as_view(), name='object_detection'),
    path('send-human/', send_human_view, name='send_human'),
    path('send-count/', send_uart_sequence, name='send_uart_sequence'),

]
