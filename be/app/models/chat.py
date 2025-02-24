from datetime import datetime, timezone
from flask_pymongo import PyMongo
from pymongo import MongoClient

mongo = PyMongo()


def generate_chatroom_id(user_id):
    """새로운 대화 시작 시 자동으로 채팅방 ID 생성"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{user_id}_{timestamp}"


def end_previous_chatroom(user_id):
    """새로운 대화가 시작되면 기존 대화 자동 종료"""
    mongo.db.chats.update_many(
        {"user_id": user_id, "conversation_end": False},
        {"$set": {"conversation_end": True}},
    )


def auto_end_chatroom_by_date():
    """날짜가 바뀌면 미종료된 대화 자동 종료"""
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)

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
                "updated_at": datetime.now(timezone.utc),
            }
            mongo.db.chatrooms.insert_one(chatroom)  # MongoDB에 새로운 채팅방 저장

        # 채팅 데이터 생성
        chat_data = {
            "user_message": user_message,
            "bot_response": bot_response,
            "emotion_id": emotion_id,
            "confidence": confidence,
            "conversation_end": conversation_end,
            "timestamp": datetime.now(timezone.utc),
        }

        # 채팅방에 채팅 데이터 추가
        mongo.db.chatrooms.update_one(
            {"chatroom_id": chatroom_id},
            {"$push": {"chats": chat_data}},
        )

        # 채팅방의 업데이트 시간 기록
        mongo.db.chatrooms.update_one(
            {"chatroom_id": chatroom_id},
            {"$set": {"updated_at": datetime.now(timezone.utc)}}
        )

        # 디버깅을 위한 로그 추가
        print(f"채팅 데이터 저장됨: {chat_data}")
        print(f"저장된 채팅방 ID: {chatroom_id}")
        print(f"현재 채팅방의 채팅 개수: {len(chatroom['chats'])}")

        return {
            "message": "챗봇 대화가 성공적으로 저장되었습니다.",
            "chatroom_id": chatroom_id,
            "chats_count": len(chatroom["chats"]),
        }

    except Exception as e:
        # 예외 발생 시 오류 메시지 출력
        print(f"MongoDB 삽입 오류: {e}")
        raise RuntimeError(f"MongoDB 삽입 오류: {e}")
