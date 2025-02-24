from flask import Blueprint
from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.home_routes import home_bp
from app.routes.chat_routes import chat_bp
from app.routes.emotion_routes import emotion_bp
from app.routes.diary_routes import diary_bp

def register_routes(app):
    """Flask 앱에 모든 블루프린트(라우트) 등록"""
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")  
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(emotion_bp, url_prefix="/emotion")
    app.register_blueprint(diary_bp, url_prefix="/diary")