import pymongo
from app.database import mongo
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import pytz  
import logging

# 한국 표준시(KST) 정의
KST = pytz.timezone("Asia/Seoul")

# 일기장 저장
def create_diary(user_id, chatroom_id, content, date, emotion, summary=None):
    """
    새 일기 저장
    :param user_id: 사용자 ID
    :param chatroom_id: 채팅방 ID
    :param content: 일기 내용
    :param date: 작성 날짜 (무시됨, 현재 KST 날짜가 사용됨)
    :param emotion: 감정
    :param summary: 요약 (선택 사항)
    """
    try:
        # 항상 현재 KST 시간을 기준으로 함
        kst_now = datetime.now(KST)
        kst_date = kst_now.strftime("%Y-%m-%d")  # YYYY-MM-DD 형식

        diary_data = {
            "user_id": user_id,
            "chatroom_id": chatroom_id,
            "content": content,
            "date": kst_date,  
            "emotion": emotion,
            "summary": summary if summary is not None else None,
            "created_at": kst_now.isoformat(), 
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
    :param date: 날짜 (프론트엔드에서 전달된 날짜, KST 기준)
    :param chatroom_id: 특정 채팅방 ID (선택 사항)
    """
    try:
        if isinstance(date, str):
            date = datetime.fromisoformat(date).astimezone(KST)

        kst_date = date.replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d")

        query = {"user_id": user_id, "date": kst_date}

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
    :param diary_id: 일기 ID
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
    :param diary_id: 일기 ID
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
    :param diary_id: 일기 ID
    :param new_content: 수정된 일기 내용
    :param new_emotion: 수정된 감정
    :return: 수정 성공 여부 (True/False)
    """
    try:
        kst_now = datetime.now(KST).isoformat()

        result = mongo.db.diaries.update_one(
            {"_id": ObjectId(diary_id)},
            {
                "$set": {
                    "content": new_content,
                    "emotion": new_emotion,
                    "updated_at": kst_now,
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
    :param user_id: 사용자 ID
    :param keyword: 검색 키워드
    """
    try:
        diaries = mongo.db.diaries.find(
            {"user_id": user_id, "content": {"$regex": keyword, "$options": "i"}}
        )
        return [{**diary, "_id": str(diary["_id"])} for diary in diaries]
    except Exception as e:
        raise Exception(f"일기 검색 중 오류 발생: {str(e)}")