from datetime import datetime, timezone
from app.database import mongo
import uuid
import logging
from bson import ObjectId


def save_emotion_data(user_id, chatroom_id, emotion, confidence):
    """
    감정 데이터를 MongoDB에 저장
    :param user_id: 사용자 ID
    :param chatroom_id: 채팅방 ID
    :param emotion: 감정 (panic, 'happy', 'sadness', 'angry')
    :param confidence: 감정의 신뢰도 (0~1)
    """

    if not all([user_id, chatroom_id, emotion, confidence]):
        raise ValueError("필수 데이터가 누락되었습니다.")

    emotion_id = str(uuid.uuid4())

    try:
        result = mongo.db.emotions.insert_one(
            {
                "user_id": user_id,
                "chatroom_id": chatroom_id,
                "emotion_id": emotion_id,
                "emotion": emotion,
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc),
            }
        )
        return {
            "message": "감정 데이터가 성공적으로 저장되었습니다.",
            "emotion": emotion,
            "confidence": confidence,
            "emotion_id": emotion_id,
            "inserted_id": str(result.inserted_id),
        }
    except Exception as e:
        logging.error(f"감정 데이터 저장 오류: {e}")
        raise RuntimeError(f"감정 데이터 저장 오류: {e}")


def get_emotion_results(chatroom_id, user_id):
    """
    특정 채팅방에 대한 감정 분석 결과 조회 (가장 많이 나온 감정 반환)
    :param chatroom_id: 채팅방 ID
    :return: 감정 분석 결과 리스트 & 가장 많이 등장한 감정
    """
    try:
        if not isinstance(chatroom_id, str):
            logging.error(f"[ERROR] chatroom_id가 문자열이 아님: {chatroom_id}")
            return {
                "emotions": [],
                "most_common": {"emotion": "neutral", "confidence": 0.5},
            }
        if not is_authorized(user_id, chatroom_id):
            logging.error(
                f"[ERROR] 접근 권한 없음: user_id={user_id}, chatroom_id={chatroom_id}"
            )
            return {
                "emotions": [],
                "most_common": {"emotion": "neutral", "confidence": 0.5},
            }
        emotions_cursor = mongo.db.emotions.find({"chatroom_id": chatroom_id})
        emotions = []
        emotion_counts = {}
        total_confidence = {}
        for emotion_data in emotions_cursor:
            emotion = emotion_data["emotion"]
            confidence = emotion_data["confidence"]
            timestamp = emotion_data["timestamp"]
            emotions.append(
                {"emotion": emotion, "confidence": confidence, "timestamp": timestamp}
            )
            if emotion in emotion_counts:
                emotion_counts[emotion] += 1
                total_confidence[emotion] += confidence
            else:
                emotion_counts[emotion] = 1
                total_confidence[emotion] = confidence
        if emotion_counts:
            most_common_emotion = max(emotion_counts, key=emotion_counts.get)
            avg_confidence = (
                total_confidence[most_common_emotion]
                / emotion_counts[most_common_emotion]
            )
        else:
            most_common_emotion = "neutral"
            avg_confidence = 0.5
        return {
            "emotions": emotions,
            "most_common": {
                "emotion": most_common_emotion,
                "confidence": avg_confidence,
            },
        }
    except Exception as e:
        logging.error(f"[ERROR] 감정 결과 조회 오류: {e}")
        return {
            "emotions": [],
            "most_common": {"emotion": "neutral", "confidence": 0.5},
        }


def delete_emotion_results(chatroom_id):
    """
    특정 채팅방의 감정 분석 결과 삭제
    :param chatroom_id: 채팅방 ID
    """
    try:
        result = mongo.db.emotions.delete_many({"chatroom_id": chatroom_id})
        return result.deleted_count > 0  # 삭제된 문서 수 확인
    except Exception as e:
        raise RuntimeError(f"감정 결과 삭제 오류: {e}")


def auto_end_emotions():
    """
    미종료된 감정 분석 데이터를 자동 종료
    """
    try:
        now = datetime.now(timezone.utc)
        result = mongo.db.emotions.update_many(
            {"timestamp": {"$lt": now}},  # 현재 시간 이전의 데이터
            {"$set": {"confidence": None}},  # 신뢰도를 None으로 설정
        )
        return result.modified_count  # 업데이트된 문서 수 반환
    except Exception as e:
        raise RuntimeError(f"자동 종료 오류: {e}")


def get_model_status(model):
    """
    감정 분석 모델의 상태 확인
    """
    try:
        # 모델이 정상적으로 로드되었는지 확인
        model.summary()  # 모델 요약 출력
        return "정상"
    except Exception as e:
        return f"오류 발생: {str(e)}"


def get_user_emotion_history(user_id):
    """
    사용자의 감정 분석 기록을 조회
    :param user_id: 사용자 ID
    """
    try:
        emotions = mongo.db.emotions.find({"user_id": user_id})
        return [
            {
                "emotion": emotion["emotion"],
                "confidence": emotion["confidence"],
                "timestamp": emotion["timestamp"],
            }
            for emotion in emotions
        ]
    except Exception as e:
        raise RuntimeError(f"사용자 감정 기록 조회 오류: {e}")


def get_most_common_emotion(emotion_data):
    """
    가장 많이 감지된 감정을 찾아 반환하는 함수
    :param emotion_data: 감정 데이터 리스트
    """
    emotion_counts = {"happy": 0, "sadness": 0, "angry": 0, "panic": 0}
    for data in emotion_data:
        emotion_counts[data["emotion"]] += 1
    most_common = max(emotion_counts, key=emotion_counts.get)
    return {"emotion": most_common, "confidence": emotion_counts[most_common]}


def get_emotion_statistics(user_id, start_date, end_date):
    """
    특정 기간 동안 감정 통계 계산 (감정 요약 + 감정 변화)
    :param user_id: 사용자 ID
    :param start_date: 시작 날짜 (ISO 형식, 예: '2023-02-01')
    :param end_date: 종료 날짜 (ISO 형식, 예: '2023-02-28')
    """
    try:
        query = {
            "user_id": user_id,
            "timestamp": {
                "$gte": datetime.fromisoformat(start_date),
                "$lte": datetime.fromisoformat(end_date),
            },
        }
        emotions = mongo.db.emotions.find(query)

        # 감정별 빈도수 계산
        emotion_counts = {"happy": 0, "sadness": 0, "angry": 0, "panic": 0}
        trend_data = []  # 감정 변화 저장 (날짜별 감정 변화)

        for emotion in emotions:
            emotion_counts[emotion["emotion"]] += 1
            trend_data.append(
                {
                    "date": emotion["timestamp"].strftime(
                        "%Y-%m-%d"
                    ),  # datetime → 문자열 변환 후 날짜만 추출
                    "emotion": emotion["emotion"],
                    "confidence": emotion["confidence"],
                }
            )

        # 감정 빈도수를 퍼센트(%)로 변환
        total = sum(emotion_counts.values())
        if total > 0:
            summary = {
                emotion: round((count / total) * 100, 2)
                for emotion, count in emotion_counts.items()
            }
        else:
            summary = {emotion: 0 for emotion in emotion_counts.keys()}

        return {
            "summary": summary,
            "trend": sorted(trend_data, key=lambda x: x["date"]),
        }

    except Exception as e:
        raise RuntimeError(f"감정 통계 조회 오류: {e}")


def is_authorized(user_id, chatroom_id):
    """
    해당 사용자가 특정 채팅방에 접근할 권한이 있는지 확인
    :param user_id: 사용자 ID
    :param chatroom_id: 채팅방 ID
    :return: 권한이 있으면 True, 없으면 False
    """
    try:
        chatroom = mongo.db.chatrooms.find_one(
            {"chatroom_id": chatroom_id, "user_id": user_id}
        )
        return chatroom is not None
    except Exception as e:
        print(
            f"[ERROR] 권한 확인 실패 (user_id={user_id}, chatroom_id={chatroom_id}): {e}"
        )
        return False
