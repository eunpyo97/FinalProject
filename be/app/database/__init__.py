from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv
from flask import Flask, current_app

# 환경 변수 로딩
load_dotenv()

# SQLAlchemy (MySQL ORM)
db = SQLAlchemy()

# PyMongo (MongoDB) 
mongo = PyMongo()

def init_db(app):
    """Flask 앱에 DB 확장 적용"""
    print(f"MongoDB URI: {app.config.get('MONGO_URI')}") 

    app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get("SQLALCHEMY_DATABASE_URI")
    app.config["MONGO_URI"] = app.config.get("MONGO_URI")

    # MySQL 연결 초기화
    db.init_app(app)

    # MongoDB 설정 
    mongo.init_app(app)
    
    # Flask 앱 컨텍스트 내에서 MySQL 테이블 생성
    with app.app_context():
        try:
            db.create_all()
            print("MySQL 테이블 생성 성공!")
        except Exception as e:
            print(f"MySQL 테이블 생성 오류: {str(e)}")

    # MongoDB 연결 상태 확인
    try:
        if mongo.db is not None:  # None과 비교
            print("MongoDB 연결 성공!")
        else:
            print("MongoDB 연결 실패!")
    except Exception as e:
        print(f"MongoDB 연결 오류: {str(e)}")
        raise 

    return mongo