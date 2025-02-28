import pymongo
from app.database import mongo
from bson.objectid import ObjectId
from datetime import datetime, timedelta, timezone
import logging


# 일기장 저장
def create_diary(user_id, chatroom_id, content, date, emotion, summary=None):
    """
    새 일기 저장
    """
    try:
        # KST(한국 시간)으로 변환
        kst_now = datetime.now(timezone.utc) + timedelta(hours=9)

        # 만약 summary가 None이라면, content만 저장
        diary_data = {
            "user_id": user_id,
            "chatroom_id": chatroom_id,
            "content": content,
            "date": date,
            "emotion": emotion,
            "summary": (
                summary if summary is not None else None
            ),  # summary가 None일 경우 null로 저장
            "created_at": kst_now,
        }
        result = mongo.db.diaries.insert_one(diary_data)
        return str(result.inserted_id)
    except Exception as e:
        logging.error(f"[ERROR] 일기 저장 중 오류 발생: {str(e)}")
        raise Exception(f"일기 저장 중 오류 발생: {str(e)}")


# 일기 목록 조회
def get_diary_list(user_id, date, chatroom_id=None):
    """
    특정 날짜에 작성된 일기 목록 조회
    :param user_id: 사용자 ID
    :param date: 날짜
    :param chatroom_id: 특정 채팅방 ID
    """
    try:
        query = {"user_id": user_id, "date": date}

        if chatroom_id:
            query["chatroom_id"] = chatroom_id

        diaries_cursor = mongo.db.diaries.find(query)
        diaries = [
            {
                "_id": str(diary["_id"]),
                "user_id": diary["user_id"],
                "chatroom_id": diary.get("chatroom_id"),
                "content": diary["content"],
                "date": diary["date"],
                "emotion": diary.get("emotion"),
                "summary": diary.get("summary"),
                "created_at": diary["created_at"],
            }
            for diary in diaries_cursor
        ]

        return diaries
    except Exception as e:
        raise Exception(f"일기 목록 조회 중 오류 발생: {str(e)}")


# 일기 상세 조회
def get_diary_detail(diary_id):
    """
    일기 상세 조회
    """
    try:
        diary = mongo.db.diaries.find_one({"_id": ObjectId(diary_id)})
        if diary:
            diary["_id"] = str(diary["_id"])
            return diary
        return None
    except Exception as e:
        raise Exception(f"일기 상세 조회 중 오류 발생: {str(e)}")


# 일기 삭제
def delete_diary(diary_id):
    """
    일기 삭제
    """
    try:
        result = mongo.db.diaries.delete_one({"_id": ObjectId(diary_id)})
        return result.deleted_count > 0
    except Exception as e:
        raise Exception(f"일기 삭제 중 오류 발생: {str(e)}")


# 일기 수정
def update_diary(diary_id, new_content, new_emotion):
    """
    일기 수정
    """
    try:
        result = mongo.db.diaries.update_one(
            {"_id": ObjectId(diary_id)},
            {
                "$set": {
                    "content": new_content,
                    "emotion": new_emotion,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
        return result.modified_count > 0
    except Exception as e:
        raise Exception(f"일기 수정 중 오류 발생: {str(e)}")


# 일기 검색
def search_diary_by_keyword(user_id, keyword):
    """
    일기 내용 검색
    """
    try:
        diaries = mongo.db.diaries.find(
            {"user_id": user_id, "content": {"$regex": keyword, "$options": "i"}}
        )
        return [{**diary, "_id": str(diary["_id"])} for diary in diaries]
    except Exception as e:
        raise Exception(f"일기 검색 중 오류 발생: {str(e)}")
