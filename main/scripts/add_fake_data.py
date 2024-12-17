import os
import django
import random
from datetime import datetime, timedelta
from pathlib import Path

# Django 설정 불러오기
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from main.models import BusStop, CongestionData

# 경로 설정: 이미지 파일 저장 위치 (더미 이미지 사용)
BASE_DIR = Path(__file__).resolve().parent.parent  # 프로젝트 루트 경로
DUMMY_IMAGE_PATH = BASE_DIR / "dummy_image.jpg"  # 더미 이미지 경로

# 1. 더미 이미지 생성 (이미 존재하지 않는 경우)
if not DUMMY_IMAGE_PATH.exists():
    with open(DUMMY_IMAGE_PATH, "wb") as f:
        f.write(os.urandom(1024))  # 임의의 1KB 데이터 생성

# 2. 버스 정류장 추가
bus_stops = [
    {"name": "1번 버스", "capacity": 18},
    {"name": "2번 버스", "capacity": 22},
]

for stop_data in bus_stops:
    stop, created = BusStop.objects.get_or_create(name=stop_data["name"])
    stop.capacity = stop_data["capacity"]
    stop.save()
    print(f"Updated or created: {stop.name} with capacity {stop.capacity}")

# 3. 혼잡도 데이터 추가
for _ in range(50):  # 50개의 가상 데이터 생성
    stop = random.choice(BusStop.objects.all())
    student_count = random.randint(0, stop.capacity + 5)  # 초과 학생 수 포함
    congestion_level = (
        "Empty" if student_count <= stop.capacity // 2
        else "Moderate" if student_count <= stop.capacity
        else "High"
    )
    timestamp = datetime.now() - timedelta(minutes=random.randint(0, 1440))  # 최근 하루 데이터

    # 가상 이미지 파일 경로 설정
    fake_image_path = f"congestion_images/{stop.name}/image_{random.randint(1, 100)}.jpg"

    # CongestionData 생성
    CongestionData.objects.create(
        stop=stop,
        student_count=student_count,
        congestion_level=congestion_level,
        timestamp=timestamp,
        image=fake_image_path if random.choice([True, False]) else None  # 랜덤하게 이미지 포함
    )
    print(f"Added data for {stop.name}: {student_count} students ({congestion_level})")
