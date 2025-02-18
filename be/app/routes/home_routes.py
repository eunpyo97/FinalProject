from flask import Blueprint, jsonify, current_app

home_bp = Blueprint("home", __name__)

@home_bp.route("/", methods=["GET"])
def home():
    try:
        return jsonify({"message": "Welcome to RobotPet!"}), 200
    except Exception as e:
        current_app.logger.error(f"Error in home route: {str(e)}")
        raise  
