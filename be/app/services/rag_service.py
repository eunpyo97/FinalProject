"""
# RAG 검색 및 벡터 DB 관련 로직 담당

FAISS 벡터 DB 로드 및 검색 기능 제공
문서 검색 (retriever 활용)
검색된 문서에서 output 추출
"""

import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from config.settings import ActiveConfig

load_dotenv()

VECTOR_DB_PATH = ActiveConfig.VECTOR_DB_PATH

try:
    # FAISS 벡터 DB 로드
    vectorstore = FAISS.load_local(
        VECTOR_DB_PATH, OpenAIEmbeddings(), allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever()

    if retriever is None:
        raise RuntimeError(
            "retriever가 None입니다. 벡터 DB 로드에 실패했을 가능성이 있습니다."
        )
    print("FAISS 벡터 DB 로드 성공")
except Exception as e:
    print(f"모델 로드 중 오류 발생: {e}")
    raise


def retrieve_relevant_documents(user_message):
    """
    사용자의 입력을 기반으로 FAISS 벡터 DB에서 관련 문서를 검색하는 함수

    매개변수:
        user_message (str): 사용자가 입력한 메시지

    반환값:
        list: 검색된 문서 리스트 (각 문서는 metadata에 'output' 필드 포함)
    """
    if retriever is None:
        raise RuntimeError("retriever가 초기화되지 않았습니다. 벡터 DB를 확인하세요.")

    try:
        search_results = retriever.get_relevant_documents(user_message)
        return search_results
    except Exception as e:
        raise RuntimeError(f"RAG 검색 중 오류 발생: {str(e)}")


def preview_rag_search(user_message):
    """
    RAG 검색 결과 미리보기: 상담 사례의 'output'만 반환

    매개변수:
        user_message (str): 사용자가 입력한 메시지

    반환값:
        dict: 검색된 상담 사례 리스트 또는 오류 메시지
    """
    try:
        # 유사도 검색 수행
        search_results = retriever.get_relevant_documents(user_message)

        results = []
        for doc in search_results:
            # metadata에 "output" 필드가 있으면 사용
            if hasattr(doc, "metadata") and doc.metadata and "output" in doc.metadata:
                content = doc.metadata["output"].strip()
            elif hasattr(doc, "page_content") and doc.page_content:
                # "output:" 접두어 제거
                if doc.page_content.lower().startswith("output:"):
                    content = doc.page_content[len("output:") :].strip()
                else:
                    continue
            else:
                continue

            if content:
                results.append(content)

        if not results:
            return {
                "message": "관련된 상담 사례를 찾을 수 없습니다.",
                "retrieved_documents": [],
            }

        return {"retrieved_documents": results}

    except Exception as e:
        return {"error": str(e)}
