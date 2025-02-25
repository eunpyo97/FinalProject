from datetime import datetime
from flask_pymongo import PyMongo
from flask import Flask
from bson.objectid import ObjectId

mongo = PyMongo()

class Diary:
    def __init__(self, user_id, content, date, emotion, title=None, tag=None, created_at=None, updated_at=None, summary=None):
        self.user_id = user_id
        self.content = content
        self.date = date
        self.emotion = emotion
        self.title = title
        self.tag = tag
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at
        self.summary = summary  

    def to_dict(self):
        """
        Diary 객체를 딕셔너리로 변환
        """
        return {
            "user_id": self.user_id,
            "content": self.content,
            "date": self.date,
            "emotion": self.emotion,
            "title": self.title,
            "tag": self.tag,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "summary": self.summary,
        }

    @staticmethod
    def from_dict(data):
        """
        딕셔너리 데이터를 Diary 객체로 변환
        """
        return Diary(
            user_id=data["user_id"],
            content=data["content"],
            date=data["date"],
            emotion=data["emotion"],
            title=data.get("title", None),
            tag=data.get("tag", None),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", None),
            summary=data.get("summary", None),
        )

    @staticmethod
    def save(diary_data):
        """
        새 일기 저장
        :param diary_data: Diary 객체 또는 딕셔너리 형태의 데이터
        """
        if isinstance(diary_data, Diary):
            diary_data = diary_data.to_dict()  # Diary 객체라면 딕셔너리로 변환
        result = mongo.db.diaries.insert_one(diary_data)  # mongo.db 사용
        return str(result.inserted_id)  # 저장된 문서의 ID를 문자열로 반환

    @staticmethod
    def get_by_user_and_date(user_id, date):
        """
        특정 사용자의 날짜별 일기 목록 조회
        :param user_id: 사용자 ID
        :param date: 날짜 (ISO 형식, 예: '2023-02-01')
        """
        diaries = mongo.db.diaries.find({"user_id": user_id, "date": date})  # mongo.db 사용
        return [Diary.from_dict(diary) for diary in diaries]  

    @staticmethod
    def get_by_id(diary_id):
        """
        일기 ID로 상세 조회
        :param diary_id: 일기 ID (문자열)
        """
        diary = mongo.db.diaries.find_one({"_id": ObjectId(diary_id)})  # mongo.db 사용
        if diary:
            return Diary.from_dict(diary)  # Diary 객체로 변환
        return None

    @staticmethod
    def delete_by_id(diary_id):
        """
        일기 ID로 삭제
        :param diary_id: 일기 ID (문자열)
        """
        result = mongo.db.diaries.delete_one({"_id": ObjectId(diary_id)})  # mongo.db 사용
        return result.deleted_count > 0  

    @staticmethod
    def update_by_id(diary_id, update_data):
        """
        일기 ID로 수정
        :param diary_id: 일기 ID (문자열)
        :param update_data: 수정할 데이터 (딕셔너리)
        """
        result = mongo.db.diaries.update_one({"_id": ObjectId(diary_id)}, {"$set": update_data})  # mongo.db 사용
        return result.modified_count > 0  
