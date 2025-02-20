## Swagger url
Swagger UI: http://localhost:5000/api/docs  
Swagger JSON: http://localhost:5000/static/swagger.json  

## 구조 및 흐름
1. 회원가입
- 입력 검증 : 이메일 형식 검증, 비밀번호 규칙 검증, 사용자중복체크
- 비밀번호 암호화 : bcrypt로 해싱
- 회원가입 시 사용자 정보 db에 저장
- jwt 토큰 발급 : access_token과 refresh_token을 발급
- Redis에 Refresh Token 저장 : 토큰 만료 후 갱신

## 백엔드 실행 방법
- 가상환경 생성
- 패키지 설치
```
pip install -r requirements.txt

```
- be/ 디렉토리에서 환경 변수 등록
```
set FLASK_APP=app
```
- 실행
```
flask run
```

## 도커 파일 실행
1. .env 확인 : 아래 내용이 들어있어야 함
```
REDIS_HOST=redis  
REDIS_PORT=6379
REDIS_DB=0
```

2. docker desktop 관리자 모드로 실행

3. Redis 실행
```
cd be
docker-compose up -d
```

4. 실행여부 확인
- 아래 명령어 실행 시 PONG 응답
```
docker exec -it redis_server redis-cli ping
```
- 또는 docker ps로 확인

5. redis 중지
```
docker-compose down
```

## redis 다운로드 필요(도커 미실행시)
1. 최신 파일 다운로드
```
https://github.com/microsoftarchive/redis/releases
```
2. 기본 설정으로 설치 진행
3. 설치 후, Redis 실행
```
redis-server
```
4. 다른 터미널에서 Redis CLI 실행
```
redis-cli
```
5. 연결 확인 : ping 명령어 실행해서 PONG이 뜨는지 확인
```
ping
```
6. redis-server.exe 실행(mysql 워크벤치처럼 켜놓키만 하면 됩니다.)


## .env 내용
```
# SQLAlchemy (MySQL DB)
DB_HOST=localhost
DB_USER=
DB_PASSWORD=
DB_NAME=

# MongoDB 연결 URI
# MONGO_URI=mongodb://localhost:27017/RobotPet
SECRET_KEY=

# 이메일 설정
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=          # 이메일 계정
MAIL_PASSWORD=          # 구글에서 생성한 앱 비밀번호
MAIL_DEFAULT_SENDER=    # 발신자 이메일

# 기본 URL 설정
BASE_URL=http://127.0.0.1:3000

# swagger 관련 설정
SWAGGER_UI_URL=/api/docs
SWAGGER_API_DOCS=/static/swagger.json

# redis 설정
# REDIS_HOST=localhost  # 로컬 redis 실행시 주석 해제하고 아래 주석하기
REDIS_HOST=redis        
REDIS_PORT=6379
REDIS_DB=0

REDIS_TIMEOUT=0         
REDIS_MAXMEMORY=512mb 
REDIS_MAXMEMORY_POLICY=allkeys-lru 
```
  
## 폴더 구조
```bash
📂 be/
├── 📂 app/
│   ├── 📂 database/                  # DB 초기화 및 설정
│   │   └── 📄 __init__.py
│   ├── 📂 models/                    # DB 테이블 정의
│   │   ├── 📄 __init__.py
│   │   └── 📄 users.py
│   ├── 📂 routes/                    # 각 API 엔드포인트에 대한 라우팅 설정
│   │   ├── 📄 __init__.py
│   │   ├── 📄 auth_routes.py         # 인증 관련 API 
│   │   ├── 📄 home_routes.py         # 홈 화면
│   │   └── 📄 user_routes.py         # 사용자 관련 API
│   ├── 📂 services/                  # 비즈니스 로직 처리   
│   │   ├── 📄 auth_service.py        # 인증 서비스 로직
│   │   └── 📄 user_service.py        # user 서비스 로직
│   ├── 📂 static/                
│   │   └── 📄 swagger.json           # Swagger 설정
│   ├── 📂 utils/                  
│   │   └── 📄 error_handler.py       # 공통 에러 핸들러
│   ├── 📄 __init__.py                # Flask 애플리케이션 팩토리 함수 (create_app)
├── 📂 config/                     
│   └── 📄 settings.py                # Flask 환경 변수 설정 (ActiveConfig)
├── 📄 .env                           # 환경 변수
├── 📄 requirements.txt               
├── 📄 .gitignore                     
├── 📄 app.py                         # Flask 실행 스크립트
└── 📄 README.md                      
```
