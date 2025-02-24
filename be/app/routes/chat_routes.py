from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from functools import wraps
from app.services.chat_service import (
    save_chat, 
    get_chat_history, 
    end_chatroom,
    create_chatroom, 
    get_user_chat_history, 
    delete_chat_message,
    chat_with_bot,
    add_chat,
    handle_message,
    get_user_chatroom_history,
    delete_chatroom_service,
    search_chatrooms
)
from app.services.rag_service import preview_rag_search
from app.utils.auth import jwt_required_without_bearer, login_required
import logging


logging.basicConfig(level=logging.INFO) 


chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chatroom", methods=["POST"])
@jwt_required_without_bearer 
def create_new_chatroom():
    """새로운 채팅방 생성"""
    user_id = request.user_id  # jwt_required_without_bearer 데코레이터에서 user_id가 자동으로 추가됨

    logging.info(f"인증된 사용자 ID: {user_id}") 

    chatroom_id = create_chatroom(user_id)  
    return jsonify({"chatroom_id": chatroom_id}), 201



@chat_bp.route("/message", methods=["POST"])
@jwt_required_without_bearer  
def create_chat():
    """새로운 챗봇 대화 저장"""
    try:
        user_id = request.user_id  
        if not user_id:
            return jsonify({"error": "인증이 필요합니다."}), 401

        data = request.get_json()
        if not data:
            raise BadRequest("JSON 데이터를 전달해야 합니다.")

        chatroom_id = data.get("chatroom_id")
        user_message = data.get("user_message")
        bot_response = data.get("bot_response")
        emotion_id = data.get("emotion_id", None)
        confidence = data.get("confidence", None)
        conversation_end = data.get("conversation_end", False)

        if not all([chatroom_id, user_message, bot_response]):
            raise BadRequest("필수 값이 누락되었습니다.")

        add_chat(
            user_id=user_id,
            chatroom_id=chatroom_id,
            user_message=user_message,
            bot_response=bot_response,
            emotion_id=emotion_id,
            confidence=confidence,
            conversation_end=conversation_end
        )
        return jsonify({"message": "대화가 저장되었습니다."}), 201

    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"서버 오류: {e}")
        return jsonify({"error": "서버 내부 오류"}), 500


@chat_bp.route("/<chatroom_id>", methods=["GET"])
@jwt_required_without_bearer  
def get_chat(chatroom_id):
    """특정 채팅방 대화 기록 조회"""
    try:
        user_id = request.user_id 
        if not user_id:
            return jsonify({"error": "인증이 필요합니다."}), 401
        
        limit = int(request.args.get("limit", 10))
        history = get_user_chatroom_history(user_id, chatroom_id, limit)
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": "서버 내부 오류"}), 500

    
@chat_bp.route("/history/<user_id>", methods=["GET"])
@jwt_required_without_bearer
def get_chat_history(user_id):
    """사용자의 모든 채팅방 조회"""
    # 인증 확인
    if not request.user_id:
        return jsonify({"error": "인증이 필요합니다."}), 401

    # 요청된 user_id와 JWT 토큰의 user_id가 일치하는지 확인
    if request.user_id != user_id:
        return jsonify({"error": "잘못된 사용자 ID입니다."}), 403

    try:
        # 사용자의 채팅방 목록 조회
        chatrooms = get_user_chat_history(user_id)
        return jsonify({"chatrooms": chatrooms}), 200
    except Exception as e:
        print(f"[ERROR] 채팅방 조회 중 오류 발생 (user_id={user_id}): {e}")
        return jsonify({"error": "채팅방 조회 중 오류가 발생했습니다."}), 500


@chat_bp.route("/<chatroom_id>/end", methods=["PUT"])
@jwt_required_without_bearer  
def close_chat(chatroom_id):
    """특정 채팅방 대화 종료"""
    try:
        user_id = request.user_id  
        if not user_id:
            return jsonify({"error": "인증이 필요합니다."}), 401
        
        # 채팅방 종료 처리
        response = end_chatroom(user_id, chatroom_id)
        
        # 응답에 따라 적절한 HTTP 상태 코드 반환
        if "error" in response:
            return jsonify(response), 404 if "찾을 수 없습니다" in response["error"] else 500
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"[ERROR] close_chat 오류 (chatroom_id={chatroom_id}): {e}")
        return jsonify({"error": "서버 내부 오류"}), 500


@chat_bp.route("/preview", methods=["POST"])
@jwt_required_without_bearer  
def preview_rag():
    """RAG 검색 결과 미리보기"""
    user_id = request.user_id 
    if not user_id:
        return jsonify({"error": "인증이 필요합니다."}), 401

    data = request.json
    user_message = data.get("user_message")

    if not user_message:
        return jsonify({"error": "user_message가 필요합니다."}), 400

    search_results = preview_rag_search(user_message)
    return jsonify({"retrieved_documents": search_results}), 200


@chat_bp.route("/message/<message_id>", methods=["DELETE"])
@jwt_required_without_bearer  
def delete_message(message_id):
    """특정 메시지 삭제"""
    try:
        user_id = request.user_id  
        if not user_id:
            return jsonify({"error": "인증이 필요합니다."}), 401

        result = delete_chat_message(message_id, user_id)  
        if not result:
            raise NotFound("메시지를 찾을 수 없습니다.")

        return jsonify({"message": "삭제 완료"}), 200

    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "서버 내부 오류"}), 500


@chat_bp.route("/rag-response", methods=["POST"])
@jwt_required_without_bearer  # 인증 처리
@login_required  # 로그인된 사용자만 RAG 응답을 받을 수 있도록 추가
def chat_rag_response():
    """
    RAG 기반 상담 챗봇 응답 API
    """
    try:
        user_id = request.user_id  # jwt_required_without_bearer에서 자동으로 추가됨
        if not user_id:
            return jsonify({"error": "인증이 필요합니다."}), 401

        data = request.get_json()
        user_message = data.get("user_message", "").strip()
        
        if not user_message:
            return jsonify({"error": "user_message는 필수 입력값입니다."}), 400

        chatroom_id = "test_chatroom"
        response = chat_with_bot(user_id, chatroom_id, user_message, test_mode=True)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/chatroom/<chatroom_id>", methods=["DELETE"])
@jwt_required_without_bearer
def delete_chatroom(chatroom_id):
    """
    특정 채팅방 삭제
    """
    try:
        user_id = request.user_id
        if not user_id:
            return jsonify({"error": "인증이 필요합니다."}), 401

        success = delete_chatroom_service(user_id, chatroom_id)
        if not success:
            return jsonify({"error": "채팅방을 찾을 수 없습니다."}), 404

        return jsonify({"message": "채팅방이 삭제되었습니다."}), 200

    except Exception as e:
        logging.error(f"채팅방 삭제 중 오류 발생 (chatroom_id={chatroom_id}): {e}")
        return jsonify({"error": "서버 내부 오류"}), 500


@chat_bp.route("/history/search", methods=["GET"])
@jwt_required_without_bearer
def search_chat_history():
    """
    사용자의 채팅방 검색
    요청 파라미터:
    - query: 검색어
    """
    try:
        user_id = request.user_id
        if not user_id:
            return jsonify({"error": "인증이 필요합니다."}), 401

        # 검색어 확인
        query = request.args.get("query", "").strip()
        if not query:
            return jsonify({"error": "검색어가 필요합니다."}), 400

        result = search_chatrooms(user_id, query)
        return jsonify({"chatrooms": result}), 200

    except Exception as e:
        logging.error(f"채팅방 검색 중 오류 발생 (user_id={user_id}): {e}")
        return jsonify({"error": "서버 내부 오류"}), 500
    
    
# 테스트 용도. user_id 없이
@chat_bp.route("/test/rag-response", methods=["POST"])
def chat_rag_response_test():
    """
    RAG 기반 상담 챗봇 응답 API
    요청 형식:
    {
        "user_message": "요즘 너무 우울해."
    }
    응답 형식:
    {
        "user_message": "요즘 너무 우울해.",
        "retrieved_documents": "반영됨" 또는 "반영 안 됨",
        "bot_response": "챗봇의 최종 응답"
    }
    """
    try:
        data = request.get_json()
        user_message = data.get("user_message", "").strip()
        
        if not user_message:
            return jsonify({"error": "user_message는 필수 입력값입니다."}), 400
        
        # 테스트 용도: user_id와 chatroom_id를 고정값으로 설정하고 test_mode 활성화
        user_id = "test_user"
        chatroom_id = "test_chatroom"

        # test_mode=True를 전달하여 DB 저장 없이 응답만 반환
        response = chat_with_bot(user_id, chatroom_id, user_message, test_mode=True)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

