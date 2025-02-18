from flask import Blueprint, request, current_app, jsonify
from app.services.auth_service import (
    register_user,
    verify_email_token,
    authenticate_user,
    generate_tokens,
    verify_token,
    request_password_reset, 
    reset_password
)
from jose import jwt 
import logging

# 블루프린트 설정
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    회원가입 API

    요청 형식:
    {
        "email": "example@email.com",
        "password": "SecurePassword123!"
    }

    응답:
    201 Created
    {
        "message": "회원가입 성공. 이메일을 확인하세요."
    }
    """
    try:
        data = request.get_json()
        response = register_user(data["email"], data["password"], data["confirm_password"])
        return jsonify(response), 201

    except ValueError as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        current_app.logger.error(f"Unexpected error in registration: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500

    # try:
    #     data = request.get_json()
    #     response = register_user(data["email"], data["password"])
    #     return jsonify(response), 201

    # except ValueError as e:
    #     current_app.logger.error(f"Registration error: {str(e)}")
    #     raise  

@auth_bp.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    """
    이메일 인증 API

    요청: GET /auth/verify-email/<token>

    응답:
    200 OK
    {
        "message": "이메일 인증 성공"
    }
    """
    try:
        response = verify_email_token(token)
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Email verification error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        current_app.logger.error(f"Unexpected error in email verification: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500

    # except ValueError as e:
    #     current_app.logger.error(f"Email verification error: {str(e)}")
    #     raise  

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    로그인 API

    요청 형식:
    {
        "email": "example@email.com",
        "password": "SecurePassword123!",
        "remember_me": true
    }

    응답:
    200 OK
    {
        "access_token": "<JWT_ACCESS_TOKEN>",
        "refresh_token": "<JWT_REFRESH_TOKEN>",
        "redirect_url": "http://localhost:3000/home"
    }
    """
    try:
        data = request.get_json()
        email, password = data["email"], data["password"]
        remember_me = data.get("remember_me", False)

        access_token_expiry = 15 if not remember_me else 7 * 24 * 60  # 15분 또는 7일
        access_token, refresh_token = authenticate_user(email, password)

        redirect_url = f"{current_app.config['BASE_URL']}/home"

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "redirect_url": redirect_url
        }), 200

    except ValueError as e:
        current_app.logger.error(f"Login error: {str(e)}")
        raise  

@auth_bp.route("/token", methods=["PUT"])
def refresh():
    """
    리프레시 토큰 API

    요청 형식:
    {
        "refresh_token": "<JWT_REFRESH_TOKEN>"
    }

    응답:
    200 OK
    {
        "access_token": "<새로운 JWT_ACCESS_TOKEN>"
    }
    """
    try:
        data = request.get_json()
        refresh_token = data.get("refresh_token")

        if not refresh_token:
            raise ValueError("Refresh token is required")

        decoded_token = verify_token(refresh_token)
        user_id = decoded_token["user_id"]

        # 새로운 액세스 토큰 발급
        access_token, _ = generate_tokens(user_id, access_token_expiry=15)

        return jsonify({"access_token": access_token}), 200

    except jwt.ExpiredSignatureError:
        raise ValueError("Refresh token has expired")

    except jwt.JWTError:
        raise ValueError("Invalid refresh token")

    except Exception as e:
        current_app.logger.error(f"Error in token refresh: {str(e)}")
        raise  

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    로그아웃 API

    요청 형식:
    {
        "access_token": "<JWT_ACCESS_TOKEN>"
    }

    응답:
    200 OK
    {
        "message": "Logged out successfully"
    }
    """
    try:
        data = request.get_json()
        access_token = data.get("access_token")

        if not access_token:
            raise ValueError("Access token is required")

        decoded_token = verify_token(access_token)
        user_id = decoded_token["user_id"]

        # Redis에서 해당 access_token 삭제
        from app.services.auth_service import r
        r.delete(f"access_token_{user_id}")

        return jsonify({"message": "Logged out successfully"}), 200

    except jwt.ExpiredSignatureError:
        raise ValueError("Access token has expired")

    except jwt.JWTError:
        raise ValueError("Invalid access token")

    except Exception as e:
        current_app.logger.error(f"Error in logout: {str(e)}")
        raise  


@auth_bp.route("/reset-password-request", methods=["POST"])
def reset_password_request():
    """비밀번호 재설정 요청 (이메일로 인증 링크 전송)"""
    try:
        data = request.get_json()
        email = data.get("email")
        if not email:
            raise ValueError("이메일을 입력해야 합니다.")
        
        response = request_password_reset(email)
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Password reset request error: {str(e)}")
        raise  
    except Exception as e:
        current_app.logger.error(f"Unexpected error in reset-password-request: {str(e)}")
        raise  

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password_route():
    """비밀번호 재설정 (토큰 검증 후 비밀번호 변경)"""
    try:
        data = request.get_json()
        token = data.get("token")
        email = data.get("email")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if not all([token, email, new_password, confirm_password]):
            raise ValueError("모든 필드를 입력해야 합니다.")

        response = reset_password(token, email, new_password, confirm_password)
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Password reset error: {str(e)}")
        raise  
    except Exception as e:
        current_app.logger.error(f"Unexpected error in reset-password: {str(e)}")
        raise  