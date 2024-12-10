# Python 이미지 사용
FROM python:3.11-slim

# 작업 디렉터리 설정
WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 소스코드 복사
COPY . /app/

# 포트 열기
EXPOSE 8000

# 기본 명령어 설정
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

