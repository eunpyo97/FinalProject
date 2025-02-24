# # 1. Python 3.10을 기반 이미지로 사용
# FROM python:3.10

# # 2. 컨테이너 내부 작업 디렉터리 설정
# WORKDIR /app

# # 최신 pip 설치
# RUN pip install --upgrade pip setuptools

# # 4. 의존성 파일 복사 및 설치
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # 5. Flask 애플리케이션 코드 복사
# COPY . .

# # 6. 환경 변수 설정 (Flask 실행을 위해 필요)
# ENV FLASK_APP=app.py
# ENV FLASK_RUN_HOST=0.0.0.0
# ENV FLASK_RUN_PORT=5000
# ENV PYTHONUNBUFFERED=1

# # 7. 컨테이너 실행 시 Flask 서버 시작
# CMD ["python", "app.py"]
