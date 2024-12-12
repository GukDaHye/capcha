from django.contrib import admin
from .models import User, BusStop, CongestionData, SystemLog, Notification

admin.site.register(User)
admin.site.register(BusStop)
admin.site.register(CongestionData)
admin.site.register(SystemLog)
admin.site.register(Notification)
