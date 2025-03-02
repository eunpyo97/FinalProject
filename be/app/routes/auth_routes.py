from flask import Blueprint, request, jsonify, current_app
from app.services.auth_service import (
    register_user,
    authenticate_user,
    generate_tokens,
    verify_token,
    reset_password,
    verify_email_status_service,
    verify_email_request_service,
    logout_service,
    send_verification_code_service,
    verify_email_service,
    validate_password,
    validate_email,
    generate_token,
    request_password_reset,
    verify_reset_password_token,
)
from jose import jwt
from app.models.users import User
import redis
import os
from werkzeug.security import generate_password_hash
from app.database import db, mongo
from datetime import timedelta



REDIS_HOST = os.getenv("REDIS_HOST", "localhost")  
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))  
REDIS_DB = int(os.getenv("REDIS_DB", 0))  

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    회원가입 API

    요청 형식:
    {
        "email": "example@email.com",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!"
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
        user = User.query.filter_by(email=data["email"]).first()
        if user:
            response["user_id"] = user.user_id 
        
        return jsonify(response), 201
    except ValueError as e:
        current_app.logger.error(f"Registration error: {str(e)}")

        # 회원가입 실패 시 MongoDB에서도 user_id 삭제 (롤백)
        if "email" in data:
            user = User.query.filter_by(email=data["email"]).first()
            if user:
                mongo.db.user_sessions.delete_one({"user_id": user.user_id})

        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in registration: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500


@auth_bp.route("/verify-email", methods=["POST"])
def verify_email():
    """
    이메일 인증 API (6자리 인증 코드 사용)

    요청 형식:
    {
        "email": "example@email.com",
        "code": "123456"
    }

    응답:
    200 OK
    {
        "message": "이메일 인증 성공"
    }
    """
    try:
        data = request.get_json()
        response = verify_email_service(data["email"], data["code"])  
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Email verification error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in email verification: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500


@auth_bp.route("/verify-email-status", methods=["GET"])
def verify_email_status():
    """
    이메일 인증 상태 확인 API
    사용자가 이메일을 입력하고 인증했는지 상태를 조회한다.

    요청 형식:
    GET /verify-email-status?email=example@email.com

    응답:
    {
        "verified": true  # 또는 false
    }
    """
    try:
        email = request.args.get("email")
        if not email:
            raise ValueError("이메일을 입력해야 합니다.")

        response = verify_email_status_service(email)
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Email verification status error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in email verification status check: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500

@auth_bp.route("/verify-email-request", methods=["POST"])
def verify_email_request():
    """
    이메일 인증 요청 API
    사용자가 이메일을 입력하고 인증 요청을 하면, 해당 이메일로 인증 코드가 전송됨.
    """
    try:
        data = request.get_json()
        email = data.get("email")
        if not email:
            raise ValueError("이메일을 입력해야 합니다.")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "이미 가입된 이메일입니다."}), 400

        # 인증 코드 반환을 위해 함수 호출
        response_data = send_verification_code_service(email)
        return jsonify(response_data), 200
    except ValueError as e:
        current_app.logger.error(f"Email verification request error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in email verification request: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500

    
@auth_bp.route("/resend-verification-code", methods=["POST"])
def resend_verification_code():
    """
    이메일 인증 코드 재전송 API

    요청 형식:
    {
        "email": "example@email.com"
    }

    응답:
    200 OK
    {
        "message": "새로운 인증 코드가 이메일로 전송되었습니다."
    }
    """
    try:
        data = request.get_json()
        email = data.get("email")
        if not email:
            raise ValueError("이메일을 입력해야 합니다.")

        response = send_verification_code_service(email) 
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Resend verification code error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in resending verification code: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    로그인 API

    요청 형식:
    {
        "email": "example@email.com",
        "password": "SecurePassword123!"
    }

    응답:
    200 OK
    {
        "access_token": "<JWT_ACCESS_TOKEN>",
        "refresh_token": "<JWT_REFRESH_TOKEN>"
    }
    :return: 로그인 성공 시 액세스 및 리프레시 토큰 반환
    """
    try:
        data = request.get_json()
        if not data:
            raise ValueError("잘못된 요청 형식입니다. JSON 데이터를 제공해야 합니다.")
        
        if "email" not in data or "password" not in data:
            raise ValueError("이메일과 비밀번호를 모두 입력해야 합니다.")

        current_app.logger.info(f"로그인 요청: {data['email']}")

        response = authenticate_user(data["email"], data["password"])
        
        if not response or "access_token" not in response:
            raise ValueError("인증 실패: 예상치 못한 응답 형식입니다.")

        current_app.logger.info(f"로그인 성공: user_id={response.get('user_id', 'Unknown')}")

    except ValueError as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except KeyError as e:
        current_app.logger.error(f"KeyError: 필수 필드 누락 {str(e)}")
        return jsonify({"error": "요청 데이터에 필요한 필드가 없습니다."}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in authentication: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500

    # MongoDB 조회
    try:
        active_sessions = mongo.db.user_sessions.count_documents({"user_id": response["user_id"]})
        current_app.logger.info(f"현재 로그인된 세션 수: {active_sessions}")

        if active_sessions > 1:
            current_app.logger.warning(f"MongoDB에 중복된 로그인 세션 감지: user_id={response['user_id']}")

    except Exception as e:
        current_app.logger.error(f"MongoDB 조회 중 오류 발생: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다. (DB 조회 실패)"}), 500

    return jsonify(response), 200


@auth_bp.route("/refresh-token", methods=["POST"])
def refresh():
    """
    리프레시 토큰을 이용해 새로운 액세스 토큰 발급
    """
    try:
        data = request.get_json()
        if not data or "refresh_token" not in data:
            raise ValueError("리프레시 토큰이 제공되지 않았습니다.")

        refresh_token = data["refresh_token"]
        current_app.logger.info(f"[DEBUG] 리프레시 토큰 검증 시작: {refresh_token}")

        # 리프레시 토큰 검증 및 user_id 추출
        user_id = verify_token(refresh_token)
        current_app.logger.info(f"[DEBUG] 검증된 user_id: {user_id}")

        # 세션 상태 확인 (Redis에서 세션 상태 가져오기)
        session_key = f"user:{user_id}:session"
        session_status = r.get(session_key)

        current_app.logger.info(f"[DEBUG] Redis에서 세션 상태 확인: {session_status}")
        if session_status is None or session_status != b'active':
            current_app.logger.error(f"[ERROR] 세션 상태 없음 또는 inactive: 로그아웃된 사용자입니다.")
            raise ValueError("로그아웃된 사용자입니다. 다시 로그인해주세요.")

        # 새로운 액세스 토큰 발급
        access_token, _ = generate_tokens(user_id)
        current_app.logger.info(f"[DEBUG] 새로운 액세스 토큰 발급 완료: {access_token}")

        return jsonify({"access_token": access_token}), 200

    except jwt.ExpiredSignatureError:
        current_app.logger.error("리프레시 토큰 만료됨")
        return jsonify({"error": "Refresh token has expired"}), 400

    except jwt.JWTError:
        current_app.logger.error("유효하지 않은 리프레시 토큰")
        return jsonify({"error": "Invalid refresh token"}), 400

    except ValueError as e:
        current_app.logger.error(f"Refresh token error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        current_app.logger.error(f"Unexpected error in refresh token: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500


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
        "message": "로그아웃이 완료되었습니다."
    }
    """
    try:
        data = request.get_json()
        # 먼저 토큰 검증을 통해 user_id를 얻음
        access_token = data.get("access_token")
        if not access_token:
            raise ValueError("토큰이 제공되지 않았습니다.")
        
        # user_id 추출
        user_id = verify_token(access_token)
        
        # MongoDB에서 해당 user_id의 로그인 세션 삭제
        mongo.db.user_sessions.delete_many({"user_id": user_id})
        
        # 로그아웃 서비스 호출하여 Redis에 저장된 토큰 무효화
        response = logout_service(access_token)
        return jsonify(response), 200

    except ValueError as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in logout: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500



@auth_bp.route("/request-password-reset", methods=["POST"])
def request_password_reset_route():
    """
    비밀번호 재설정 요청 API (이메일로 링크 전송)
    """
    try:
        data = request.get_json()
        if "email" not in data:
            raise ValueError("이메일을 입력해야 합니다.")

        response = request_password_reset(data["email"])
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Password reset request error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in password reset request: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500


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
        return jsonify({"error": str(e)}), 400 
    except Exception as e:
        current_app.logger.error(f"Unexpected error in reset-password: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500
    
@auth_bp.route("/reset-password", methods=["GET"])
def reset_password_page():
    """
    비밀번호 재설정 페이지 로드 (토큰 검증)
    """
    try:
        token = request.args.get("token")
        response = verify_reset_password_token(token)
        return jsonify(response), 200
    except ValueError as e:
        current_app.logger.error(f"Reset password error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in reset password: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500
