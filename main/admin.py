from django.contrib import admin
from django.utils.html import format_html

from .models import User, BusStop, CongestionData, SystemLog, Notification

admin.site.register(User)
admin.site.register(BusStop)
class CongestionDataAdmin(admin.ModelAdmin):
    list_display = ('stop', 'timestamp', 'student_count', 'congestion_level', 'image_preview')  # Add `image_preview`

    def image_preview(self, obj):
        """
        Display the image thumbnail in the admin list view.
        """
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" style="max-height: 100px; max-width: 150px;" />')
        return "No Image"

    image_preview.short_description = "Image Preview"  # Custom column name in admin

admin.site.register(CongestionData, CongestionDataAdmin)
admin.site.register(SystemLog)
admin.site.register(Notification)
