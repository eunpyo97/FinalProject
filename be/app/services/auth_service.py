import os
import re
import uuid
import bcrypt
import redis
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from jose import jwt, ExpiredSignatureError, JWTError
from flask_mail import Mail, Message
from flask import request, current_app
from app.models import db, User, UserProfile, UserTime, UserLog
import random
from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from app.database import mongo

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "noreply@example.com")  
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")  
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")  
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))  
REDIS_DB = int(os.getenv("REDIS_DB", 0))  

mail = Mail()
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)  

def validate_password(password):
    """
    비밀번호 복잡성 검사

    :param password: 입력된 비밀번호
    :raises ValueError: 비밀번호 조건이 충족되지 않을 경우 예외 발생
    """
    if len(password) < 8:
        raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
    if not any(c.isupper() for c in password):  
        raise ValueError("비밀번호에 최소 하나의 대문자가 포함되어야 합니다.")
    if not any(c.islower() for c in password):  
        raise ValueError("비밀번호에 최소 하나의 소문자가 포함되어야 합니다.")
    if not any(c.isdigit() for c in password):  
        raise ValueError("비밀번호에 최소 하나의 숫자가 포함되어야 합니다.")
    if not any(c in "@$!%*?&" for c in password):  
        raise ValueError("비밀번호에 최소 하나의 특수문자가 포함되어야 합니다.")

def validate_email(email):
    """
    이메일 형식 검증

    :param email: 입력된 이메일
    :return: 이메일이 유효한 경우 True, 그렇지 않으면 False
    """
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email)

def register_user(email, password, confirm_password):
    """
    회원가입 처리

    :param email: 사용자 이메일
    :param password: 비밀번호
    :param confirm_password: 비밀번호 확인
    :raises ValueError: 유효하지 않은 이메일, 이미 존재하는 이메일, 비밀번호 불일치 시 예외 발생
    :return: 회원가입 성공 메시지
    """
    if not validate_email(email):
        raise ValueError("유효하지 않은 이메일 형식입니다.")

    if User.query.filter_by(email=email).first():
        raise ValueError("이미 가입된 이메일입니다.")

    if password != confirm_password:
        raise ValueError("비밀번호가 일치하지 않습니다.")

    validate_password(password)

    # 중복 이메일 인증 요청 방지 (10분 동안 유효)
    if r.exists(f"email_verification_request:{email}"):
        raise ValueError("이메일 인증 요청이 이미 진행 중입니다. 잠시 후 다시 시도하세요.")

    # 새 사용자 저장 (is_verified=True 로 설정)
    # 평문 비밀번호를 넘겨서 모델의 setter가 해싱하도록
    user_id = str(uuid.uuid4())

    try:
        new_user = User(email=email, user_id=user_id, password=password, is_verified=True)

        db.session.add(new_user)
        db.session.commit()

        new_profile = UserProfile(user_id=user_id, nickname=email.split("@")[0])
        new_user_time = UserTime(user_id=new_user.id)

        db.session.add(new_profile)
        db.session.add(new_user_time)
        db.session.commit()

        mongo.db.user_sessions.insert_one({
            "user_id": user_id,  
        })

        # Redis에서 중복 요청 제한 해제
        r.delete(f"email_verification_request:{email}")

        send_welcome_email(email)

        return {"message": "회원가입이 완료되었습니다."}
    except Exception as e:
        db.session.rollback() 
        mongo.db.user_sessions.delete_one({"user_id": user_id})  
        raise ValueError(f"회원가입 중 오류 발생: {str(e)}")

def send_welcome_email(email):
    """
    회원가입 환영 이메일 전송

    :param email: 사용자 이메일
    """
    subject = "회원가입을 환영합니다!"
    body = (
        "안녕하세요!\n\n"
        "회원가입을 완료해 주셔서 감사합니다.\n"
        "앞으로 다양한 서비스를 이용하실 수 있습니다.\n\n"
        "궁금한 사항이 있다면 언제든지 문의해 주세요.\n\n"
        "상담 챗봇팀 드림"
    )

    msg = Message(subject, sender=MAIL_USERNAME, recipients=[email])
    msg.body = body

    try:
        mail.send(msg)
    except Exception as e:
        print(f"[ERROR] 환영 이메일 전송 실패: {str(e)}")  


def send_verification_code_service(email):
    """
    이메일 인증 코드 생성 및 전송 (6자리 숫자 코드)
    
    :param email: 사용자 이메일
    :return: 성공 메시지와 생성된 인증 코드를 담은 딕셔너리
    """
    if not validate_email(email):
        raise ValueError("유효하지 않은 이메일 형식입니다.")
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValueError("이미 가입된 이메일입니다.")

    verification_code = str(random.randint(100000, 999999))
    print(f"[DEBUG] 생성된 인증 코드: {verification_code}")  

    msg = Message("이메일 인증 코드", sender=MAIL_USERNAME, recipients=[email])
    msg.body = f"인증 코드: {verification_code}\n\n이 코드는 5분 동안 유효합니다."

    try:
        mail.send(msg)
    except Exception as e:
        print(f"[ERROR] 이메일 전송 실패: {str(e)}")  
        raise ValueError(f"이메일 전송 실패: {str(e)}")  

    return {
        "message": "이메일이 전송되었습니다.",
        "verificationCode": verification_code  
    }


def verify_email_service(email, code):
    """
    이메일 인증 코드 검증 (로컬스토리지 활용)
    
    :param email: 사용자 이메일
    :param code: 사용자가 입력한 인증 코드
    :return: 이메일 인증 성공 메시지
    """
    if not code:
        raise ValueError("인증 코드가 입력되지 않았습니다.")

    return {"message": "이메일 인증이 완료되었습니다."}


# def verify_email_service(email, code):
#     """
#     이메일 인증 코드 검증

#     :param email: 사용자 이메일
#     :param code: 사용자가 입력한 인증 코드
#     :raises ValueError: 인증 코드가 만료되었거나 일치하지 않는 경우
#     :return: 이메일 인증 성공 메시지
#     """
#     stored_code = r.get(f"verification_code:{email}")

#     if not stored_code:
#         raise ValueError("인증 코드가 만료되었거나 요청되지 않았습니다.")

#     if stored_code.decode("utf-8") != code:
#         raise ValueError("잘못된 인증 코드입니다.")

#     # 인증 코드 검증 성공 시, Redis에서 삭제
#     r.delete(f"verification_code:{email}")

#     # DB에서 사용자 이메일 인증 상태 업데이트
#     user = User.query.filter_by(email=email).first()
#     if not user:
#         raise ValueError("해당 이메일의 사용자가 존재하지 않습니다.")

#     user.is_verified = True
#     db.session.commit()

#     return {"message": "이메일 인증이 완료되었습니다."}


def verify_email_status_service(email):
    """
    이메일 인증 상태 확인
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ValueError("등록되지 않은 이메일입니다.")

    return {"verified": user.is_verified}

def verify_email_request_service(email):
    """
    이메일 인증 요청 처리
    """
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            raise ValueError("이미 등록된 이메일입니다.")  
        
        send_verification_code_service(email)  

        return {"message": "이메일이 전송되었습니다. 인증 후 다시 확인해주세요."}

    except Exception as e:
        current_app.logger.error(f"이메일 인증 요청 처리 중 오류: {str(e)}")
        raise e


# def verify_email_request_service(email):
#     """
#     이메일 인증 요청 처리
#     """
#     try:
#         # 이메일이 DB에 존재하는지 확인
#         user = User.query.filter_by(email=email).first()
#         if user:
#             raise ValueError("이미 등록된 이메일입니다.")  # 이메일이 이미 존재하면 예외 발생
        
#         # Redis에서 인증 요청이 진행 중인지 확인
#         if r.exists(f"pending_user:{email}"):
#             # Redis에서 이미 요청된 이메일 삭제
#             print(f"기존 인증 요청이 있으면 Redis에서 키를 삭제하려고 시도: pending_user:{email}")
#             r.delete(f"pending_user:{email}")  # 이미 요청된 이메일은 삭제
#             print(f"기존 인증 요청 키 삭제 완료: pending_user:{email}")
#             raise ValueError("이미 이메일 인증 요청이 진행 중입니다. 잠시 후 다시 시도하세요.")
        
#         # 새로운 사용자 추가
#         new_user = User(email=email, is_verified=False)
#         db.session.add(new_user)
#         db.session.commit()

#         # Redis에 인증 요청 정보 저장 (1분 동안 유효)
#         print(f"새 인증 요청 저장: pending_user:{email}")
#         r.setex(f"pending_user:{email}", timedelta(minutes=1), json.dumps({"email": email}))

#         print(f"인증 요청 저장 완료: pending_user:{email}")
        
#         # 이메일 인증 코드 전송
#         send_verification_code_service(email)

#         return {"message": "이메일이 전송되었습니다. 인증 후 다시 확인해주세요."}

#     except Exception as e:
#         current_app.logger.error(f"이메일 인증 요청 처리 중 오류: {str(e)}")
#         raise e


def logout_service(access_token):
    """
    로그아웃 처리 (토큰 즉시 무효화)
    :param access_token: 사용자 액세스 토큰
    :return: 로그아웃 성공 메시지
    """
    try:
        user_id = verify_token(access_token) 
        print(f"[DEBUG] 로그아웃 요청: user_id = {user_id}")

        if not user_id:
            raise ValueError("잘못된 토큰 형식입니다. user_id 없음")
        
    except ValueError as e:
        raise ValueError(f"로그아웃 실패: {str(e)}") 

    # Redis에서 해당 사용자의 토큰 삭제 (즉시 만료)
    r.setex(f"access_token_{user_id}", timedelta(seconds=1), "invalid")
    r.setex(f"refresh_token_{user_id}", timedelta(seconds=1), "invalid")

    # Redis에서 세션 상태 삭제
    r.delete(f"user:{user_id}:session")  

    # Redis에서 세션 삭제 대신 만료 시간만 줄이기
    # r.setex(f"user:{user_id}:session", timedelta(minutes=1), "inactive")

    # MongoDB에서 해당 사용자의 로그인 세션 삭제
    mongo.db.user_sessions.delete_one({"user_id": user_id})

    return {"message": "로그아웃이 완료되었습니다."}



def authenticate_user(email, password):
    """
    사용자 로그인 처리

    :param email: 사용자 이메일
    :param password: 비밀번호
    :raises ValueError: 이메일 또는 비밀번호가 잘못되었을 경우 예외 발생
    :raises ValueError: 이메일 인증이 완료되지 않은 경우 예외 발생
    :return: 액세스 토큰 및 리프레시 토큰
    """
    if not email or not password:
        raise ValueError("이메일과 비밀번호를 입력해야 합니다.")

    # 이메일로 사용자 조회
    user = User.query.filter_by(email=email).first()

    if not user:
        print("[DEBUG] 사용자를 찾을 수 없음! (해당 이메일이 DB에 없음)")
        raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")
    
    print(f"[DEBUG] 조회된 사용자: {user.email}, 인증 상태: {user.is_verified}")

    is_password_correct = user.check_password(password)
    print(f"[DEBUG] 비밀번호 검증 결과: {is_password_correct}")

    if not is_password_correct:
        print(f"[DEBUG] 저장된 비밀번호 해시: {user.password_hash}")
        print(f"[DEBUG] 입력된 비밀번호: {password}")
        raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")

    if not user.is_verified:
        raise ValueError("이메일 인증이 완료되지 않았습니다. 이메일을 확인하세요.")
    
    print("[DEBUG] 비밀번호 검증 성공!")

    access_token = create_access_token(identity=user.user_id, expires_delta=timedelta(minutes=30))  
    refresh_token = create_refresh_token(identity=user.user_id, expires_delta=timedelta(days=7))

    # MongoDB에서 기존 로그인 세션 종료
    print("[DEBUG] MongoDB에 저장된 user_id:", user.user_id)
    mongo.db.user_sessions.delete_many({"user_id": user.user_id})  
    mongo.db.user_sessions.insert_one({"user_id": user.user_id})

    # MySQL에 로그인 기록 추가 (IP 포함)
    try:
        user_log = UserLog(user_id=user.user_id, action="login", ip_address=request.remote_addr)
        db.session.add(user_log)
        db.session.commit()  
        print("[DEBUG] 로그인 로그 저장 완료!")
    except Exception as e:
        db.session.rollback()  
        print(f"[ERROR] 로그인 로그 저장 실패: {str(e)}")

    # Redis에 토큰 저장
    r.setex(f"access_token_{user.user_id}", timedelta(minutes=30), access_token)
    r.setex(f"refresh_token_{user.user_id}", timedelta(days=7), refresh_token)

    # Redis에서 세션 상태를 'active'로 설정
    r.setex(f"user:{user.user_id}:session", timedelta(days=7), "active")
    current_app.logger.info(f"[DEBUG] Redis에 사용자 {user.user_id}의 세션 상태를 'active'로 설정: {r.get(f'user:{user.user_id}:session')}")

    return {
        "user_id": user.user_id,  
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def generate_tokens(user_id: str, access_token_expiry: int = 15, refresh_token_expiry: int = 60 * 24 * 7) -> tuple:
    """
    액세스 토큰 및 리프레시 토큰을 한 번의 호출로 생성

    :param user_id: 사용자 ID
    :param access_token_expiry: 액세스 토큰 유효 시간 (분)
    :param refresh_token_expiry: 리프레시 토큰 유효 시간 (분)
    :return: 액세스 토큰 및 리프레시 토큰 (tuple)
    """
    try:
        access_token = generate_token(user_id, expiration_minutes=access_token_expiry)
        
        refresh_token = generate_token(user_id, expiration_minutes=refresh_token_expiry)

        r.setex(f"access_token_{user_id}", timedelta(minutes=access_token_expiry), access_token)
        r.setex(f"refresh_token_{user_id}", timedelta(minutes=refresh_token_expiry), refresh_token)

        return access_token, refresh_token
    except Exception as e:
        raise ValueError(f"토큰 생성 중 오류 발생: {str(e)}")

def generate_token(user_id: str, expiration_minutes: int) -> str:
    """
    JWT 토큰 생성

    :param user_id: 사용자 ID
    :param expiration_minutes: 토큰 유효 시간 (분)
    :return: 생성된 JWT 토큰
    """
    try:
        expiration_time = datetime.now(timezone.utc) + timedelta(minutes=expiration_minutes)
        payload = {
            "sub": user_id, 
            "exp": expiration_time
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    except Exception as e:
        raise ValueError(f"토큰 생성 오류: {str(e)}")

def verify_token(token):
    """
    토큰 검증 (Redis에서 저장된 토큰인지 확인 포함)

    :param token: JWT 토큰
    :raises ValueError: 유효하지 않은 토큰 또는 만료된 토큰일 경우 예외 발생
    :return: user_id 문자열
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print("[DEBUG] 검증된 토큰 페이로드:", payload)
        
        # 'sub' 필드에서 user_id 추출
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("유효하지 않은 토큰: user_id 없음")
        
        # Redis에서 해당 사용자의 세션 상태 확인 (로그아웃된 사용자인지 확인)
        session_status = r.get(f"user:{user_id}:session")
        print(f"[DEBUG] Redis에서 세션 상태 확인: {session_status}")

        # Redis 세션이 만료되었더라도, 토큰이 유효하면 로그인 상태 유지
        if session_status is None:
            return user_id

        if session_status is None or session_status != b'active':  # 세션 상태가 'active'인지 비교
            raise ValueError("로그아웃된 사용자입니다. 다시 로그인해주세요.")
        
        print(f"[DEBUG] 검증된 user_id: {user_id}")
        return user_id
    
    except ExpiredSignatureError:
        raise ValueError("토큰이 만료되었습니다.")
    except JWTError:
        raise ValueError("유효하지 않은 토큰입니다.")


def request_password_reset(email):
    """
    비밀번호 재설정 요청 (중복 요청 방지 추가)

    :param email: 사용자 이메일
    :raises ValueError: 등록되지 않은 이메일, 너무 빈번한 요청일 경우 예외 발생
    :return: 이메일 발송 성공 메시지
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ValueError("해당 이메일을 사용하는 계정을 찾을 수 없습니다.")

    # Redis에서 중복 요청 여부 확인 (5분 내 요청 제한)
    if r.exists(f"password_reset_request:{email}"):
        raise ValueError("비밀번호 재설정 요청이 너무 자주 발생했습니다. 잠시 후 다시 시도하세요.")

    token = jwt.encode(
        {
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    reset_url = f"{BASE_URL}/reset-password?token={token}"

    msg = Message("비밀번호 재설정 요청", sender=MAIL_USERNAME, recipients=[email])
    msg.body = f"비밀번호를 재설정하려면 아래 링크를 클릭하세요:\n{reset_url}"
    msg.html = f"""
        <html>
        <body>
            <p>비밀번호를 재설정하려면 아래 버튼을 클릭하세요:</p>
            <p>
                <a href="{reset_url}" target="_blank" rel="noopener noreferrer"
                    style="display:inline-block; padding:10px 20px; background-color:#3498db;
                    color:#fff; text-decoration:none; border-radius:5px;">
                    비밀번호 재설정
                </a>
            </p>
            <p>또는 다음 링크를 복사하여 브라우저에 붙여넣으세요:</p>
            <p><a href="{reset_url}" target="_blank" rel="noopener noreferrer">{reset_url}</a></p>
        </body>
        </html>
    """


    # msg = Message("비밀번호 재설정 요청", sender=MAIL_USERNAME, recipients=[email])
    # msg.body = f"비밀번호를 재설정하려면 아래 링크를 클릭하세요:\n{reset_url}"

    try:
        mail.send(msg)
    except Exception as e:
        raise ValueError(f"이메일 전송 실패: {str(e)}")

    # Redis에 비밀번호 재설정 요청 기록 저장 (5분 유지)
    r.setex(f"password_reset_request:{email}", timedelta(minutes=5), "requested")

    return {"message": "비밀번호 재설정 링크를 이메일로 전송했습니다."}



def reset_password(token, email, new_password, confirm_password):
    """
    비밀번호 변경 (토큰 검증 후 새 비밀번호 저장)

    :param token: JWT 토큰
    :param email: 사용자 이메일
    :param new_password: 새 비밀번호
    :param confirm_password: 비밀번호 확인
    :raises ValueError: 유효하지 않은 토큰, 이메일 불일치, 비밀번호 조건 미충족 시 예외 발생
    :return: 성공 메시지
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["email"] != email:
            raise ValueError("이메일이 일치하지 않습니다.")
    except ExpiredSignatureError:
        raise ValueError("토큰이 만료되었습니다.")
    except JWTError:
        raise ValueError("유효하지 않은 토큰입니다.")

    if new_password != confirm_password:
        raise ValueError("비밀번호가 일치하지 않습니다.")

    if len(new_password) < 8:
        raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")

    user = User.query.filter_by(email=email).first()
    if not user:
        raise ValueError("사용자를 찾을 수 없습니다.")

    # 비밀번호 해싱 후 저장
    hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user.password_hash = hashed_password
    db.session.commit()

    return {"message": "비밀번호가 성공적으로 변경되었습니다."}

def refresh_token(refresh_token):
    """
    리프레시 토큰 검증 및 새로운 액세스 토큰 발급 (수정됨)

    :param refresh_token: 사용자 리프레시 토큰
    :raises ValueError: 유효하지 않은 토큰일 경우 예외 발생
    :return: 새 액세스 토큰
    """
    try:
        decoded_token = verify_token(refresh_token)
        access_token, _ = generate_tokens(decoded_token["user_id"])
        return {"access_token": access_token}
    except jwt.ExpiredSignatureError:
        raise ValueError("Refresh token has expired")
    except jwt.JWTError:
        raise ValueError("Invalid refresh token")
    
def verify_reset_password_token(token):
    """
    비밀번호 재설정 토큰 검증 로직

    :param token: 클라이언트에서 제공한 JWT 토큰
    :return: 유효한 경우 이메일 반환, 예외 발생 시 오류 메시지 반환
    """
    if not token:
        raise ValueError("토큰이 제공되지 않았습니다.")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"message": "토큰이 유효합니다.", "email": payload["email"]}
    except ExpiredSignatureError:
        raise ValueError("토큰이 만료되었습니다.")
    except JWTError:
        raise ValueError("유효하지 않은 토큰입니다.")