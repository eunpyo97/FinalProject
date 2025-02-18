from flask import jsonify
import logging
from werkzeug.exceptions import (
    BadRequest, Unauthorized, Forbidden, NotFound, InternalServerError,
    MethodNotAllowed, UnsupportedMediaType, UnprocessableEntity, TooManyRequests
)
from jose.exceptions import ExpiredSignatureError, JWTError
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

def register_error_handlers(app):
    """공통 에러 핸들러 등록"""

    # 400 Bad Request (잘못된 요청)
    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return jsonify({
            "status": 400,
            "error": "잘못된 요청입니다.",
            "message": str(e) or "요청이 올바르지 않습니다."
        }), 400

    # 401 Unauthorized (인증 필요)
    @app.errorhandler(Unauthorized)
    def handle_unauthorized(e):
        return jsonify({
            "status": 401,
            "error": "인증이 필요합니다.",
            "message": str(e) or "로그인이 필요합니다."
        }), 401

    # 401 Unauthorized - 잘못된 JWT 토큰
    @app.errorhandler(JWTError)
    def handle_invalid_token(e):
        return jsonify({
            "status": 401,
            "error": "Invalid Token",
            "message": "유효하지 않은 토큰입니다. 다시 로그인하세요."
        }), 401

    # 401 Unauthorized - JWT 토큰 만료
    @app.errorhandler(ExpiredSignatureError)
    def handle_expired_token(e):
        return jsonify({
            "status": 401,
            "error": "Expired Token",
            "message": "토큰이 만료되었습니다. 다시 로그인하세요."
        }), 401

    # 403 Forbidden (권한 없음)
    @app.errorhandler(Forbidden)
    def handle_forbidden(e):
        return jsonify({
            "status": 403,
            "error": "접근이 제한되었습니다.",
            "message": str(e) or "이 작업을 수행할 권한이 없습니다."
        }), 403

    # 404 Not Found (요청한 리소스를 찾을 수 없음)
    @app.errorhandler(NotFound)
    def handle_not_found(e):
        return jsonify({
            "status": 404,
            "error": "요청한 리소스를 찾을 수 없습니다.",
            "message": str(e) or "잘못된 URL이거나 리소스가 존재하지 않습니다."
        }), 404

    # 405 Method Not Allowed (허용되지 않은 HTTP 메서드)
    @app.errorhandler(MethodNotAllowed)
    def handle_method_not_allowed(e):
        return jsonify({
            "status": 405,
            "error": "허용되지 않은 HTTP 메서드입니다.",
            "message": str(e) or "이 요청에 대해 지원되지 않는 메서드입니다."
        }), 405

    # 415 Unsupported Media Type (지원되지 않는 Content-Type)
    @app.errorhandler(UnsupportedMediaType)
    def handle_unsupported_media_type(e):
        return jsonify({
            "status": 415,
            "error": "지원되지 않는 미디어 타입입니다.",
            "message": str(e) or "요청의 Content-Type이 올바르지 않습니다."
        }), 415

    # 422 Unprocessable Entity (처리할 수 없는 요청 데이터)
    @app.errorhandler(UnprocessableEntity)
    def handle_unprocessable_entity(e):
        return jsonify({
            "status": 422,
            "error": "처리할 수 없는 요청입니다.",
            "message": str(e) or "요청 데이터를 처리할 수 없습니다. 입력값을 확인하세요."
        }), 422

    # 429 Too Many Requests (요청 제한 초과)
    @app.errorhandler(TooManyRequests)
    def handle_too_many_requests(e):
        return jsonify({
            "status": 429,
            "error": "요청 횟수가 초과되었습니다.",
            "message": str(e) or "일정 시간 동안 너무 많은 요청을 보냈습니다."
        }), 429

    # 500 Internal Server Error (서버 내부 오류)
    @app.errorhandler(InternalServerError)
    def handle_internal_server_error(e):
        logging.error(f"Internal Server Error: {str(e)}")  # 서버 로그 기록
        return jsonify({
            "status": 500,
            "error": "서버 내부 오류가 발생했습니다.",
            "message": "예기치 않은 오류가 발생했습니다. 관리자에게 문의하세요."
        }), 500

    # 데이터 무결성 오류 (중복 키 등)
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(e):
        return jsonify({
            "status": 400,
            "error": "데이터 무결성 오류", 
            "message": "중복된 값이 존재하거나, 잘못된 데이터입니다."
        }), 400

    # 데이터베이스 연결 오류
    @app.errorhandler(OperationalError)
    def handle_db_connection_error(e):
        logging.error(f"Database Connection Error: {str(e)}")  # 로그 기록 추가
        return jsonify({
            "status": 503,
            "error": "데이터베이스 연결 오류", 
            "message": "서버에서 데이터베이스에 연결할 수 없습니다."
        }), 503  # 500이 아닌 503으로 변경

    # 쿼리 실행 오류
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(e):
        logging.error(f"Database Query Error: {str(e)}")  # 로그 기록 추가
        return jsonify({
            "status": 500,
            "error": "데이터베이스 오류", 
            "message": "데이터 처리 중 오류가 발생했습니다."
        }), 500

    # 기본 예외 처리 (예측하지 못한 오류)
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        logging.error(f"Unhandled Exception: {str(e)}")  # 서버 로그에 기록
        return jsonify({
            "status": 500,
            "error": "알 수 없는 오류가 발생했습니다.",
            "message": str(e) or "예기치 않은 오류가 발생했습니다."
        }), 500
