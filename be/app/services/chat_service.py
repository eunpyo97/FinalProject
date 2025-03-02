import pymongo
from bson import ObjectId
from werkzeug.exceptions import NotFound, BadRequest
from app.database import mongo
from app.services.rag_service import retrieve_relevant_documents
from app.services.llm_service import generate_response
from app.models.chat import save_chat
from datetime import datetime, timezone, timedelta
from flask import current_app
import uuid
from flask import jsonify
import logging
from app.services.emotion_service import get_emotion_results
from pytz import timezone  
KST = timezone('Asia/Seoul') 


def chat_with_bot(user_id: str, chatroom_id: str, user_message: str, emotion_id=None, confidence=None, test_mode=False) -> dict:
  
    """
    사용자의 메시지를 받아 RAG 검색 및 LLM을 이용해 챗봇 응답을 생성하는 함수

    :param user_id: 사용자의 고유 ID
    :param chatroom_id: 현재 채팅방의 ID
    :param user_message: 사용자의 입력 메시지
    :param emotion_id: 감정 분석 결과 ID
    :param test_mode: test_mode=True로 설정하면 DB에 저장하지 않고 응답만 반환 (기본값 False)
    :return: 챗봇 응답 JSON
    """
    try:
        # user_id가 없거나 빈 문자열이면 테스트 모드로 전환 및 기본 user_id 할당
        if not user_id or user_id == "":
            test_mode = True
            user_id = "test_user"

        if mongo.db is None:
            raise RuntimeError("MongoDB가 올바르게 초기화되지 않았습니다.")
        
        # RAG 검색 수행 (관련 상담 사례 검색)
        retrieved_documents = retrieve_relevant_documents(user_message)

        # 검색 결과 처리
        if retrieved_documents:
            retrieved_context = "\n".join(
                doc.metadata["output"].strip() if "output" in doc.metadata else str(doc)
                for doc in retrieved_documents
            )
            retrieved_status = "반영됨"
        else:
            retrieved_context = "상담 기록이 없습니다."
            retrieved_status = "반영 안 됨"

        # LLM을 활용하여 최종 챗봇 응답 생성
        bot_response, emotion, confidence, emotion_id = generate_response(user_id, chatroom_id, user_message, retrieved_context)

        # 대화 내용 저장 (테스트 모드일 경우 DB 저장 건너뜀)
        if not test_mode:
            chat_data = save_chat(user_id, chatroom_id, user_message, bot_response, emotion_id, False, confidence)
            chat_id = str(chat_data)
        else:
            chat_id = "test_chat_id"

        return {
            "user_message": user_message,
            "retrieved_documents": retrieved_status,
            "bot_response": bot_response,
            "chat_id": chat_id,
            "emotion": emotion,
            "confidence": confidence,
            "emotion_id": emotion_id
        }

    except pymongo.errors.PyMongoError as e:
        raise RuntimeError(f"MongoDB 오류 발생: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"챗봇 응답 생성 중 오류 발생: {str(e)}")


def get_chat_history(chatroom_id: str, limit: int = 10) -> list:
    """
    특정 채팅방의 대화 기록 조회

    :param chatroom_id: 조회할 채팅방 ID
    :param limit: 가져올 대화 개수 (기본값: 10)
    :return: 대화 목록
    """
    try:
        with current_app.app_context():  
            chats = mongo.db.chats.find({"chatroom_id": chatroom_id}).sort("timestamp", -1).limit(limit)
            history = [{"_id": str(chat["_id"]), **chat} for chat in chats]
            return history
    except pymongo.errors.PyMongoError as e:
        raise RuntimeError(f"MongoDB 조회 오류: {str(e)}")


def end_chatroom(user_id: str, chatroom_id: str) -> dict:
    """
    사용자의 채팅방을 종료하는 함수
    :param user_id: 사용자 ID
    :param chatroom_id: 채팅방 ID
    :return: 종료된 채팅방에 대한 메시지
    """
    try:
        chatroom = mongo.db.chatrooms.find_one({"chatroom_id": chatroom_id, "user_id": user_id})
        
        if not chatroom:
            raise NotFound(f"사용자의 채팅방을 찾을 수 없습니다.")
        
        if chatroom.get("conversation_end"):
            return {"message": "이미 종료된 채팅방입니다."}
        
        kst_now = datetime.now(KST)

        result = mongo.db.chatrooms.update_one(
            {"chatroom_id": chatroom_id},
            {
                "$set": {
                    "conversation_end": True,
                    "conversation_end_timestamp": kst_now.isoformat()  
                }
            }
        )
        print(f"[DEBUG] update result: {result.modified_count}")
        
        if result.modified_count == 0:
            return {"error": f"채팅방 {chatroom_id}을 찾을 수 없습니다."}
        
        return {"message": "채팅방 종료 완료"}
    
    except NotFound as e:
        print(f"[ERROR] 채팅방 종료 오류 (user_id={user_id}, chatroom_id={chatroom_id}): {e}")
        return {"error": str(e)}
    
    except Exception as e:
        print(f"[ERROR] 채팅방 종료 중 오류 발생 (user_id={user_id}, chatroom_id={chatroom_id}): {e}")
        return {"error": "서버 내부 오류"}


def get_chat_end_status_service(user_id, chatroom_id):
    """
    특정 채팅방의 종료 상태와 감정 데이터 조회
    :param user_id: 사용자 ID
    :param chatroom_id: 채팅방 ID
    :return: 채팅방 종료 상태 및 감정 데이터
    """
    try:
        chatroom = mongo.db.chatrooms.find_one({"chatroom_id": chatroom_id, "user_id": user_id})

        if not chatroom:
            return {"error": "채팅방을 찾을 수 없습니다."}, 404

        # 대화 종료 상태 확인
        conversation_end = chatroom.get("conversation_end", False)
        # 대화가 종료된 경우 종료 타임스탬프를 반환, 없으면 None 반환
        conversation_end_timestamp = chatroom.get("conversation_end_timestamp") if conversation_end else None

        # 대화가 종료된 경우 감정 데이터 조회
        emotion_data = {"emotions": [], "most_common": {"emotion": "default", "confidence": 0}}
        if conversation_end:
            emotion_data = get_emotion_results(chatroom_id, user_id)
            # 감정 데이터가 없거나 리스트 형태가 아닐 경우 대비
            if "emotions" not in emotion_data or not isinstance(emotion_data["emotions"], list):
                emotion_data["emotions"] = []

        return {
            "chatroom_id": chatroom_id,
            "conversation_end": conversation_end,
            "conversation_end_timestamp": conversation_end_timestamp,
            "emotions": emotion_data["emotions"] 
        }, 200

    except Exception as e:
        print(f"[ERROR] 대화 종료 상태 조회 오류: {e}")
        return {"error": "서버 내부 오류"}, 500


    except Exception as e:
        print(f"[ERROR] 대화 종료 상태 조회 오류: {e}")
        return {"error": "서버 내부 오류"}, 500


def create_chatroom(user_id: str) -> str:
    """
    새로운 채팅방 생성하는 함수
    :param user_id: 사용자의 고유 ID
    :return: 생성된 채팅방 ID
    """
    try:
        chatroom_id = str(uuid.uuid4())
        # UTC → KST 변환
        timestamp = datetime.now(KST).strftime("%Y%m%d%H%M%S")  
        
        chatroom_data = {
            "user_id": user_id,
            "chatroom_id": chatroom_id,
            "timestamp": timestamp,
            "conversation_end": False
        }

        mongo.db.chatrooms.insert_one(chatroom_data)

        print(f"[DEBUG] 채팅방 생성 완료 - chatroom_id: {chatroom_id}, user_id: {user_id}")
        return chatroom_id

    except Exception as e:
        print(f"채팅방 생성 중 오류 발생: {e}")
        raise RuntimeError(f"채팅방 생성 중 오류 발생: {e}")


def get_user_chat_history(user_id: str) -> list:
    """
    특정 사용자의 모든 채팅방을 조회하는 함수
    :param user_id: 사용자의 고유 ID
    :return: 사용자의 채팅방 목록
    """
    try:
        chatrooms = list(mongo.db.chatrooms.find({"user_id": user_id}))

        if not chatrooms:
            print(f"[DEBUG] 사용자 {user_id}의 기존 채팅방이 없음.")
            return []

        result = []
        for chatroom in chatrooms:
            timestamp = chatroom.get("timestamp")

            # timestamp가 문자열이라면 datetime 객체로 변환
            if isinstance(timestamp, str) and len(timestamp) == 14:
                timestamp = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
            
            # 디버깅 로그 추가
            print(f"[DEBUG] 채팅방 ID: {chatroom['chatroom_id']}, timestamp: {timestamp}")

            result.append({
                "chatroom_id": chatroom["chatroom_id"],
                "timestamp": timestamp.isoformat() if timestamp else None,  # ISO 형식 변환
                "conversation_end": chatroom["conversation_end"],
                "updated_at": chatroom.get("updated_at")
            })

        return result

    except Exception as e:
        print(f"[ERROR] 채팅방 조회 오류 (user_id={user_id}): {e}")
        raise RuntimeError("채팅방 조회 중 오류가 발생했습니다.")


def add_chat(user_id, chatroom_id, user_message, bot_response, emotion_id=None, confidence=None, conversation_end=False):
    """
    채팅방에 메시지 추가

    :param user_id: 사용자의 고유 ID
    :param chatroom_id: 채팅방 ID
    :param user_message: 사용자의 메시지
    :param bot_response: 챗봇의 응답
    :param emotion_id: 감정 분석 ID
    :param confidence: 감정 분석 신뢰도
    :param conversation_end: 채팅 종료 여부
    :return: 성공 여부
    """
    if mongo.db is None:
        raise RuntimeError("MongoDB 연결이 설정되지 않았습니다.") 

    try:
        if not isinstance(chatroom_id, str) or not is_valid_uuid(chatroom_id):
            raise ValueError("유효하지 않은 chatroom_id입니다.")
        
        kst_now = datetime.now(KST)

        chat_data = {
            "user_id": user_id,
            "user_message": user_message,
            "bot_response": bot_response,
            "emotion_id": emotion_id,
            "confidence": confidence,
            "conversation_end": conversation_end,
            "timestamp": kst_now.isoformat(),  
        }
        
        existing_chatroom = mongo.db.chatrooms.find_one({"chatroom_id": chatroom_id})

        # 채팅방이 없으면 새로운 채팅방 생성
        if not existing_chatroom:
            print(f"새로운 채팅방 생성: {chatroom_id}")
            chatroom_data = {
                "user_id": user_id,
                "chatroom_id": chatroom_id,
                "chats": [chat_data],
                "created_at": kst_now.isoformat(),  
                "updated_at": kst_now.isoformat(),  
                "conversation_end": conversation_end
            }
            mongo.db.chatrooms.insert_one(chatroom_data)
        else:
            # 기존 채팅방에 메시지 추가
            update_result = mongo.db.chatrooms.update_one(
                {"chatroom_id": chatroom_id},
                {
                    "$push": {"chats": chat_data},
                    "$set": {
                        "updated_at": kst_now.isoformat(), 
                        "conversation_end": conversation_end
                    }
                }
            )

            if update_result.modified_count == 0:
                raise ValueError("메시지 추가 실패")
            
        # conversation_end가 True이면 채팅방 종료 처리 호출
        if conversation_end:
            end_chatroom(chatroom_id)

        return True

    except Exception as e:
        print(f"채팅 추가 중 오류 발생: {str(e)}")
        raise


def delete_chat_message(message_id: str) -> bool:
    """
    특정 메시지를 삭제하는 함수

    :param message_id: 삭제할 메시지의 ObjectId
    :return: 삭제 성공 여부
    """
    try:
        result = mongo.db.chats.delete_one({"_id": ObjectId(message_id)})
        if result.deleted_count > 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"메시지 삭제 중 오류 발생: {str(e)}")
        raise


def is_valid_uuid(uuid_string):
    """
    유효한 UUID인지 확인하는 함수

    :param uuid_string: 검사할 문자열
    :return: 유효한 UUID이면 True, 아니면 False
    """
    try:
        uuid_obj = uuid.UUID(uuid_string)
        return str(uuid_obj) == uuid_string
    except ValueError:
        return False
    

def handle_message(user_id, chatroom_id, user_message, bot_response, conversation_end):
    chatroom_data = mongo.db.chatrooms.find_one({"chatroom_id": chatroom_id})
    
    if chatroom_data is None:
        chatroom_data = {
            'user_id': user_id,
            'chatroom_id': chatroom_id,
            'conversation_end': conversation_end,
            'messages': []  
        }
        mongo.db.chatrooms.insert_one(chatroom_data) 

    try:
        mongo.db.chatrooms.update_one(
            {"chatroom_id": chatroom_id},
            {"$push": {
                "messages": {
                    'user_message': user_message,
                    'bot_response': bot_response,
                    'conversation_end': conversation_end
                }
            }}
        )
    except Exception as e:
        print(f"MongoDB 삽입 오류: {e}")
        return jsonify({"error": "Failed to save the chat."}), 500
    
    return jsonify({"message": "Chat successfully saved."}), 200


def get_chat_history(user_id, limit=10):
    """
    특정 사용자가 속한 모든 채팅방의 대화 기록을 가져오는 함수

    :param user_id: 조회할 사용자의 user_id
    :param limit: 가져올 대화의 수 (기본값: 10)
    :return: 대화 기록 리스트
    """
    try:
        chatrooms = mongo.db.chatrooms.find({"user_id": user_id})

        if not chatrooms:
            raise NotFound(f"사용자의 채팅방을 찾을 수 없습니다.")

        chat_history = []
        for chatroom in chatrooms:
            chatroom_id = chatroom.get("chatroom_id")
            chats = chatroom.get("chats", [])

            # 각 채팅방에서 최대 limit 개수의 대화만 가져옴
            chat_history.extend([
                {
                    "chatroom_id": chatroom_id,
                    "user_message": chat.get("user_message"),
                    "bot_response": chat.get("bot_response"),
                    "timestamp": chat.get("timestamp")
                }
                for chat in chats[-limit:]
            ])

        # 대화 기록이 많은 경우, limit 개수만큼 최근 대화만 반환
        return chat_history[-limit:]

    except NotFound as e:
        print(f"[ERROR] 채팅방 조회 오류: {e}")
        raise e
    except Exception as e:
        print(f"[ERROR] 대화 기록 조회 중 오류 발생: {e}")
        raise RuntimeError("대화 기록 조회 중 오류 발생")


def get_user_chatroom_history(user_id, chatroom_id, limit):
    """특정 사용자의 특정 채팅방 대화 기록을 조회"""
    try:
        # print(f"[DEBUG] user_id: {user_id}, chatroom_id: {chatroom_id}")  
        chatroom = mongo.db.chatrooms.find_one(
            {"user_id": user_id, "chatroom_id": chatroom_id}
        )
        
        if not chatroom:
            raise NotFound(f"사용자의 채팅방을 찾을 수 없습니다.")
        
        chats = chatroom.get("chats", [])
        conversation_end = chatroom.get("conversation_end", False)
        
        return {"chats": chats[-limit:], "conversationEnd": conversation_end}

    except Exception as e:
        print(f"[ERROR] 대화 기록 조회 오류: {e}")
        raise


def delete_chatroom_service(user_id: str, chatroom_id: str) -> bool:
    """
    특정 사용자의 채팅방을 삭제하는 서비스 로직
    :param user_id: 사용자 ID
    :param chatroom_id: 삭제할 채팅방 ID
    :return: 삭제 성공 여부 (True/False)
    """
    try:
        result = mongo.db.chatrooms.delete_one({"user_id": user_id, "chatroom_id": chatroom_id})
        
        # 삭제된 문서가 없는 경우
        if result.deleted_count == 0:
            raise NotFound("채팅방을 찾을 수 없습니다.")
        
        return True

    except NotFound as e:
        logging.error(f"[ERROR] 채팅방 삭제 오류 (user_id={user_id}, chatroom_id={chatroom_id}): {e}")
        return False

    except Exception as e:
        logging.error(f"[ERROR] 채팅방 삭제 중 예기치 않은 오류 발생 (user_id={user_id}, chatroom_id={chatroom_id}): {e}")
        return False
    
def search_chatrooms(user_id: str, query: str) -> list:
    """
    사용자의 채팅방을 검색하는 서비스 로직
    :param user_id: 사용자 ID
    :param query: 검색어
    :return: 검색된 채팅방 목록
    """
    try:
        if not query.strip():
            raise BadRequest("검색어가 비어 있습니다.")

        chatrooms = list(mongo.db.chatrooms.find({
            "user_id": user_id,
            "$or": [
                {"chatroom_id": {"$regex": query, "$options": "i"}},
                {"chats": {"$elemMatch": {"user_message": {"$regex": ".*" + query + ".*", "$options": "i"}}}}
            ]
        }))

        result = [
            {
                "chatroom_id": chatroom["chatroom_id"],
                "timestamp": chatroom["timestamp"],
                "conversation_end": chatroom["conversation_end"]
            }
            for chatroom in chatrooms
        ]

        print(f"[DEBUG] 검색 결과: {result}") 
        return result

    except BadRequest as e:
        logging.error(f"[ERROR] 채팅방 검색 오류 (user_id={user_id}, query={query}): {e}")
        raise e

    except Exception as e:
        logging.error(f"[ERROR] 채팅방 검색 중 예기치 않은 오류 발생 (user_id={user_id}, query={query}): {e}")
        raise e
    
def modify_message_based_on_emotion(user_message, emotion_label):
    """감정에 맞는 사용자 메시지 수정"""
    if emotion_label == "sadness":
        return f"이해해, 많이 힘들지? {user_message}"
    elif emotion_label == "happy":
        return f"오! 기분 좋아 보이네! {user_message}"
    return user_message

def modify_response_with_emotion(response, emotion_label, confidence):
    """감정에 맞는 챗봇 응답 수정"""
    if confidence >= 0.7:
        if emotion_label == "sadness":
            response = f"정말 힘든 일이 있었나봐... {response}"
        elif emotion_label == "happy":
            response = f"기분이 좋은 것 같아서 나도 행복해! {response}"
    return response