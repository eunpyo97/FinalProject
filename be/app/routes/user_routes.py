from flask import Blueprint, request, current_app, jsonify
from app.services.user_service import change_password, delete_account

# 블루프린트 설정
user_bp = Blueprint("user", __name__)


@user_bp.route("/<user_id>/password", methods=["PATCH"])
def change_password_route(user_id):
    """
    비밀번호 변경 API

    요청 형식:
    {
        "old_password": "이전 비밀번호",
        "new_password": "새 비밀번호"
    }

    :param user_id: 변경할 사용자 ID (UUID)
    :return: JSON 응답 (비밀번호 변경 성공 메시지)
    """
    try:
        data = request.get_json()
        if not data or "old_password" not in data or "new_password" not in data:
            raise ValueError("필수 요청 데이터가 누락되었습니다.")

        response = change_password(user_id, data["old_password"], data["new_password"])
        return jsonify(response), 200

    except ValueError as e:
        current_app.logger.error(f"Password change error: {str(e)}")
        raise  # `error_handler.py`에서 400 처리

    except Exception as e:
        current_app.logger.error(f"Unexpected error in change_password: {str(e)}")
        raise  # `error_handler.py`에서 500 처리


@user_bp.route("/<user_id>", methods=["DELETE"])
def delete_account_route(user_id):
    """
    회원 탈퇴 API

    요청 형식:
    {
        "access_token": "JWT_ACCESS_TOKEN"
    }

    :param user_id: 삭제할 사용자 ID (UUID)
    :return: JSON 응답 (회원 탈퇴 성공 메시지)
    """
    try:
        data = request.get_json()
        if not data or "access_token" not in data:
            raise ValueError("액세스 토큰이 필요합니다.")

        response = delete_account(user_id, data["access_token"])
        return jsonify(response), 200

    except ValueError as e:
        current_app.logger.error(f"Account deletion error: {str(e)}")
        raise  # `error_handler.py`에서 400 처리

    except PermissionError as e:
        current_app.logger.error(f"Permission error in delete_account: {str(e)}")
        raise  

    except Exception as e:
        current_app.logger.error(f"Unexpected error in delete_account: {str(e)}")
        raise  


@user_bp.route("/profile", methods=["GET"])
def get_profile():
    """
    프로필 조회 API (미구현)
    """
    raise NotImplementedError("프로필 조회 기능이 아직 구현되지 않았습니다.") 

@user_bp.route("/profile", methods=["PATCH"])
def update_profile():
    """
    프로필 수정 API (미구현)
    """
    raise NotImplementedError("프로필 수정 기능이 아직 구현되지 않았습니다.")

@user_bp.route("/<user_id>", methods=["GET"])
def get_user_info(user_id):
    """
    사용자 정보 조회 API(미구현)
    """
    raise NotImplementedError("사용자 정보 조회 기능이 아직 구현되지 않았습니다.")
