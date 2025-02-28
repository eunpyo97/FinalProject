from bson.errors import InvalidId
from datetime import datetime, timezone
from flask_pymongo import PyMongo
from flask import Flask
from bson.objectid import ObjectId

mongo = PyMongo()

class Diary:
    def __init__(
        self,
        user_id,
        chatroom_id,
        content,
        date,
        emotion,
        title=None,
        tag=None,
        created_at=None,
        updated_at=None,
        summary=None,
    ):
        self.user_id = user_id
        self.chatroom_id = chatroom_id
        self.content = content
        self.date = date
        self.emotion = emotion
        self.title = title
        self.tag = tag
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at
        self.summary = summary

    def to_dict(self):
        """
        Diary 객체를 딕셔너리로 변환 (MongoDB 저장용)
        """
        return {
            "user_id": self.user_id,
            "chatroom_id": self.chatroom_id,
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
            chatroom_id=data.get("chatroom_id", None),
            content=data["content"],
            date=data["date"],
            emotion=data["emotion"],
            title=data.get("title", None),
            tag=data.get("tag", None),
            created_at=data.get("created_at", datetime.now(timezone.utc)),
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
            diary_data = diary_data.to_dict()
        diary_data["created_at"] = datetime.now(timezone.utc)

        result = mongo.db.diaries.insert_one(diary_data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_user_and_date(user_id, date):
        """
        특정 사용자의 날짜별 일기 목록 조회
        :param user_id: 사용자 ID
        :param date: 날짜 (ISO 형식, 예: '2023-02-01')
        """
        diaries = mongo.db.diaries.find({"user_id": user_id, "date": date})
        return [{**diary, "_id": str(diary["_id"])} for diary in diaries]

    @staticmethod
    def get_by_id(diary_id):
        """
        일기 ID로 상세 조회
        :param diary_id: 일기 ID (문자열)
        """
        diary = mongo.db.diaries.find_one({"_id": ObjectId(diary_id)})
        if diary:
            diary["_id"] = str(diary["_id"])
            return diary
        return None

    @staticmethod
    def delete_by_id(diary_id):
        """
        일기 ID로 삭제
        :param diary_id: 일기 ID (문자열)
        """
        result = mongo.db.diaries.delete_one({"_id": ObjectId(diary_id)})
        return result.deleted_count > 0

    @staticmethod
    def update_by_id(diary_id, update_data):
        """
        일기 ID로 수정
        :param diary_id: 일기 ID (문자열)
        :param update_data: 수정할 데이터 (딕셔너리)
        """
        try:
            if not diary_id:
                return {"error": "diary_id가 필요합니다."}, 400

            diary_id = ObjectId(diary_id)

            if not update_data:
                return {"error": "업데이트할 데이터가 없습니다."}, 400

            update_data["updated_at"] = datetime.now(timezone.utc)

            result = mongo.db.diaries.update_one(
                {"_id": diary_id}, {"$set": update_data}
            )

            if result.modified_count > 0:
                return {"message": "일기 수정 성공!"}, 200
            return {"message": "변경된 내용이 없습니다."}, 400

        except InvalidId:
            return {"error": "올바르지 않은 diary_id입니다."}, 400
        except Exception as e:
            return {"error": f"일기 수정 중 오류 발생: {str(e)}"}, 500
