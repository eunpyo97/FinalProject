import os
import re
import uuid
import bcrypt
import redis
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from jose import jwt, ExpiredSignatureError, JWTError
from flask_mail import Mail, Message
from flask import current_app
from app.models import db, User

# 환경 변수 불러오기 (없으면 기본값 사용)
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "noreply@example.com")  
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")  
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")  
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))  
REDIS_DB = int(os.getenv("REDIS_DB", 0))  

mail = Mail()
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)  # Redis 설정

def validate_password(password):
    """
    비밀번호 복잡성 검사

    :param password: 입력된 비밀번호
    :raises ValueError: 비밀번호 조건이 충족되지 않을 경우 예외 발생
    """
    if len(password) < 8:
        raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
    if not any(c.isupper() for c in password):  # 대문자 포함 여부 확인
        raise ValueError("비밀번호에 최소 하나의 대문자가 포함되어야 합니다.")
    if not any(c.islower() for c in password):  # 소문자 포함 여부 확인
        raise ValueError("비밀번호에 최소 하나의 소문자가 포함되어야 합니다.")
    if not any(c.isdigit() for c in password):  # 숫자 포함 여부 확인
        raise ValueError("비밀번호에 최소 하나의 숫자가 포함되어야 합니다.")
    if not any(c in "@$!%*?&" for c in password):  # 특수문자 포함 여부 확인
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
    :raises ValueError: 유효하지 않은 이메일, 이미 존재하는 이메일, 비밀번호 불일치일 경우 예외 발생
    :return: 회원가입 성공 메시지
    """
    if not validate_email(email):
        raise ValueError("유효하지 않은 이메일 형식입니다.")

    if User.query.filter_by(email=email).first():
        raise ValueError("이미 존재하는 이메일입니다.")

    # 비밀번호와 비밀번호 확인이 일치하는지 체크
    if password != confirm_password:
        raise ValueError("비밀번호가 일치하지 않습니다.")

    validate_password(password)

    # UUID 생성 및 비밀번호 해싱
    user_id = str(uuid.uuid4())
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # DB에 is_verified=False로 저장 (이메일 인증 필요)
    new_user = User(email=email, user_id=user_id, password_hash=hashed_password, is_verified=False)
    db.session.add(new_user)
    db.session.commit()

    # 이메일 인증 요청
    send_verification_email(new_user)
    return {"message": "회원가입 요청이 완료되었습니다. 이메일을 확인하세요."}

    #### 추가로 생각할 부분 #############
    # 이메일 전송 실패 처리 및 재시도 안내 로직
    # 이메일 재전송 기능
    # 약관 동의 및 개인정보 처리방침
    # 인증 완료 후 자동으로 로그인
    # 이메일 인증을 위한 토큰 유효 기간 관리


def send_verification_email(user):
    """
    이메일 인증 링크 전송

    :param user: 사용자 객체
    :return: 이메일 전송 성공 여부
    """
    token = generate_token(user.user_id, expiration=60)  # 60분 유효
    verification_url = f"{BASE_URL}/auth/verify-email/{token}"

    msg = Message("이메일 인증", sender=MAIL_USERNAME, recipients=[user.email])
    msg.body = f"이메일 인증을 완료하려면 다음 링크를 클릭하세요: {verification_url}"

    try:
        mail.send(msg)
    except Exception as e:
        raise ValueError(f"이메일 발송 실패: {str(e)}")

    return True

def verify_email_token(token):
    """
    이메일 인증 처리

    :param token: 이메일 인증 토큰
    :raises ValueError: 유효하지 않은 또는 만료된 토큰일 경우 예외 발생
    :return: 이메일 인증 성공 메시지
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
    except ExpiredSignatureError:
        raise ValueError("이메일 인증 토큰이 만료되었습니다.")
    except JWTError:
        raise ValueError("유효하지 않은 토큰입니다.")

    # DB에서 사용자 검색
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        raise ValueError("해당 사용자를 찾을 수 없습니다.")

    # 이메일 인증 완료 (`is_verified=True`)
    user.is_verified = True
    db.session.commit()

    return {"message": "이메일 인증이 완료되었습니다. 이제 로그인이 가능합니다."}

def authenticate_user(email, password):
    """
    사용자 로그인 처리

    :param email: 사용자 이메일
    :param password: 비밀번호
    :raises ValueError: 이메일 또는 비밀번호가 잘못되었을 경우 예외 발생
    :raises ValueError: 탈퇴한 계정일 경우 예외 발생
    :return: 액세스 토큰 및 리프레시 토큰
    """
    # 이메일로 사용자 조회
    user = User.query.filter_by(email=email).first()

    # 사용자 없거나 비밀번호가 틀린 경우 예외 발생
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")

    # 탈퇴한 계정인지 확인
    if user.status == "deleted":
        raise ValueError("탈퇴한 계정입니다. 로그인할 수 없습니다.")

    # 토큰 생성
    return generate_tokens(user.user_id)

def generate_tokens(user_id: str, access_token_expiry: int = 15, refresh_token_expiry: int = 60 * 24 * 7) -> tuple:
    """
    액세스 토큰 및 리프레시 토큰을 한 번의 호출로 생성

    :param user_id: 사용자 ID
    :param access_token_expiry: 액세스 토큰 유효 시간 (분)
    :param refresh_token_expiry: 리프레시 토큰 유효 시간 (분)
    :return: 액세스 토큰 및 리프레시 토큰 (tuple)
    """
    try:
        # 액세스 토큰 생성
        access_token = generate_token(user_id, expiration_minutes=access_token_expiry)
        
        # 리프레시 토큰 생성
        refresh_token = generate_token(user_id, expiration_minutes=refresh_token_expiry)

        # Redis에 액세스 토큰 저장
        r.setex(f"access_token_{user_id}", timedelta(minutes=access_token_expiry), access_token)

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
            "user_id": user_id,
            "exp": expiration_time
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    except Exception as e:
        raise ValueError(f"토큰 생성 오류: {str(e)}")

def verify_token(token):
    """
    토큰 검증

    :param token: JWT 토큰
    :raises ValueError: 유효하지 않은 토큰 또는 만료된 토큰일 경우 예외 발생
    :return: 토큰 페이로드
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise ValueError("토큰이 만료되었습니다.")
    except JWTError:
        raise ValueError("유효하지 않은 토큰입니다.")

def request_password_reset(email):
    """비밀번호 재설정 요청 (이메일로 링크 전송)"""
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ValueError("해당 이메일을 사용하는 계정을 찾을 수 없습니다.")

    # JWT 토큰 생성 (30분 유효)
    token = jwt.encode(
        {
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    reset_url = f"{BASE_URL}/reset-password?token={token}"
    
    # 이메일 발송
    msg = Message("비밀번호 재설정 요청", sender=MAIL_USERNAME, recipients=[email])
    msg.body = f"비밀번호를 재설정하려면 아래 링크를 클릭하세요:\n{reset_url}"
    
    try:
        mail.send(msg)
    except Exception as e:
        raise ValueError(f"이메일 전송 실패: {str(e)}")

    return {"message": "비밀번호 재설정 링크를 이메일로 전송했습니다."}


def reset_password(token, email, new_password, confirm_password):
    """
    비밀번호 변경 (토큰 검증 후 새로운 비밀번호 저장)

    :param token: 이메일 인증을 위한 JWT 토큰
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

    # 비밀번호 유효성 체크
    validate_password(new_password)  # 기존 `validate_password` 함수 활용

    if new_password != confirm_password:
        raise ValueError("비밀번호가 일치하지 않습니다.")

    # 비밀번호 변경
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ValueError("사용자를 찾을 수 없습니다.")

    # 해싱 후 저장
    hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user.password_hash = hashed_password
    db.session.commit()

    return {"message": "비밀번호가 성공적으로 변경되었습니다."}
