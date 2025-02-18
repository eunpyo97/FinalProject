import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """기본 환경 설정"""

    # Flask 설정
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    
    # 관계형 DB (MySQL) 설정
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
        raise ValueError("환경 변수(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)가 설정되지 않았습니다.")
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MongoDB 설정
    # MONGO_URI = os.getenv("MONGO_URI")
    # if not MONGO_URI:
    #     raise ValueError("MongoDB 환경 변수(MONGO_URI)가 설정되지 않았습니다.")

    # 이메일 설정
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # 기본 URL 설정
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

    # Swagger 관련 설정
    SWAGGER_UI_URL = os.getenv("SWAGGER_UI_URL", "/api/docs")  # Swagger UI 기본 경로
    SWAGGER_API_DOCS = os.getenv("SWAGGER_API_DOCS", "/static/swagger.json")  # Swagger JSON 문서 경로


class ProductionConfig(Config):
    """배포 환경 설정"""
    DEBUG = False
    BASE_URL = os.getenv("PROD_BASE_URL", "https://your-production-domain.com")


class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    BASE_URL = os.getenv("DEV_BASE_URL", "http://localhost:3000")


# 환경 변수에 따라 설정 로드
FLASK_ENV = os.getenv("FLASK_ENV", "development")
if FLASK_ENV == "production":
    ActiveConfig = ProductionConfig
else:
    ActiveConfig = DevelopmentConfig

SECRET_KEY = os.getenv("SECRET_KEY", "your_jwt_secret_key")
