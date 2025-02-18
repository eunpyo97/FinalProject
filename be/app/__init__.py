from flask import Flask
from config.settings import ActiveConfig
from app.database import init_db  # MySQL 초기화
from app.models import init_models  # 모델 초기화
from app.routes import register_routes  # 라우트 등록
from app.utils.error_handler import register_error_handlers  # 에러 핸들러 등록
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS  # CORS 지원 추가
from flask_mail import Mail

mail = Mail()

def create_app():
    """Flask 애플리케이션 팩토리 함수"""
    app = Flask(__name__)

    # 환경 변수 적용
    app.config.from_object(ActiveConfig)

    # CORS 활성화 (Swagger UI와 API 간 요청 문제 해결)
    CORS(app)

    # 데이터베이스 초기화
    init_db(app)

    # 모델 초기화
    init_models()

    # 라우트 등록
    register_routes(app)

    # 에러 핸들러 등록
    register_error_handlers(app)

    # Flask-Mail 초기화
    mail.init_app(app)

    # ActiveConfig에서 Swagger 설정 가져오기
    SWAGGER_URL = app.config["SWAGGER_UI_URL"]
    API_URL = app.config["SWAGGER_API_DOCS"]

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL, 
        API_URL,
        config={
            "app_name": "RobotPet API",
            "validatorUrl": None,  # Swagger UI 자체 검증 사용 안 함
            "displayRequestDuration": True,  # 요청 시간 표시
            "tryItOutEnabled": True,  # "Try it out" 버튼 활성화
            "jsonEditor": True  # JSON 편집 가능하게 설정
        }
    )

    # Swagger UI 블루프린트 등록
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
