from django.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    preferences = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class BusStop(models.Model):
    stop_id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=200, blank=True, null=True)  # GPS 좌표, optional
    name = models.CharField(max_length=100)
    capacity = models.IntegerField(default=0)  # 새 필드 추가: 버스 정원의 최대값

    def __str__(self):
        return self.name

class CongestionData(models.Model):
    record_id = models.AutoField(primary_key=True)
    stop = models.ForeignKey(BusStop, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    student_count = models.IntegerField()
    congestion_level = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.stop.name} - {self.congestion_level} at {self.timestamp}"


class SystemLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    event_type = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stop = models.ForeignKey(BusStop, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return f"Notification for {self.user.name} - {self.message[:20]}"
