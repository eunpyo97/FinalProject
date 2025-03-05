import openai
from dotenv import load_dotenv
import os
import logging
from app.database import mongo
from openai import OpenAI, OpenAIError, AuthenticationError, RateLimitError

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_summary(chatroom_id):
    """
    대화방 ID에 따른 요약 생성
    :param chatroom_id: 대화방 ID (문자열)
    """
    logging.info(f"[INFO] 대화방 ID: {chatroom_id} - 요약 요청 시작")

    try:
        chatroom = mongo.db.chatrooms.find_one(
            {"chatroom_id": chatroom_id}, {"chats": 1, "conversation_end": 1}
        )
        if not chatroom:
            logging.warning(
                f"[WARNING] 대화방 ID: {chatroom_id} - 해당 대화방을 찾을 수 없음"
            )
            return {"error": "해당 대화방을 찾을 수 없습니다."}, 404

        if not chatroom.get("conversation_end"):
            logging.warning(
                f"[WARNING] 대화방 ID: {chatroom_id} - 대화가 종료되지 않음"
            )
            return {"error": "대화가 종료되지 않았습니다."}, 400

        # 대화 내용 합치기
        conversation_text = ""
        for chat in chatroom.get("chats", []):
            user_message = chat.get("user_message", "").strip()
            bot_response = chat.get("bot_response", "").strip()
            if user_message or bot_response:
                conversation_text += f"User: {user_message}\nBot: {bot_response}\n"

        if not conversation_text.strip():
            logging.warning(f"[WARNING] 대화방 ID: {chatroom_id} - 대화 내용이 없음")
            return {"error": "대화 내용이 없습니다."}, 400

        logging.debug(
            f"[DEBUG] 대화방 ID: {chatroom_id} - 대화 내용: {conversation_text}"
        )

    except Exception as e:
        logging.error(f"[ERROR] MongoDB 쿼리 중 오류 발생: {e}")
        return {"error": "데이터베이스 오류"}, 500

    # 요약 프롬프트 만들기
    prompt = f"""
    아래 내용을 바탕으로 감성적인 일기를 생성하세요.
    - 일기는 개인적인 감정을 솔직하게 표현하며, 자연스러운 말투로 작성됩니다.
    - 이모지를 적절히 사용하여 감정을 생생하게 표현하세요.
    - 제공된 대화 내용만 기반으로 작성하고, 새로운 정보를 추가하지 마세요.
    - 날짜나 시간 정보를 임의로 작성하지 마세요. 
    - 문장을 자연스럽게 연결하여 완성된 글로 작성하세요.
    - 문장이 끊기지 않도록 주의하며, 완결성있게 마무리지으세요.
    - 8문장 내로 마무리 지어주세요.

    대화 내용:
    {conversation_text}
    일기 형식으로 요약:
    """

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        logging.info(f"[INFO] OpenAI API 호출 시작 - 대화방 ID: {chatroom_id}")
        response = client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.7,
            stop=["\n\n", "일기 끝"],
        )

        summary = response.choices[0].message.content.strip()

        summary = summary.replace("\n\n", " ").replace("\n", " ")

        logging.info(f"[INFO] OpenAI API 호출 완료 - 요약 결과: {summary}")
        return summary

    except OpenAIError as e:
        logging.error(f"[ERROR] OpenAI API 서버 오류: {e}")
        return {"error": f"OpenAI API 서버 오류: {str(e)}"}, 500

    except AuthenticationError as e:
        logging.error(f"[ERROR] OpenAI API 인증 오류: {e}")
        return {"error": "OpenAI API 인증 오류: API 키를 확인하세요."}, 500

    except RateLimitError as e:
        logging.error(f"[ERROR] OpenAI API 요청 한도 초과: {e}")
        return {"error": "OpenAI API 요청 한도 초과: 잠시 후 다시 시도하세요."}, 429

    except Exception as e:
        logging.error(f"[ERROR] OpenAI API 호출 중 예기치 않은 오류: {e}")
        return {"error": "서버 내부 오류"}, 500
