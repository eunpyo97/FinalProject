import pymongo
from app.database import mongo
from datetime import datetime
from app.models.diary import Diary

# # 1. 대화 내용 요약 API
# def generate_summary(chatroom_id):
#     """대화 내용을 요약하여 일기 형식으로 생성"""
#     # 여기에 OpenAI API 호출 및 요약 생성 로직 추가
#     return generate_summary_from_chatroom(chatroom_id)

# 2. 일기장 저장 API
def create_diary(user_id, content, date, emotion, summary=None):
    """새 일기 저장"""
    diary = Diary(user_id, content, date, emotion, summary)
    return Diary.save(diary)

# 3. 달력 이모지 표시 API
def create_calendar_emoji(user_id, date, emotion_emoji):
    """달력에 감정 이모지 표시"""
    # 감정 이모지 관련 로직 처리
    return True  # 이모지 표시 성공적으로 처리

# 4. 일기 목록 조회 API
def get_diary_list(user_id, date):
    """특정 날짜에 작성된 일기 목록 조회"""
    diaries = Diary.get_by_user_and_date(user_id, date)
    return [diary for diary in diaries]

# 5. 일기 상세 조회 API
def get_diary_detail(diary_id):
    """일기 상세 조회"""
    diary = Diary.get_by_id(diary_id)
    if diary:
        return diary
    return None

# 6. 일기 삭제 API
def delete_diary(diary_id):
    """일기 삭제"""
    result = Diary.delete_by_id(diary_id)
    return result.deleted_count > 0

# 7. 일기 수정 API
def update_diary(diary_id, new_content, new_emotion):
    """일기 수정"""
    diary = Diary.get_by_id(diary_id)
    if diary:
        # 일기 수정 로직
        mongo.db.diaries.update_one({"_id": diary_id}, {"$set": {"content": new_content, "emotion": new_emotion}})
        return True
    return False

# 8. 일기 검색 API
def search_diary_by_keyword(user_id, keyword):
    """일기 내용 검색"""
    diaries = mongo.db.diaries.find({
        "user_id": user_id,
        "content": {"$regex": keyword, "$options": "i"}  # 대소문자 구분 없이 검색
    })
    return [diary for diary in diaries]

# 10. 새 일기 쓰기 API
def create_diary(user_id, content, emotion):
    """새 일기 작성"""
    # 새로운 일기 데이터 생성
    diary_data = {
        "user_id": user_id,
        "content": content,
        "emotion": emotion,
        "created_at": datetime.utcnow()  # 작성 날짜
    }
    
    result = mongo.db.diaries.insert_one(diary_data)
    return result.inserted_id  # 삽입된 일기 ID 반환
