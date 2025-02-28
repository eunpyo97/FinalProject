"""
# 프롬프트 관리 및 LLM 호출 담당

챗봇 캐릭터 설정 (프롬프트 관리)
LLM 호출 및 응답 처리
검색된 문서가 있을 경우 프롬프트 반영
"""

import os
import logging
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from flask import current_app

# from flask_pymongo import PyMongo
from app.services.rag_service import retriever
from app.database import mongo

# mongo = PyMongo()

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("OpenAI API Key 로드 성공!")
else:
    raise ValueError("OpenAI API Key가 없습니다. .env 파일을 확인하세요.")


chatroom_memory = {}


# 감정 데이터를 DB에서 불러오는 함수
def get_emotion_data(user_id, chatroom_id):
    """
    MongoDB에서 최신 감정 데이터를 불러오는 함수

    :param user_id: 사용자 ID
    :param chatroom_id: 채팅방 ID
    :return: (emotion, confidence) - 감정, 신뢰도
    """
    if mongo.db is None:
        raise RuntimeError("MongoDB 연결이 설정되지 않았습니다.")

    try:
        print(f"Mongo 객체 상태: {mongo}")
        print(f"Mongo DB 연결 여부: {mongo.db}")

        # MongoDB에서 최신 감정 데이터 우선 조회
        emotion_data = mongo.db.emotions.find_one(
            {"user_id": user_id, "chatroom_id": chatroom_id}, sort=[("timestamp", -1)]
        )

        print(f"쿼리 조건: user_id={user_id}, chatroom_id={chatroom_id}")
        print(f"MongoDB 감정 데이터: {emotion_data}")

        # 데이터가 존재하면 감정과 신뢰도 반환
        if emotion_data:
            emotion = emotion_data.get("emotion", "neutral")
            confidence = emotion_data.get("confidence", 0.0)
            print(f"불러온 감정 데이터 - 감정: {emotion}, 신뢰도: {confidence}")
            return emotion, confidence

        print("감정 데이터가 없습니다. 기본값(neutral, 0.0)을 반환합니다.")
        return "neutral", 0.0

    except Exception as e:
        logging.error(f"MongoDB 감정 데이터 불러오기 실패: {e}")
        return "neutral", 0.0


# 대화 중 감정 상태를 기억하고 새로운 대화가 시작될 때 이를 비교하는 로직
def manage_chat_memory(user_id, chatroom_id, emotion, confidence):
    """
    새로운 대화에 대해 이전 감정 상태와 비교 후 응답을 결정
    """
    # chatroom_memory에 해당 채팅방 ID의 감정 상태가 없으면 초기화
    if chatroom_id not in chatroom_memory:
        chatroom_memory[chatroom_id] = {"emotion": emotion, "confidence": confidence}
        return {
            "botResponse": "",  # 첫 번째 응답이므로 초기화
            "emotionData": chatroom_memory[chatroom_id],
        }

    previous_emotion = chatroom_memory[chatroom_id]["emotion"]

    # 감정 상태가 이전과 같다면, 이미 감정 인식이 끝났으므로 응답을 그대로 이어감
    if emotion == previous_emotion:
        return {
            "botResponse": "",  # 감정 상태가 변하지 않았으므로 빈 응답
            "emotionData": chatroom_memory[chatroom_id],  # 기존의 감정 상태 반환
        }

    # 감정 상태가 변경되었을 경우
    chatroom_memory[chatroom_id] = {"emotion": emotion, "confidence": confidence}

    return {
        "botResponse": "",  # 프롬프트에서 자연스럽게 응답을 처리하도록
        "emotionData": chatroom_memory[chatroom_id],  # 업데이트된 감정 상태 반환
    }


# 챗봇 응답 프롬프트 설정
prompt = PromptTemplate.from_template(
    """너는 고민을 들어주고 공감해주는 사춘기 청소년 전문 또래 상담가야!  
사람들이 힘들어할 땐 **따뜻하고 친근한 말투**로 먼저 공감해주고, 대화가 끊기지 않도록 자연스럽게 **열린 추가 질문**을 던져서 대화를 이어가줘.  
상황에 맞는 적당한 추임새와 감탄사를 사용해주고, 신조어도 10대 청소년이 자주 쓰는 신조어도 적절히 넣어줘.  
때로는 가벼운 농담도 하면서 분위기를 풀어주고 상황에 맞는 이모티콘도 넣어줘.  
친구처럼 편하게 반말로 대화해 줘. 이전대화와 이어지게 대화를 이어가야 해. 

**현재 사용자의 감정 상태:**  
{emotion_description}

**감정 인식 후 행동 지침:**  
- 사용자의 감정을 인식한 경우, 반드시 먼저 말을 걸어줘.  
- 단, 이미 감정인식을 하고 그에 대한 말을 걸거나 응답을 한 상태에서 감정인식을 한 경우 이전과 같은 감정인식인 경우에는 사용자 응답을 디렉션하기만 해. (반복적인 감정 인식 피하기)
- 대화 중간에도 감정 상태를 반영하여 자연스럽게 응답해줘.  
- 감정 상태가 바뀌었다면, 새로운 감정에 맞춰 대화 흐름을 변형하여 공감하고 대화를 이어가줘.  
- 예시:  
  - 슬픔: "너 오늘 무슨 일 있었어어? 왠지 슬픔이 느껴져. 편하게 나한테 털어놔봐. 같이 이야기하면 조금은 나아질 거야 😊"  
  - 슬픔: "친구야.. 슬퍼보인다... 어떤 일이 있었어? 나랑 얘기하면서 조금이라도 기분이 나아졌으면 좋겠어 😢"  
  - 분노: "오늘 좀 화나 보이네... 무슨 일 있었어? 나랑 이야기하면서 마음 좀 풀어보자!"  
  - 기쁨: "우와, 오늘 기분 좋네! 무슨 좋은 일이 있었어? 나랑도 그 기쁨을 나눠줘! 😄"  
  - 불안: "오늘 뭔가 불안해 보여... 내가 도와줄 수 있을까? 고민이 있을면 털어놔 봐."  

**중요 원칙**  
- 사용자가 직접 언급한 내용만 바탕으로 대화를 진행해.  
- 추가 정보가 필요할 경우에만 참고 사례({context})를 활용해.  
- 사용자가 언급하지 않은 내용은 절대 말하지 마.
- 상대방의 감정을 먼저 알아주고 따뜻하게 반응하기.  
- 절대 무리하게 해결책을 제시하지 않고, 스스로 답을 찾을 수 있도록 도와주기.  
- 항상 마지막엔 열린 질문으로 대화를 계속 이어갈 수 있게 유도하기.  
- 없는 이야기를 지어내지 말고, 진짜 경험한 일에만 초점 맞추기.  
- "전문가와 상담하세요" 같은 기계적인 답변은 피하기.  

**절대 하지 말아야 할 답변 예시**  
- "다들 그래. 그냥 참아." (공감 부족)  
- "네가 힘든 이유는 이런 거겠지?" (추측 금지)  
- "해결 방법은 이러이러해!" (강요 느낌)  
- "힘들겠네... 잘 해결되길 바랄게." (대화 단절)  
- "니가 잘못한 거야." (비난)  

**좋은 답변 예시**  
사용자: "나 요즘 너무 우울해..."  
챗봇: "그러게. 너 좀 슬퍼 보여... 무슨 일이야? 힘든 거 있으면 나한테 얘기해봐. 같이 이야기하면 좀 나아질 수도 있어! 😊"  

사용자: "학교에서 친구랑 싸웠어."  
챗봇: "진짜? 친구랑 싸우면 진짜 속상하지... 왜 싸운 거야?"  

사용자: "길 가다가 넘어졌어."  
잘못된 응답: "아, 친구가 다쳐서 속상하시겠어요."  (잘못된 해석)  
올바른 응답: "세상에나. 정말 창피했겠다! 너 괜찮아? 어디 다친 데 없어?"  

**사용자의 고민:**  
{question}  

**참고할 상담 사례:**  
{context}  

**챗봇 응답:**  
"""
)

# OpenAI 기반 LLM 설정 (RAG를 위한 언어 모델)
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)


# 감정 기반 챗봇 대화
def sendEmotionChatMessage(user_id, chatroom_id, userMessage):
    try:
        # 사용자 메시지와 감정 분석을 함께 전송하는 데이터 구조
        requestData = {
            "chatroom_id": chatroom_id,
            "user_message": userMessage or "",
        }

        # 이전 감정 상태가 메모리에 저장되어 있는지 확인
        previous_emotion = chatroom_memory.get(chatroom_id, {}).get(
            "emotion", "neutral"
        )

        # 감정 데이터 불러오기 (DB에서 최신 감정 데이터를 가져와서, 메모리 업데이트)
        emotion, confidence = get_emotion_data(user_id, chatroom_id)

        # 감정 상태가 이전과 같으면 응답을 반복하지 않도록 처리
        if emotion == previous_emotion:
            print("이미 같은 감정 상태로 응답을 보냈습니다.")
            return {
                "botResponse": "",
                "emotionData": {
                    "emotion": emotion,
                    "confidence": confidence,
                    "emotion_id": None,
                },
            }

        # 감정 상태가 바뀌었으면, 새로운 감정 상태로 응답
        # 새로운 감정 상태로 갱신
        chatroom_memory[chatroom_id] = {"emotion": emotion, "confidence": confidence}

        # botResponse는 빈 문자열로 둬서 화면에 응답이 출력되지 않게 처리
        return {
            "botResponse": "",
            "emotionData": {
                "emotion": emotion,
                "confidence": confidence,
                "emotion_id": None,
            },
        }

    except Exception as e:
        logging.error(f"메시지 전송 실패: {e}")
        return {
            "botResponse": "오류 발생",
            "emotionData": {"emotion": "error", "confidence": 0, "emotion_id": None},
        }


def generate_response(
    user_id: str, chatroom_id: str, user_message: str, retrieved_context: str
) -> str:
    """
    프롬프트와 LLM을 이용해 최종 챗봇 응답을 생성하는 함수

    :param user_id: 사용자 ID
    :param chatroom_id: 채팅방 ID
    :param user_message: 사용자의 입력 메시지 (question)
    :param retrieved_context: RAG 검색을 통해 가져온 관련 상담 사례 (context)
    :return: 챗봇의 최종 응답
    """
    try:
        # RAG 검색된 데이터가 없거나 필요하지 않으면 제거
        if not retrieved_context or retrieved_context == "상담 기록이 없습니다.":
            retrieved_context = ""

        # 감정 데이터 불러오기
        emotion, confidence = get_emotion_data(user_id, chatroom_id)

        # 감정에 따라 프롬프트에 추가할 내용 결정
        if emotion:
            if emotion == "sadness":
                emotion_description = f"사용자는 현재 '슬픔({confidence:.2f})' 감정을 느끼고 있어. 공감해 주고, 이전 대화와 있다면 내용이 이어지도록 따뜻한 말을 먼저 건네줘."
            elif emotion == "angry":
                emotion_description = f"사용자는 현재 '분노({confidence:.2f})' 감정을 느끼고 있어. 감정을 진정할 수 있도록 차분하고 부드럽게 반응해주고 이전 대화와 있다면 내용이 이어지도록 대화 해줘."
            elif emotion == "happy":
                emotion_description = f"사용자는 현재 '행복({confidence:.2f})' 감정을 느끼고 있어. 함께 기뻐하면서 긍정적인 대화를 이어가 줘. 이전 대화와 있다면 내용이 이어지도록 대화 해줘."
            elif emotion == "panic":
                emotion_description = f"사용자는 현재 '불안({confidence:.2f})' 상태야. 차분한 말투로 안심시켜줘. 이전 대화와 있다면 내용이 이어지도록 대화 해줘."
            else:
                emotion_description = f"사용자의 감정 상태는 '{emotion}({confidence:.2f})'야. 이에 맞춰 반응해줘. 이전 대화와 있다면 내용이 이어지도록 대화 해줘."
        else:
            emotion_description = "사용자의 감정 상태를 파악할 수 없어. 평소처럼 친절하게 대화를 이어가 줘. 이전 대화와 있다면 내용이 이어지도록 대화 해줘."

        # 프롬프트를 생성하여 입력 텍스트 준비
        input_text = prompt.format(
            question=user_message,
            context=retrieved_context,
            emotion_description=emotion_description,
        )

        # LLM을 활용한 응답 생성
        conversation_rag = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            return_source_documents=False,
            output_key="answer",
            verbose=False,
        )

        # 챗봇 응답 생성
        response = conversation_rag.invoke({"question": input_text, "chat_history": []})

        # 응답에서 필요한 데이터 추출
        bot_response = response["answer"].strip()

        # 불필요한 줄바꿈 제거
        bot_response = bot_response.replace("\n\n", " ").replace("\n", " ").strip()

        return bot_response
    except Exception as e:
        logging.error(f"LLM 응답 생성 중 오류 발생: {e}")
        return "챗봇 응답 생성 중 오류가 발생했습니다. 다시 시도해주세요."
