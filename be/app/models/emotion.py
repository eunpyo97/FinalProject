from flask_pymongo import PyMongo
from datetime import datetime
import tensorflow as tf
import cv2
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array
import os
import uuid

mongo = PyMongo()


def save_emotion(mongo, user_id, chatroom_id, emotion, confidence):
    """
    감정 데이터를 MongoDB에 저장하는 함수
    :param mongo: Flask-PyMongo 객체
    :param user_id: 사용자 ID
    :param chatroom_id: 채팅방 ID
    :param emotion: 감정 ('panic', 'happy', 'sadness', 'angry')
    :param confidence: 감정의 신뢰도 (0~1)
    """
    emotion_id = str(uuid.uuid4())

    try:
        mongo.db.emotions.insert_one(
            {
                "user_id": user_id,
                "chatroom_id": chatroom_id,
                "emotion_id": emotion_id,
                "emotion": emotion,
                "confidence": confidence,
                "timestamp": datetime.utcnow(),
            }
        )
        print("감정 데이터 저장 성공!")
    except Exception as e:
        print(f"감정 데이터 저장 실패: {str(e)}")


def load_emotion_model():
    """
    감정 분석 모델을 로드하는 함수
    """
    try:
        # 현재 파일(__file__)의 디렉토리를 기준으로 상대 경로 설정
        base_dir = os.path.dirname(os.path.abspath(__file__))  # models 디렉토리 경로
        model_path = os.path.join(
            base_dir, "..", "..", "data", "model", "TEST_1efficientnet_b2_model.keras"
        )

        # 절대 경로로 변환 (상대 경로를 안전하게 처리하기 위해)
        model_path = os.path.abspath(model_path)

        # 파일 존재 여부 확인
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {model_path}")

        # 모델 로드
        model = tf.keras.models.load_model(model_path)
        print("모델 로드 성공!")
        return model

    except Exception as e:
        print(f"모델 로드 중 오류 발생: {e}")
        raise


def predict_emotion(image, model):
    """이미지 경로를 받아 감정 예측을 수행하는 함수"""
    if image is None:
        raise ValueError("이미지를 불러올 수 없습니다.")

    # 이미지 전처리
    face_resized = cv2.resize(image, (224, 224))
    face_array = img_to_array(face_resized)
    face_array = np.expand_dims(face_array, axis=0) / 255.0  # 정규화

    # 감정 예측
    predictions = model.predict(face_array)
    predicted_class = np.argmax(predictions)
    confidence = np.max(predictions)

    # 감정 클래스 정의
    class_names = ["happy", "sadness", "angry", "panic"]
    emotion_label = class_names[predicted_class]

    # confidence를 float으로 변환
    return emotion_label, float(confidence)  # confidence를 float으로 변환
