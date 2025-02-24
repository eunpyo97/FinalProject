from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from app.models.emotion import load_emotion_model, predict_emotion
from app.services.emotion_service import (
    save_emotion_data, get_emotion_results, delete_emotion_results,
    auto_end_emotions, get_model_status, get_user_emotion_history,
    get_most_common_emotion, get_emotion_statistics
)
import cv2

emotion_bp = Blueprint('emotion', __name__)
model = load_emotion_model()

# 감정 예측 API
@emotion_bp.route('/predict', methods=['POST'])
def predict():
    """사용자가 이미지를 업로드하면 해당 이미지의 감정을 예측하고 결과를 반환"""
    try:
        # 이미지 파일 받기
        file = request.files.get('image')
        if not file:
            return jsonify({"message": "이미지 파일이 필요합니다."}), 400
        
        # 저장할 파일 경로 설정
        filename = secure_filename(file.filename)
        image_path = os.path.join('uploads', filename)
        file.save(image_path)
        
        # 감정 예측
        image = cv2.imread(image_path)
        emotion_label, confidence = predict_emotion(image, model)
        
        # 감정 데이터 저장
        user_id = request.form.get("user_id", "default_user")
        chatroom_id = request.form.get("chatroom_id", "default_chatroom")
        save_emotion_data(user_id, chatroom_id, emotion_label, confidence)
        
        return jsonify({
            "emotion": emotion_label,
            "confidence": confidence,
            "message": "감정 분석이 성공적으로 수행되었습니다."
        })
    
    except Exception as e:
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500

# 감정 분석 결과 조회 API
@emotion_bp.route('/results/<chatroom_id>', methods=['GET'])
def results(chatroom_id):
    """특정 채팅방의 감정 분석 결과를 조회"""
    try:
        results = get_emotion_results(chatroom_id)
        return jsonify(results)
    except Exception as e:
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500

# 감정 분석 히스토리 삭제 API
@emotion_bp.route('/results/<chatroom_id>', methods=['DELETE'])
def delete_results(chatroom_id):
    """특정 채팅방의 감정 분석 결과를 삭제"""
    try:
        success = delete_emotion_results(chatroom_id)
        return jsonify({"message": "삭제 성공" if success else "삭제 실패"})
    except Exception as e:
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500

# 미처리된 감정 분석 데이터 자동 종료 API
@emotion_bp.route('/end', methods=['POST'])
def auto_end():
    """날짜가 바뀌면 미종료된 감정 분석 데이터를 자동으로 종료"""
    try:
        ended_emotions = auto_end_emotions()
        return jsonify({"message": "자동 종료된 감정 분석 데이터", "ended_emotions": ended_emotions})
    except Exception as e:
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500

# 감정 분석 모델 상태 확인 API
@emotion_bp.route('/status', methods=['GET'])
def model_status():
    """감정 분석 모델의 상태를 확인"""
    try:
        status = get_model_status(model)
        return jsonify({"status": status})
    except Exception as e:
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500

# 사용자 감정 분석 기록 조회 API
@emotion_bp.route('/history/<user_id>', methods=['GET'])
def user_history(user_id):
    """사용자의 감정 분석 기록을 조회"""
    try:
        history = get_user_emotion_history(user_id)
        return jsonify(history)
    except Exception as e:
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500

# 대화 종료 시 감정 기록 저장 API
@emotion_bp.route('/save-end-emotion', methods=['POST'])
def save_end_emotion():
    """대화 종료 시, 채팅방에서 가장 많이 감지된 감정을 저장"""
    try:
        chatroom_id = request.json.get("chatroom_id")
        user_id = request.json.get("user_id")
        
        # 감정 데이터를 불러와서 가장 많이 감지된 감정 확인
        emotion_data = get_emotion_results(chatroom_id)
        most_common_emotion = get_most_common_emotion(emotion_data)
        
        # 감정 데이터를 저장
        save_emotion_data(user_id, chatroom_id, most_common_emotion["emotion"], most_common_emotion["confidence"])
        
        return jsonify({
            "message": "대화 종료 시 감정 데이터 저장 성공",
            "emotion": most_common_emotion
        })
    except Exception as e:
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500

# 감정 통계 API
@emotion_bp.route('/stats/<user_id>', methods=['GET'])
def emotion_stats(user_id):
    """사용자의 감정 통계를 조회 (주간, 월간 등)"""
    try:
        start_date = request.args.get('start_date')  # 예: '2023-02-01'
        end_date = request.args.get('end_date')      # 예: '2023-02-28'
        
        stats = get_emotion_statistics(user_id, start_date, end_date)
        
        return jsonify({
            "message": "감정 통계 조회 성공",
            "stats": stats
        })
    except Exception as e:
        return jsonify({"message": f"오류 발생: {str(e)}"}), 500