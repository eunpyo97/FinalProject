from flask import Blueprint
from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.home_routes import home_bp

def register_routes(app):
    """Flask 앱에 모든 블루프린트(라우트) 등록"""
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")  
    app.register_blueprint(user_bp, url_prefix="/users")