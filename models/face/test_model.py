import datetime
from pymongo import MongoClient

# MongoDB 연결
client = MongoClient("mongodb://localhost:27017/")
db = client["emotionDB"]
collection = db["emotions"]

# 모델 로드
model_path = "TEST_1efficientnet_b2_model.keras"
model = tf.keras.models.load_model(model_path)
print(" 모델이 로드되었습니다.")

# 감정 클래스
class_names = ['happy', 'sadness', 'angry', 'panic']

# 이미지 로드 (테스트 이미지 경로 지정)
image_path = ""
image = cv2.imread(image_path)

# 이미지 전처리
face_resized = cv2.resize(image, (224, 224))
face_array = img_to_array(face_resized)
face_array = np.expand_dims(face_array, axis=0) / 255.0  # 정규화

# 감정 분석 실행
predictions = model.predict(face_array)
predicted_class = np.argmax(predictions)
confidence = np.max(predictions)

# 결과 출력
emotion_label = class_names[predicted_class]
print(f"🔹 감정 분석 결과: {emotion_label} ({confidence*100:.2f}%)")

# MongoDB 저장 
emotion_data = {
    "emotion": emotion_label,
    "confidence": round(confidence * 100, 2),
    "timestamp": datetime.datetime.now(), 
}

#  MongoDB에 데이터 저장
result = collection.insert_one(emotion_data)
print(f" 데이터 저장 완료, ID: {result.inserted_id}")
