import api from "./config";

/**
 * 특정 채팅방의 종료 상태 조회
 * @param {string} chatroomId 
 * @returns {Promise<Object>} - { chatroom_id, conversation_end, emotion }
 */
export const getChatEndStatus = async (chatroomId) => {
  try {
    const response = await api.get(`/chat/${chatroomId}/end`);
    console.log(`[DEBUG] 채팅방(${chatroomId}) 종료 상태:`, response.data);
    return response.data;  
  } catch (error) {
    console.error(`[ERROR] 채팅방(${chatroomId}) 종료 상태 조회 실패:`, error);
    return { chatroom_id: chatroomId, conversation_end: false, emotion: "default" }; 
  }
};
