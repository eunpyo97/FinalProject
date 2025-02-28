from flask import Blueprint, request, jsonify
from app.services.diary_service import (
    create_diary,
    get_diary_list,
    get_diary_detail,
    delete_diary,
    update_diary,
    search_diary_by_keyword,
)
from app.services.diary_summary_service import generate_summary
from app.services.emotion_service import (
    get_most_common_emotion, get_emotion_results
)
from datetime import datetime, timezone
import logging
from app.utils.auth import jwt_required_without_bearer

diary_bp = Blueprint("diary", __name__)


# 대화 내용 요약 API
@diary_bp.route("/summary", methods=["POST"])
@jwt_required_without_bearer
def summarize_conversation():
    try:
        user_id = request.user_id
        chatroom_id = request.json.get("chatroom_id")

        if not chatroom_id:
            return jsonify({"error": "chatroom_id가 필요합니다."}), 400

        summary = generate_summary(chatroom_id)

        if isinstance(summary, tuple):
            return jsonify({"error": summary[0]}), summary[1]

        return jsonify({"summary": summary}), 200

    except Exception as e:
        logging.error(f"[ERROR] /summary: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500


# 요약 생성과 동시에 DB 저장
@diary_bp.route("/summary/save", methods=["POST"])
@jwt_required_without_bearer  
def summarize_and_save_diary():
    try:
        user_id = request.user_id  
        chatroom_id = request.json.get("chatroom_id")
        date = request.json.get("date", str(datetime.now(timezone.utc).date())) 

        if not chatroom_id:
            return jsonify({"error": "chatroom_id가 필요합니다."}), 400

        summary = generate_summary(chatroom_id)

        if isinstance(summary, tuple):  
            return jsonify({"error": summary[0]}), summary[1]

        # 감정 데이터를 가져와서 가장 많이 나타난 감정을 추출
        emotion_data = get_emotion_results(chatroom_id, user_id)  
        emotion_info = emotion_data.get("most_common", {"emotion": "neutral", "confidence": 0.5})  
        emotion = emotion_info.get("emotion") 

        # 일기 저장 (summary를 content로 사용)
        diary_id = create_diary(user_id, chatroom_id, summary, date, emotion, summary)

        if diary_id:
            return jsonify({"message": "요약 및 일기 저장 성공!", "diary_id": str(diary_id), "summary": summary}), 201
        return jsonify({"message": "요약은 생성되었지만, 일기 저장 실패!"}), 400

    except Exception as e:
        logging.error(f"[ERROR] /summary/save: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500


# 일기장 저장 API
@diary_bp.route("/save", methods=["POST"])
@jwt_required_without_bearer
def save_diary():
    try:
        user_id = request.user_id
        chatroom_id = request.json.get("chatroom_id")
        content = request.json.get("content")
        date = request.json.get("date", str(datetime.now(timezone.utc).date()))
        emotion = request.json.get("emotion")
        summary = request.json.get("summary")

        if not content:
            return jsonify({"message": "일기 내용은 필수입니다!"}), 400

        diary_id = create_diary(user_id, chatroom_id, content, date, emotion, summary)

        if diary_id:
            return (
                jsonify({"message": "일기 저장 성공!", "diary_id": str(diary_id)}),
                201,
            )
        return jsonify({"message": "일기 저장 실패!"}), 400

    except Exception as e:
        logging.error(f"[ERROR] /save: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500


# 일기 목록 조회 API
@diary_bp.route("/list", methods=["GET"])
@jwt_required_without_bearer
def get_diary_list_api():
    try:
        user_id = request.user_id
        date = request.args.get("date")

        if not date:
            return jsonify({"error": "date 파라미터가 필요합니다."}), 400

        print(f"[DEBUG] 요청된 날짜: {date}")

        diaries = get_diary_list(user_id, date)

        if not diaries:
            return jsonify({"diaries": []}), 200  # 

        return jsonify({"diaries": diaries}), 200  # 
    except Exception as e:
        logging.error(f"[ERROR] /list: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500



# 일기 상세 조회 API
@diary_bp.route("/<diary_id>", methods=["GET"])
@jwt_required_without_bearer
def get_diary_detail_route(diary_id):
    try:
        user_id = request.user_id
        diary = get_diary_detail(diary_id)

        if not diary or diary["user_id"] != user_id:
            return jsonify({"message": "일기 없음"}), 404

        return jsonify(diary), 200

    except Exception as e:
        logging.error(f"[ERROR] /<diary_id>: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500


# 일기 삭제 API
@diary_bp.route("/delete/<diary_id>", methods=["DELETE"])
@jwt_required_without_bearer
def delete_diary_route(diary_id):
    try:
        user_id = request.user_id
        diary = get_diary_detail(diary_id)

        if not diary or diary["user_id"] != user_id:
            return jsonify({"message": "권한이 없습니다."}), 403

        success = delete_diary(diary_id)
        if success:
            return jsonify({"message": "일기 삭제 성공!"}), 200
        return jsonify({"message": "일기 삭제 실패!"}), 400

    except Exception as e:
        logging.error(f"[ERROR] /delete/<diary_id>: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500


# 일기 수정 API
@diary_bp.route("/update/<diary_id>", methods=["PUT"])
@jwt_required_without_bearer
def update_diary_route(diary_id):
    try:
        user_id = request.user_id
        new_content = request.json.get("content")
        new_emotion = request.json.get("emotion")

        if not new_content:
            return jsonify({"message": "일기 내용은 필수입니다!"}), 400

        diary = get_diary_detail(diary_id)
        if not diary or diary["user_id"] != user_id:
            return jsonify({"message": "권한이 없습니다."}), 403

        success = update_diary(diary_id, new_content, new_emotion)
        if success:
            return jsonify({"message": "일기 수정 성공!"}), 200
        return jsonify({"message": "일기 수정 실패!"}), 400

    except Exception as e:
        logging.error(f"[ERROR] /update/<diary_id>: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500


# 일기 검색 API
@diary_bp.route("/search", methods=["GET"])
@jwt_required_without_bearer
def search_diary():
    try:
        user_id = request.user_id
        keyword = request.args.get("keyword")

        if not keyword:
            return jsonify({"message": "검색어는 필수입니다!"}), 400

        search_results = search_diary_by_keyword(user_id, keyword)
        return jsonify(search_results), 200

    except Exception as e:
        logging.error(f"[ERROR] /search: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500


# 새 일기 쓰기 API
@diary_bp.route("/create", methods=["POST"])
@jwt_required_without_bearer
def create_diary_route():
    try:
        user_id = request.user_id
        chatroom_id = request.json.get("chatroom_id")
        content = request.json.get("content")
        emotion = request.json.get("emotion")

        if not content:
            return jsonify({"message": "일기 내용은 필수입니다!"}), 400

        diary_id = create_diary(
            user_id,
            chatroom_id,
            content,
            str(datetime.now(timezone.utc).date()),
            emotion,
        )

        if diary_id:
            return (
                jsonify({"message": "일기 작성 성공!", "diary_id": str(diary_id)}),
                201,
            )
        return jsonify({"message": "일기 작성 실패!"}), 400

    except Exception as e:
        logging.error(f"[ERROR] /create: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500
