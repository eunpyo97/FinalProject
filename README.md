# Ai-RobotPet






### 폴더구조
```
📦 AI-ROBOTPET
├── 📂 data
│   ├── 📂 raw
│   ├── 📂 db 
│   │    └── 📂 faiss_v2 # 벡터db
│   └── 📂 models  # 모델 저장
├── 📂 be
├── 📂 fe
├── 📂 test
├── 📂 notebook
├── 📂 models
│   ├──📂 llm
│   │   ├── 📄 01_jsonl_to_csv.ipynb  # JSONL 데이터를 CSV로 변환
│   │   ├── 📄 02_save_vector_db.ipynb  # 벡터DB로 변환하여 저장
│   │   ├── 📄 03_load_vector_db.ipynb  # 저장된 벡터DB 로드
│   │   └── 📄 04_rag_chatbot.ipynb  # RAG 챗봇 구현 코드
    └──📂 face
│       ├── 📄 preprocess.py  # 데이터를 전처리
│       ├── 📄 TEST_1efficientnet_b2_model.keras  # 감정분류 모델
│       ├── 📄 train_model.py  # 감정분류 모델을 훈련시켰던 코드
│       └── 📄 test_model.py  # 훈련이 완료된 모델을 테스트하고 MongoDB에 전달하는 코드
├── 📄 .env  
├── 📄 .gitattributes  # Git 속성 설정
├── 📄 .gitignore  
├── 📄 README.md  
└── 📄 requirements.txt  # 프로젝트 의존성 패키지 목록


```

### 실행 방법
1. git clone
2. 가상환경 실행
3. 라이브러리 설치
```bash
pip install -r requirements.txt
```

### .env
- 아래 내용 기입하여 별도 생성 필요
```bash
OPENAI_API_KEY=
```