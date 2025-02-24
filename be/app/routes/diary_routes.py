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

# Blueprint 정의
diary_bp = Blueprint("diary", __name__)

# 1. 대화 내용 요약 API
@diary_bp.route('/summary', methods=['POST'])
def summarize_conversation():
    """대화 내용을 요약하여 일기 형식으로 생성"""
    try:
        chatroom_id = request.json.get('chatroom_id')
        if not chatroom_id:
            return jsonify({"error": "chatroom_id가 필요합니다."}), 400
        
        # 서비스 호출하여 요약 생성
        summary = generate_summary(chatroom_id)
        
        if isinstance(summary, tuple):  # 에러 응답인 경우
            return jsonify({"error": summary[0]}), summary[1]
        
        return jsonify({"summary": summary}), 200
    
    except Exception as e:
        logging.error(f"[ERROR] 요약 생성 중 오류 발생: {e}")
        return jsonify({"error": "서버 내부 오류"}), 500


# 2. 일기장 저장 API
@diary_bp.route("/save", methods=["POST"])
def save_diary():
    """요약된 대화 내용을 일기 형식으로 저장"""
    try:
        user_id = request.json.get("user_id")
        content = request.json.get("content")
        date = request.json.get("date", str(datetime.utcnow().date()))
        emotion = request.json.get("emotion")
        summary = request.json.get("summary")
        
        # 입력값 검증
        if not user_id or not content:
            return jsonify({"message": "사용자 ID와 일기 내용은 필수입니다!"}), 400
        
        success = create_diary(user_id, content, date, emotion, summary)
        if success:
            return jsonify({"message": "일기 저장 성공!"}), 201
        return jsonify({"message": "일기 저장 실패!"}), 400
    
    except Exception as e:
        logging.error(f"[ERROR] 일기 저장 중 오류 발생: {e}")
        return jsonify({"error": "서버 내부 오류"}), 500


# 3. 달력 이모지 표시 API
@diary_bp.route("/calendar/emoji", methods=["POST"])
def set_calendar_emoji():
    """대화에서 가장 많이 감지된 감정에 따라 달력 이모지 표시"""
    try:
        user_id = request.json.get("user_id")
        date = request.json.get("date")
        emotion_emoji = request.json.get("emotion_emoji")
        
        # 입력값 검증
        if not user_id or not date or not emotion_emoji:
            return jsonify({"message": "사용자 ID, 날짜, 이모지는 필수입니다!"}), 400
        
        success = create_calendar_emoji(user_id, date, emotion_emoji)
        if success:
            return jsonify({"message": "이모지 표시 성공!"}), 200
        return jsonify({"message": "이모지 표시 실패!"}), 400
    
    except Exception as e:
        logging.error(f"[ERROR] 이모지 설정 중 오류 발생: {e}")
        return jsonify({"error": "서버 내부 오류"}), 500


# 4. 일기 목록 조회 API
@diary_bp.route("/list", methods=["GET"])
def get_diary_list_route():
    """특정 날짜에 작성된 일기 목록 조회"""
    try:
        user_id = request.args.get("user_id")
        date = request.args.get("date")
        
        # 입력값 검증
        if not user_id or not date:
            return jsonify({"message": "사용자 ID와 날짜는 필수입니다!"}), 400
        
        diaries = get_diary_list(user_id, date)
        return jsonify(diaries), 200
    
    except Exception as e:
        logging.error(f"[ERROR] 일기 목록 조회 중 오류 발생: {e}")
        return jsonify({"error": "서버 내부 오류"}), 500


# 5. 일기 상세 조회 API
@diary_bp.route("/<diary_id>", methods=["GET"])
def get_diary_detail_route(diary_id):
    """일기 상세 조회"""
    try:
        diary = get_diary_detail(diary_id)
        if diary:
            return jsonify(diary), 200
        return jsonify({"message": "일기 없음"}), 404
    
    except Exception as e:
        logging.error(f"[ERROR] 일기 상세 조회 중 오류 발생: {e}")
        return jsonify({"error": "서버 내부 오류"}), 500


# 6. 일기 삭제 API
@diary_bp.route("/delete/<diary_id>", methods=["DELETE"])
def delete_diary_route(diary_id):
    """일기 삭제"""
    try:
        success = delete_diary(diary_id)
        if success:
            return jsonify({"message": "일기 삭제 성공!"}), 200
        return jsonify({"message": "일기 삭제 실패!"}), 400
    
    except Exception as e:
        logging.error(f"[ERROR] 일기 삭제 중 오류 발생: {e}")
        return jsonify({"error": "서버 내부 오류"}), 500


# 7. 일기 수정 API
@diary_bp.route("/update/<diary_id>", methods=["PUT"])
def update_diary_route(diary_id):
    """일기 내용 수정"""
    try:
        new_content = request.json.get("content")
        new_emotion = request.json.get("emotion")
        
        # 입력값 검증
        if not new_content:
            return jsonify({"message": "일기 내용은 필수입니다!"}), 400
        
        success = update_diary(diary_id, new_content, new_emotion)
        if success:
            return jsonify({"message": "일기 수정 성공!"}), 200
        return jsonify({"message": "일기 수정 실패!"}), 400
    
    except Exception as e:
        logging.error(f"[ERROR] 일기 수정 중 오류 발생: {e}")
        return jsonify({"error": "서버 내부 오류"}), 500


# 8. 일기 검색 API
@diary_bp.route("/search", methods=["GET"])
def search_diary():
    """일기 내용 검색"""
    try:
        user_id = request.args.get("user_id")
        keyword = request.args.get("keyword")
        
        # 입력값 검증
        if not user_id or not keyword:
            return jsonify({"message": "사용자 ID와 검색어는 필수입니다!"}), 400
        
        search_results = search_diary_by_keyword(user_id, keyword)
        return jsonify(search_results), 200
    
    except Exception as e:
        logging.error(f"[ERROR] 일기 검색 중 오류 발생: {e}")
        return jsonify({"error": "서버 내부 오류"}), 500


# 9. 새 일기 쓰기 API
@diary_bp.route("/create", methods=["POST"])
def create_diary_route():
    """새 일기 작성"""
    try:
        user_id = request.json.get("user_id")
        content = request.json.get("content")
        emotion = request.json.get("emotion")
        
        # 입력값 검증
        if not user_id or not content:
            return jsonify({"message": "사용자 ID와 일기 내용은 필수입니다!"}), 400
        
        diary_id = create_diary(user_id, content, emotion)
        if diary_id:
            return jsonify({"message": "일기 작성 성공!", "diary_id": str(diary_id)}), 201
        return jsonify({"message": "일기 작성 실패!"}), 400
    
    except Exception as e:
        logging.error(f"[ERROR] 새 일기 작성 중 오류 발생: {e}")
        return jsonify({"error": "서버 내부 오류"}), 500