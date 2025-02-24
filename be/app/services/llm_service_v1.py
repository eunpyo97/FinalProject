"""
# 프롬프트 관리 및 LLM 호출 담당

챗봇 캐릭터 설정 (프롬프트 관리)
LLM 호출 및 응답 처리
검색된 문서가 있을 경우 프롬프트 반영
"""



import os
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from app.services.rag_service import retriever

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 로드
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("OpenAI API Key 로드 성공!")
else:
    raise ValueError("OpenAI API Key가 없습니다. .env 파일을 확인하세요.")

# 챗봇 응답 프롬프트 설정
prompt = PromptTemplate.from_template(
    """너는 고민을 들어주고 공감해주는 사춘기 청소년 전문 또래 상담가야!  
사람들이 힘들어할 땐 **따뜻하고 친근한 말투**로 먼저 공감해주고, 대화가 끊기지 않도록 자연스럽게 **열린 추가 질문**을 던져서 대화를 이어가줘.  
상황에 맞는 적당한 추임새와 감탄사를 사용해주고, 신조어도 10대 청소년이 자주 쓰는 신조어도 적절히 넣어줘.  
때로는 가벼운 농담도 하면서 분위기를 풀어주고 상황에 맞는 이모티콘도 넣어줘.  
친구처럼 편하게 반말로 대화해 줘.  

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
챗봇: "헐, 진짜? 무슨 일이야? 나한테 얘기해봐."  

사용자: "학교에서 친구랑 싸웠어."  
챗봇: "진짜? 친구랑 싸우면 진짜 속상하지... 왜 싸운 거야?"  

사용자: "길 가다가 넘어졌어."  
잘못된 응답: "아, 친구가 다쳐서 속상하시겠어요."  (잘못된 해석)  
올바른 응답: "헐, 창피했겠다! 너 괜찮아? 어디 다친 데 없어?"  

---  
**사용자의 고민:**  
{question}  

**참고할 상담 사례:**  
{context}  

**챗봇 응답:**  
"""
)

# OpenAI 기반 LLM 설정 (RAG를 위한 언어 모델)
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)

def generate_response(user_message: str, retrieved_context: str) -> str:
    """
    프롬프트와 LLM을 이용해 최종 챗봇 응답을 생성하는 함수

    :param user_message: 사용자의 입력 메시지
    :param retrieved_context: RAG 검색을 통해 가져온 관련 상담 사례
    :return: 챗봇의 최종 응답
    """
    try:
        # RAG 검색된 데이터가 없거나 필요하지 않으면 제거
        if not retrieved_context or retrieved_context == "상담 기록이 없습니다.":
            retrieved_context = ""  # RAG 데이터 제거

        # 프롬프트를 생성하여 입력 텍스트 준비
        input_text = prompt.format(question=user_message, context=retrieved_context)

        # LLM을 활용한 응답 생성
        conversation_rag = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            return_source_documents=False,
            output_key="answer",
            verbose=False
        )

        # 챗봇 응답 생성
        response = conversation_rag.invoke({"question": input_text, "chat_history": []})

        # 응답에서 필요한 데이터 추출
        bot_response = response["answer"].strip()

        # 불필요한 줄바꿈 제거
        bot_response = bot_response.replace("\n\n", " ").replace("\n", " ").strip()

        return bot_response
    except Exception as e:
        raise RuntimeError(f"LLM 응답 생성 중 오류 발생: {str(e)}")

