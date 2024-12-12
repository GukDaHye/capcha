import os
import django
import random
from datetime import datetime, timedelta

# Django 설정 불러오기
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from main.models import BusStop, CongestionData

# 1. 버스 정류장 추가
bus_stops = [
    {"name": "1번 버스", "capacity": 18},
    {"name": "2번 버스", "capacity": 22},
]

for stop_data in bus_stops:
    stop, created = BusStop.objects.get_or_create(name=stop_data["name"])
    print(f"Created: {created}, Bus Stop: {stop.name}")

# 2. 혼잡도 데이터 추가
for _ in range(50):  # 50개의 가상 데이터 생성
    stop = random.choice(BusStop.objects.all())
    student_count = random.randint(0, stop.capacity + 5)  # 초과 학생 수 포함
    congestion_level = (
        "low" if student_count <= stop.capacity // 2
        else "medium" if student_count <= stop.capacity
        else "high"
    )
    timestamp = datetime.now() - timedelta(minutes=random.randint(0, 1440))  # 최근 하루 데이터

    CongestionData.objects.create(
        stop=stop,
        student_count=student_count,
        congestion_level=congestion_level,
        timestamp=timestamp
    )
    print(f"Added data for {stop.name}: {student_count} students ({congestion_level})")
