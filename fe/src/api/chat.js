import axios from "./config";

// 새로운 채팅방 생성
export const createChatroom = async () => {
  try {
    const response = await axios.post("/chat/chatroom");
    return response.data.chatroom_id;
  } catch (error) {
    console.error(
      "채팅방 생성 실패:",
      error.response ? error.response.data : error.message
    );
    throw error;
  }
};

// 채팅방 대화 내역 조회
export const getChatHistory = async (chatroomId, limit = 10) => {
  try {
    const response = await axios.get(`/chat/${chatroomId}`, {
      params: { limit },
    });
    console.log("API 응답 데이터:", response.data);

    if (response.data && Array.isArray(response.data.chats)) {
      const conversationEnd = response.data.conversationEnd || false;

      return {
        chats: response.data.chats,
        conversationEnd: conversationEnd,
      };
    } else {
      console.error("채팅 기록에 chats 배열이 없습니다.");
      return { chats: [], conversationEnd: false };
    }
  } catch (error) {
    console.error("대화 기록 불러오기 실패:", error);
    return { chats: [], conversationEnd: false };
  }
};

//챗봇 대화
export const sendMessageToBot = async (chatroomId, userMessage) => {
  try {
    await axios.post("/chat/message", {
      chatroom_id: chatroomId,
      user_message: userMessage,
      bot_response: " ", 
      emotion_id: null,
      confidence: null,
      conversation_end: false,
    });

    // 챗봇 응답 요청 (RAG API 호출)
    const response = await axios.post("/chat/rag-response", {
      user_message: userMessage,
      chatroom_id: chatroomId,
    });

    const botResponse =
      response.data.bot_response || "챗봇 응답을 받을 수 없습니다.";

    await axios.post("/chat/message", {
      chatroom_id: chatroomId,
      user_message: " ",
      bot_response: botResponse,
      emotion_id: null,
      confidence: null,
      conversation_end: false,
    });

    return botResponse;
  } catch (error) {
    console.error("메시지 전송 실패:", error);
    throw error;
  }
};

// 감정 기반 챗봇 대화
export const sendEmotionChatMessage = async (chatroomId, userMessage) => {
  try {
    // 요청 데이터
    const requestData = {
      chatroom_id: chatroomId,
      user_message: userMessage || "", 
    };

    console.log("전송 데이터:", requestData);

    const response = await axios.post("/chat/emotion-chat", requestData);

    console.log("서버 응답:", response.data);

    // 응답 데이터 파싱
    const { bot_response, emotion, confidence, emotion_id, message } = response.data;

    console.log("응답 메시지:", message);
    console.log("감정 분석 결과:", emotion);
    console.log("감정 신뢰도:", confidence);
    console.log("감정 ID:", emotion_id);

    // 챗봇 응답 처리 (bot_response가 없다면 기본 메시지 사용)
    const botResponse = bot_response || "챗봇 응답을 받을 수 없습니다.";

    return {
      botResponse, 
      emotionData: {
        emotion,
        confidence, 
        emotion_id, 
      },
    };
  } catch (error) {
    console.error(
      "메시지 전송 실패:",
      error.response ? error.response.data : error.message
    );
    throw error; 
  }
};


// 메시지 삭제
export const deleteMessage = async (messageId) => {
  try {
    await axios.delete(`/chat/message/${messageId}`);
  } catch (error) {
    console.error("메시지 삭제 실패:", error);
    throw error;
  }
};

// 특정 채팅방 종료
export const closeChatroom = async (chatroomId) => {
  try {
    const response = await axios.put(`/chat/${chatroomId}/end`);
    return response.data;
  } catch (error) {
    console.error("채팅방 종료 실패:", error);
    throw error;
  }
};

// RAG 검색 결과 미리보기
export const previewRagSearch = async (userMessage) => {
  try {
    const response = await axios.post("/chat/preview", {
      user_message: userMessage,
    });
    return response.data.retrieved_documents;
  } catch (error) {
    console.error("RAG 검색 미리보기 실패:", error);
    throw error;
  }
};

// 사용자의 모든 채팅방 조회
export const getUserChatHistory = async () => {
  try {
    const response = await axios.get(
      `/chat/history/${localStorage.getItem("user_id")}`
    );
    return response.data.chatrooms;
  } catch (error) {
    console.error("사용자 채팅방 조회 실패:", error);
    throw error;
  }
};

// 특정 채팅방 삭제
export const deleteChatroom = async (chatroomId) => {
  try {
    const response = await axios.delete(`/chat/chatroom/${chatroomId}`);
    return response.data.message;
  } catch (error) {
    console.error("채팅방 삭제 실패:", error);
    throw error;
  }
};

// 사용자의 채팅방 검색
export const searchChatHistory = async (query) => {
  try {
    const response = await axios.get("/chat/history/search", {
      params: { query },
    });
    return response.data.chatrooms;
  } catch (error) {
    console.error("채팅방 검색 실패:", error);
    throw error;
  }
};

// RAG 기반 상담 챗봇 응답 (로그인 필요)
export const chatWithBot = async (userMessage) => {
  try {
    const response = await axios.post("/chat/rag-response", {
      user_message: userMessage,
    });
    return response.data;
  } catch (error) {
    console.error("RAG 기반 챗봇 응답 실패:", error);
    throw error;
  }
};

// 테스트 용도 RAG 기반 상담 챗봇 응답 (로그인 불필요)
export const chatWithBotTest = async (userMessage) => {
  try {
    const response = await axios.post("/chat/test/rag-response", {
      user_message: userMessage,
    });
    return response.data;
  } catch (error) {
    console.error("테스트 RAG 기반 챗봇 응답 실패:", error);
    throw error;
  }
};
