from datetime import datetime
import pytz  # KST 정의를 위해 추가
from app.database import mongo
import uuid
import logging
from bson import ObjectId

# 한국 표준시(KST) 정의
KST = pytz.timezone("Asia/Seoul")


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
        kst_now = datetime.now(KST)

        result = mongo.db.emotions.insert_one(
            {
                "user_id": user_id,
                "chatroom_id": chatroom_id,
                "emotion_id": emotion_id,
                "emotion": emotion,
                "confidence": confidence,
                "timestamp": kst_now.isoformat(),
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
        start_date_kst = datetime.fromisoformat(start_date).astimezone(KST)
        end_date_kst = datetime.fromisoformat(end_date).astimezone(KST)
        end_date_kst = end_date_kst.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        print(f"[DEBUG] API 요청 받은 start_date: {start_date_kst}")
        print(f"[DEBUG] API 요청 받은 end_date: {end_date_kst}")

        # 문자열로 변환
        start_date_str = start_date_kst.isoformat()
        end_date_str = end_date_kst.isoformat()

        query = {
            "user_id": user_id,
            "timestamp": {
                "$gte": start_date_str, 
                "$lte": end_date_str,
            },
        }

        emotions = list(mongo.db.emotions.find(query))

        print(f"[DEBUG] 조회된 감정 데이터 개수: {len(emotions)}")
        for emotion in emotions:
            print(f"[DEBUG] 감정 데이터: {emotion}")

        emotion_counts = {"happy": 0, "sadness": 0, "angry": 0, "panic": 0}
        trend_data = []

        for emotion in emotions:
            emotion_counts[emotion["emotion"]] += 1
            trend_data.append(
                {
                    "date": emotion["timestamp"].split("T")[0],  
                    "emotion": emotion["emotion"],
                    "confidence": emotion["confidence"],
                }
            )

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
