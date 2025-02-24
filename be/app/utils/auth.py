from functools import wraps
from flask import jsonify, current_app, request
from flask_jwt_extended import decode_token
from jwt.exceptions import DecodeError, ExpiredSignatureError  

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id, error = extract_jwt_token()
        
        if error:
            return jsonify({"error": error}), 401
        
        current_app.config["USER"] = {"user_id": user_id}  # 현재 사용자 정보 저장
        return f(*args, **kwargs)
    
    return decorated_function


def jwt_required_without_bearer(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id, error = extract_jwt_token()
        
        if error:
            return jsonify({"error": error}), 401
        
        request.user_id = user_id 
        return f(*args, **kwargs)

    return decorated_function


def extract_jwt_token():
    """Authorization 헤더에서 JWT 토큰 추출 및 디코딩"""
    token = request.headers.get('Authorization')
    
    if not token:
        return None, "JWT 토큰이 필요합니다."

    if token.startswith("Bearer "):
        token = token[len("Bearer "):]
    
    try:
        decoded_token = decode_token(token)
        
        current_app.logger.info(f"Decoded token: {decoded_token}")
        
        user_id = decoded_token.get("sub")  
        
        if not user_id:
            return None, "유효하지 않은 토큰: 'sub' 필드가 없음."
        
        return user_id, None
    except DecodeError:
        return None, "유효하지 않은 토큰입니다."
    except ExpiredSignatureError:
        return None, "토큰이 만료되었습니다."
