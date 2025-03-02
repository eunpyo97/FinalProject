from app.database import db
import bcrypt
from datetime import datetime, timezone
import uuid


class User(db.Model):
    """사용자 테이블"""

    __tablename__ = "users"  # 테이블 이름
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)  # 비밀번호 해시
    is_verified = db.Column(db.Boolean, default=False)  # 이메일 인증 여부
    is_admin = db.Column(db.Boolean, default=False)  # 관리자 여부
    status = db.Column(db.String(20), default="active")  # 'active', 'banned', 'deleted'
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )  # 계정 생성 시간
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )  # 마지막 수정 시간
    deleted_at = db.Column(db.DateTime, nullable=True)  # 삭제 시간

    @property
    def password(self):
        """비밀번호 속성 접근 금지"""
        raise AttributeError("Password is not a readable attribute.")

    @password.setter
    def password(self, password):
        """비밀번호 해시 생성 및 저장"""
        if not isinstance(password, bytes):  # 문자열이면 바이트로 변환
            password = password.encode("utf-8")
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        self.password_hash = hashed_password.decode("utf-8")  # 문자열로 변환하여 저장

    def check_password(self, password):
        """비밀번호 검증
        :param password: 입력된 비밀번호 (문자열)
        :return: 비밀번호가 일치하면 True, 그렇지 않으면 False
        """
        stored_hash = self.password_hash

        # 저장된 해시가 문자열(str)이면 바이트(bytes)로 변환
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode("utf-8")

        # 입력된 비밀번호를 bcrypt 해싱 규칙에 맞춰 바이트로 변환 후 비교
        is_match = bcrypt.checkpw(password.encode("utf-8"), stored_hash)

        print(f"[DEBUG] 입력된 비밀번호: {password}")
        print(f"[DEBUG] 저장된 해시 값: {self.password_hash}")
        print(f"[DEBUG] bcrypt.checkpw 결과: {is_match}")

        return is_match

    def soft_delete(self):
        """삭제"""
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self):
        """삭제된 계정 복구"""
        self.deleted_at = None

    def is_deleted(self):
        """삭제 여부 확인"""
        return self.deleted_at is not None

    def __repr__(self):
        return f"<User {self.email} status={self.status}>"


class UserProfile(db.Model):
    """사용자 프로필 테이블"""

    __tablename__ = "user_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.user_id"), nullable=False, unique=True
    )  # User와 1:1 관계
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    profile_image = db.Column(
        db.String(200), nullable=True, default="/static/default_profile.jpg"
    )  # 프로필 사진
    # bio = db.Column(db.String(200), nullable=True)  # 자기소개
    timezone = db.Column(db.String(50), nullable=True)  # 시간대

    user = db.relationship("User", backref=db.backref("profile", uselist=False))

    def __repr__(self):
        return f"<UserProfile {self.nickname}>"


# 이 프로젝트에선 필요 없어 보임 -> redis 저장...
class UserToken(db.Model):
    """사용자 토큰 관리 테이블"""

    __tablename__ = "user_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)  # 토큰 값
    token_type = db.Column(
        db.String(50), nullable=False
    )  # 토큰 유형 ('refresh', 'password_reset')
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )  # 생성 시간
    expires_at = db.Column(db.DateTime, nullable=False)  # 만료 시간
    revoked = db.Column(db.Boolean, default=False)  # 토큰 취소 여부

    user = db.relationship("User", backref=db.backref("tokens", lazy=True))

    def __repr__(self):
        return f"<UserToken user_id={self.user_id} type={self.token_type}>"


class UserLog(db.Model):
    """사용자 활동 로그 테이블"""

    __tablename__ = "user_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # 수행된 작업 (login, logout)
    ip_address = db.Column(db.String(45), nullable=True)  # 작업 발생 IP 주소
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )  # 작업 발생 시간

    user = db.relationship("User", backref=db.backref("logs", lazy=True))

    def __repr__(self):
        return f"<UserLog action={self.action} user_id={self.user_id}>"


class UserTime(db.Model):
    """사용자 시간 정보 테이블"""

    __tablename__ = "user_times"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )  # User와 1:1 관계
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )  # 계정 생성 시간
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )  # 마지막 수정 시간
    last_login = db.Column(db.DateTime, nullable=True)  # 마지막 로그인 시간
    deleted_at = db.Column(db.DateTime, nullable=True)  # 계정 삭제 시간

    user = db.relationship("User", backref=db.backref("time_info", uselist=False))

    def __repr__(self):
        return f"<UserTime user_id={self.user_id} last_login={self.last_login}>"
