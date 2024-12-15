from django.views.generic import TemplateView
from .models import CongestionData


class IndexView(TemplateView):
    template_name = 'main/index.html'  # 템플릿 경로 지정

    def get_context_data(self, **kwargs):
        # 템플릿에 전달할 데이터 정의
        context = super().get_context_data(**kwargs)
        context['congestion_data'] = CongestionData.objects.select_related('stop').order_by('-timestamp')[:10]
        return context


class DashboardView(TemplateView):
    template_name = 'main/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['congestion_data'] = CongestionData.objects.select_related('stop').order_by('-timestamp')[:10]
        return context

class DashboardMapView(TemplateView):
    template_name = 'main/dashboard_map.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # context['congestion_data'] = CongestionData.objects.select_related('stop').order_by('-timestamp')[:10]
    #     return context