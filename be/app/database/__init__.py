from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo

# SQLAlchemy (MySQL ORM)
db = SQLAlchemy()

# PyMongo (MongoDB) 
mongo = PyMongo()

def init_db(app):
    """Flask 앱에 DB 확장 적용"""
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get("SQLALCHEMY_DATABASE_URI")
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # MySQL 연결 초기화
    db.init_app(app)

    # MongoDB 설정 - 사용시 주석 해제
    # 주석 해제 시 env 주석도 해제 필요
    # app.config["MONGO_URI"] = app.config.get("MONGO_URI")  
    # mongo.init_app(app)

    # Flask 앱 컨텍스트 내에서 MySQL 테이블 생성
    with app.app_context():
        db.create_all()
