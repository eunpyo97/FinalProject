from datetime import datetime
import pytz
from flask_pymongo import PyMongo
from pymongo import MongoClient

# 한국 표준시(KST) 정의
KST = pytz.timezone("Asia/Seoul")

mongo = PyMongo()


def generate_chatroom_id(user_id):
    """새로운 대화 시작 시 자동으로 채팅방 ID 생성"""
    timestamp = datetime.now(KST).strftime("%Y%m%d%H%M%S")
    return f"{user_id}_{timestamp}"


def end_previous_chatroom(user_id):
    """새로운 대화가 시작되면 기존 대화 자동 종료"""
    mongo.db.chats.update_many(
        {"user_id": user_id, "conversation_end": False},
        {"$set": {"conversation_end": True}},
    )


def auto_end_chatroom_by_date():
    """날짜가 바뀌면 미종료된 대화 자동 종료"""
    now = datetime.now(KST)
    today_start = datetime(now.year, now.month, now.day, tzinfo=KST)

    mongo.db.chats.update_many(
        {"conversation_end": False, "timestamp": {"$lt": today_start}},
        {"$set": {"conversation_end": True}},
    )


def save_chat(
    user_id: str,
    chatroom_id: str,
    user_message: str,
    bot_response: str,
    emotion_id=None,
    conversation_end=False,
    confidence=None,
):
    try:
        # MongoDB에서 채팅방 찾기
        chatroom = mongo.db.chatrooms.find_one({"chatroom_id": chatroom_id})

        if chatroom is None:
            # 채팅방이 없으면 새로 생성
            chatroom = {
                "user_id": user_id,
                "chatroom_id": chatroom_id,
                "chats": [],
                "updated_at": datetime.now(KST),
            }
            mongo.db.chatrooms.insert_one(chatroom)

        # 채팅 데이터 생성
        chat_data = {
            "user_message": user_message,
            "bot_response": bot_response,
            "emotion_id": emotion_id,
            "confidence": confidence,
            "conversation_end": conversation_end,
            "timestamp": datetime.now(KST),
        }

        # 채팅방에 채팅 데이터 추가
        mongo.db.chatrooms.update_one(
            {"chatroom_id": chatroom_id},
            {"$push": {"chats": chat_data}},
        )

        # 채팅방의 업데이트 시간 기록
        mongo.db.chatrooms.update_one(
            {"chatroom_id": chatroom_id},
            {"$set": {"updated_at": datetime.now(KST)}},
        )

        print(f"채팅 데이터 저장됨: {chat_data}")
        print(f"저장된 채팅방 ID: {chatroom_id}")
        print(f"현재 채팅방의 채팅 개수: {len(chatroom['chats'])}")

        return {
            "message": "챗봇 대화가 성공적으로 저장되었습니다.",
            "chatroom_id": chatroom_id,
            "chats_count": len(chatroom["chats"]),
        }

    except Exception as e:
        print(f"MongoDB 삽입 오류: {e}")
        raise RuntimeError(f"MongoDB 삽입 오류: {e}")
