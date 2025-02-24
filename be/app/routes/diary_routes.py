from flask import Blueprint, request, jsonify
from app.services.diary_service import (
    create_diary,
    get_diary_list,
    get_diary_detail,
    delete_diary,
    update_diary,
    create_calendar_emoji,
    search_diary_by_keyword,
)
from app.services.diary_summary_service import generate_summary
from datetime import datetime
import logging
from app.utils.auth import jwt_required_without_bearer
import logging
from flask import jsonify

# Blueprint 정의
diary_bp = Blueprint("diary", __name__)


# 대화 내용 요약 API
@diary_bp.route("/summary", methods=["POST"])
@jwt_required_without_bearer  # JWT 인증 추가
def summarize_conversation():
    """대화 내용을 요약하여 일기 형식으로 생성"""
    try:
        user_id = request.user_id  # JWT에서 추출한 user_id
        chatroom_id = request.json.get("chatroom_id")

        if not chatroom_id:
            return jsonify({"error": "chatroom_id가 필요합니다."}), 400

        # 서비스 호출하여 요약 생성
        summary = generate_summary(chatroom_id)

        if isinstance(summary, tuple):  # 에러 응답인 경우
            return jsonify({"error": summary[0]}), summary[1]

        return jsonify({"summary": summary}), 200

    except Exception as e:
        logging.error(f"[ERROR] /summary: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500


# 일기장 저장 API
@diary_bp.route("/save", methods=["POST"])
@jwt_required_without_bearer  # JWT 인증 추가
def save_diary():
    """요약된 대화 내용을 일기 형식으로 저장"""
    try:
        user_id = request.user_id  # JWT에서 추출한 user_id
        content = request.json.get("content")
        date = request.json.get("date", str(datetime.utcnow().date()))
        emotion = request.json.get("emotion")
        summary = request.json.get("summary")

        # 입력값 검증
        if not content:
            return jsonify({"message": "일기 내용은 필수입니다!"}), 400

        success = create_diary(user_id, content, date, emotion, summary)
        if success:
            return jsonify({"message": "일기 저장 성공!"}), 201
        return jsonify({"message": "일기 저장 실패!"}), 400

    except Exception as e:
        logging.error(f"[ERROR] /save: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500


# 달력 이모지 표시 API
@diary_bp.route("/calendar/emoji", methods=["POST"])
@jwt_required_without_bearer  # JWT 인증 추가
def set_calendar_emoji():
    """대화에서 가장 많이 감지된 감정에 따라 달력 이모지 표시"""
    try:
        user_id = request.user_id  # JWT에서 추출한 user_id
        date = request.json.get("date")
        emotion_emoji = request.json.get("emotion_emoji")

        # 입력값 검증
        if not all([date, emotion_emoji]):
            return jsonify({"message": "날짜와 이모지는 필수입니다!"}), 400

        success = create_calendar_emoji(user_id, date, emotion_emoji)
        if success:
            return jsonify({"message": "이모지 표시 성공!"}), 200
        return jsonify({"message": "이모지 표시 실패!"}), 400

    except Exception as e:
        logging.error(f"[ERROR] /calendar/emoji: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500


# 일기 목록 조회 API
@diary_bp.route("/list", methods=["GET"])
@jwt_required_without_bearer  # JWT 인증 추가
def get_diary_list_api():
    """사용자의 일기 목록을 조회"""
    try:
        user_id = request.user_id  # JWT에서 추출한 user_id
        date = request.args.get("date")  # 날짜로 필터링할 경우 사용

        # 일기 목록 조회
        diaries = get_diary_list(user_id, date)
        if not diaries:
            return jsonify({"message": "저장된 일기가 없습니다."}), 404
        
        # 일기 목록 반환
        return jsonify({"diaries": [diary.to_dict() for diary in diaries]}), 200

    except Exception as e:
        logging.error(f"[ERROR] /list: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500


# 일기 상세 조회 API
@diary_bp.route("/<diary_id>", methods=["GET"])
@jwt_required_without_bearer  # JWT 인증 추가
def get_diary_detail_route(diary_id):
    """일기 상세 조회"""
    try:
        user_id = request.user_id  # JWT에서 추출한 user_id
        diary = get_diary_detail(diary_id)

        # 권한 검증: 해당 일기가 사용자의 것인지 확인
        if not diary or diary["user_id"] != user_id:
            return jsonify({"message": "일기 없음"}), 404

        return jsonify(diary), 200

    except Exception as e:
        logging.error(f"[ERROR] /<diary_id>: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500


# 일기 삭제 API
@diary_bp.route("/delete/<diary_id>", methods=["DELETE"])
@jwt_required_without_bearer  # JWT 인증 추가
def delete_diary_route(diary_id):
    """일기 삭제"""
    try:
        user_id = request.user_id  # JWT에서 추출한 user_id
        diary = get_diary_detail(diary_id)

        # 권한 검증: 해당 일기가 사용자의 것인지 확인
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
@jwt_required_without_bearer  # JWT 인증 추가
def update_diary_route(diary_id):
    """일기 내용 수정"""
    try:
        user_id = request.user_id  # JWT에서 추출한 user_id
        new_content = request.json.get("content")
        new_emotion = request.json.get("emotion")

        # 입력값 검증
        if not new_content:
            return jsonify({"message": "일기 내용은 필수입니다!"}), 400

        # 권한 검증: 해당 일기가 사용자의 것인지 확인
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
@jwt_required_without_bearer  # JWT 인증 추가
def search_diary():
    """일기 내용 검색"""
    try:
        user_id = request.user_id  # JWT에서 추출한 user_id
        keyword = request.args.get("keyword")

        # 입력값 검증
        if not keyword:
            return jsonify({"message": "검색어는 필수입니다!"}), 400

        search_results = search_diary_by_keyword(user_id, keyword)
        return jsonify(search_results), 200

    except Exception as e:
        logging.error(f"[ERROR] /search: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500


# 새 일기 쓰기 API
@diary_bp.route("/create", methods=["POST"])
@jwt_required_without_bearer  # JWT 인증 추가
def create_diary_route():
    """새 일기 작성"""
    try:
        user_id = request.user_id  # JWT에서 추출한 user_id
        content = request.json.get("content")
        emotion = request.json.get("emotion")

        # 입력값 검증
        if not content:
            return jsonify({"message": "일기 내용은 필수입니다!"}), 400

        diary_id = create_diary(user_id, content, emotion)
        if diary_id:
            return (
                jsonify({"message": "일기 작성 성공!", "diary_id": str(diary_id)}),
                201,
            )
        return jsonify({"message": "일기 작성 실패!"}), 400

    except Exception as e:
        logging.error(f"[ERROR] /create: {e}")
        return jsonify({"error": f"오류 발생: {str(e)}"}), 500
