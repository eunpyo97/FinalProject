import pymongo
from app.database import mongo
from datetime import datetime
from app.models.diary import Diary

# 대화 내용 요약 API
# def generate_summary(chatroom_id):
#     """
#     대화 내용을 요약하여 일기 형식으로 생성
#     OpenAI API 호출 및 요약 생성 로직 추가
#     """
#     try:
#         summary = "This is a sample summary generated from the chatroom content."
#         return summary
#     except Exception as e:
#         return f"요약 생성 중 오류 발생: {str(e)}", 500

# 일기장 저장 API
def create_diary(user_id, content, date, emotion, summary=None):
    """
    새 일기 저장
    """
    try:
        diary_data = {
            "user_id": user_id,
            "content": content,
            "date": date,
            "emotion": emotion,
            "summary": summary,
            "created_at": datetime.utcnow()  # 작성 날짜
        }
        result = mongo.db.diaries.insert_one(diary_data)
        return result.inserted_id is not None  # 삽입 성공 여부 반환
    except Exception as e:
        raise Exception(f"일기 저장 중 오류 발생: {str(e)}")
    
# 달력 이모지 표시 API
def create_calendar_emoji(user_id, date, emotion_emoji):
    """
    달력에 감정 이모지 표시
    """
    try:
        emoji_data = {
            "user_id": user_id,
            "date": date,
            "emotion_emoji": emotion_emoji,
            "created_at": datetime.utcnow()
        }
        result = mongo.db.calendar_emojis.insert_one(emoji_data)
        return result.inserted_id is not None  # 삽입 성공 여부 반환
    except Exception as e:
        raise Exception(f"이모지 설정 중 오류 발생: {str(e)}")

# 일기 목록 조회 API
def get_diary_list(user_id, date):
    """
    특정 날짜에 작성된 일기 목록 조회
    """
    try:
        diaries = mongo.db.diaries.find({"user_id": user_id, "date": date})
        return [diary for diary in diaries]  # 일기 목록 반환
    except Exception as e:
        raise Exception(f"일기 목록 조회 중 오류 발생: {str(e)}")

# 일기 상세 조회 API
def get_diary_detail(diary_id):
    """
    일기 상세 조회
    """
    try:
        diary = mongo.db.diaries.find_one({"_id": diary_id})
        if diary:
            return diary
        return None  # 일기가 없는 경우 None 반환
    except Exception as e:
        raise Exception(f"일기 상세 조회 중 오류 발생: {str(e)}")

# 일기 삭제 API
def delete_diary(diary_id):
    """
    일기 삭제
    """
    try:
        result = mongo.db.diaries.delete_one({"_id": diary_id})
        return result.deleted_count > 0  # 삭제 성공 여부 반환
    except Exception as e:
        raise Exception(f"일기 삭제 중 오류 발생: {str(e)}")

# 일기 수정 API
def update_diary(diary_id, new_content, new_emotion):
    """
    일기 수정
    """
    try:
        result = mongo.db.diaries.update_one(
            {"_id": diary_id},
            {"$set": {"content": new_content, "emotion": new_emotion}}
        )
        return result.modified_count > 0  # 수정 성공 여부 반환
    except Exception as e:
        raise Exception(f"일기 수정 중 오류 발생: {str(e)}")

# 일기 검색 API
def search_diary_by_keyword(user_id, keyword):
    """
    일기 내용 검색
    """
    try:
        diaries = mongo.db.diaries.find({
            "user_id": user_id,
            "content": {"$regex": keyword, "$options": "i"}  # 대소문자 구분 없이 검색
        })
        return [diary for diary in diaries]  # 검색 결과 반환
    except Exception as e:
        raise Exception(f"일기 검색 중 오류 발생: {str(e)}")

# 새 일기 작성 API
def create_diary(user_id, content, emotion):
    """
    새 일기 작성
    """
    try:
        diary_data = {
            "user_id": user_id,
            "content": content,
            "emotion": emotion,
            "created_at": datetime.utcnow()  # 작성 날짜
        }
        result = mongo.db.diaries.insert_one(diary_data)
        return result.inserted_id  # 삽입된 일기 ID 반환
    except Exception as e:
        raise Exception(f"새 일기 작성 중 오류 발생: {str(e)}")