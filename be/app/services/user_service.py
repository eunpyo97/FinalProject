from app.models import db, User
import re
from datetime import datetime, timezone
from jose import jwt, ExpiredSignatureError, JWTError
import os
from dotenv import load_dotenv

# 환경 변수에서 SECRET_KEY 가져오기
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")


def validate_password(password):
    """
    비밀번호 복잡성 검사

    - 최소 8자 이상
    - 대문자 포함
    - 소문자 포함
    - 숫자 포함
    - 특수문자 포함

    :param password: 입력된 비밀번호
    :raises ValueError: 비밀번호 조건이 충족되지 않을 경우 예외 발생
    """
    if len(password) < 8:
        raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
    if not re.search(r"[A-Z]", password):  # 대문자
        raise ValueError("비밀번호에 최소 하나의 대문자가 포함되어야 합니다.")
    if not re.search(r"[a-z]", password):  # 소문자
        raise ValueError("비밀번호에 최소 하나의 소문자가 포함되어야 합니다.")
    if not re.search(r"[0-9]", password):  # 숫자
        raise ValueError("비밀번호에 최소 하나의 숫자가 포함되어야 합니다.")
    if not re.search(r"[@$!%*?&]", password):  # 특수문자
        raise ValueError("비밀번호에 최소 하나의 특수문자가 포함되어야 합니다.")


def change_password(user_id, old_password, new_password):
    """
    비밀번호 변경

    :param user_id: 사용자 ID (UUID)
    :param old_password: 기존 비밀번호
    :param new_password: 새 비밀번호
    :raises ValueError: 사용자 존재 여부, 기존 비밀번호 검증 실패 시 예외 발생
    :return: 성공 메시지
    """
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        raise ValueError("해당 사용자를 찾을 수 없습니다.")

    if not user.check_password(old_password):  # 기존 비밀번호 검증
        raise ValueError("기존 비밀번호가 올바르지 않습니다.")

    validate_password(new_password)  # 새 비밀번호 복잡성 체크

    user.password = new_password  # set_password를 사용하여 비밀번호 설정
    db.session.commit()

    return {"message": "비밀번호 변경이 완료되었습니다."}


def delete_account(user_id, access_token):
    """
    회원 탈퇴 (소프트 삭제)

    :param user_id: 사용자 ID (UUID)
    :param access_token: 사용자 인증 토큰
    :raises ValueError: 잘못된 토큰 또는 사용자 정보가 없을 경우 예외 발생
    :raises PermissionError: 본인 계정이 아닌 경우 예외 발생
    :return: 성공 메시지
    """
    if not access_token:
        raise ValueError("액세스 토큰이 필요합니다.")

    try:
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
        token_user_id = decoded_token["user_id"]
    except ExpiredSignatureError:
        raise ValueError("액세스 토큰이 만료되었습니다.")
    except JWTError:
        raise ValueError("유효하지 않은 액세스 토큰입니다.")

    user = User.query.filter_by(user_id=token_user_id).first()
    if not user:
        raise ValueError("해당 사용자를 찾을 수 없습니다.")

    if user.user_id != user_id:
        raise PermissionError("본인 계정만 삭제할 수 있습니다.")

    user.deleted_at = datetime.now(timezone.utc)
    user.status = "deleted"
    db.session.commit()

    return {"message": "계정이 성공적으로 삭제되었습니다."}
