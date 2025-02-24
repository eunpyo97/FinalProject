import api from './config';

/**
 * 감정 예측 요청 함수
 * @param {string} imageData - Base64로 인코딩된 이미지 데이터
 * @param {string} userId - 사용자 ID
 * @param {string} chatroomId - 채팅방 ID
 * @returns {Promise<Object>} - 감정 예측 결과 (emotion, confidence)
 */
export const predictEmotion = async (imageData, userId, chatroomId) => {
  try {
    const response = await api.post('/emotion/predict', {
      frame: imageData,  // Base64 이미지 데이터
      user_id: userId,
      chatroom_id: chatroomId,
    });
    return response.data; // 감정 예측 결과
  } catch (error) {
    console.error('감정 예측 실패:', error);
    throw new Error('감정 예측 실패');
  }
};



/**
 * 감정 데이터를 MongoDB에 저장
 * @param {string} userId - 사용자 ID
 * @param {string} chatroomId - 채팅방 ID
 * @param {string} emotion - 예측된 감정
 * @param {number} confidence - 감정 신뢰도
 * @returns {Promise<Object>} - 저장된 결과
 */
export const saveEmotionData = async (userId, chatroomId, emotion, confidence) => {
  try {
    const response = await api.post('/emotion/save-emotion', {
      user_id: userId,
      chatroom_id: chatroomId,
      emotion,
      confidence,
    });
    return response.data;  // 감정 저장 성공/실패 결과
  } catch (error) {
    console.error('감정 데이터 저장 실패:', error);
    throw new Error('감정 데이터 저장 실패');
  }
};

/**
 * 특정 채팅방의 감정 분석 결과 조회
 * @param {string} chatroomId - 채팅방 ID
 * @returns {Promise<Object>} - 감정 분석 결과
 */
export const getEmotionResults = async (chatroomId) => {
  try {
    const response = await api.get(`/emotion/results/${chatroomId}`);
    return response.data;  // 감정 분석 결과
  } catch (error) {
    console.error('감정 결과 조회 실패:', error);
    throw new Error('감정 결과 조회 실패');
  }
};

/**
 * 감정 데이터 삭제
 * @param {string} emotionId - 삭제할 감정 데이터 ID
 * @returns {Promise<Object>} - 삭제 성공 여부
 */
export const deleteEmotionData = async (emotionId) => {
  try {
    const response = await api.delete(`/emotion/delete/${emotionId}`);
    return response.data;  // 삭제 성공/실패 결과
  } catch (error) {
    console.error('감정 데이터 삭제 실패:', error);
    throw new Error('감정 데이터 삭제 실패');
  }
};

/**
 * 자동 감정 종료 처리
 * @param {string} chatroomId - 채팅방 ID
 * @returns {Promise<Object>} - 처리 결과
 */
export const autoEndEmotions = async (chatroomId) => {
  try {
    const response = await api.post(`/emotion/auto-end/${chatroomId}`);
    return response.data;  // 자동 종료 처리 결과
  } catch (error) {
    console.error('자동 감정 종료 실패:', error);
    throw new Error('자동 감정 종료 실패');
  }
};

/**
 * 감정 분석 모델 상태 조회
 * @returns {Promise<Object>} - 모델 상태
 */
export const getModelStatus = async () => {
  try {
    const response = await api.get('/emotion/model-status');
    return response.data;  // 모델 상태
  } catch (error) {
    console.error('모델 상태 조회 실패:', error);
    throw new Error('모델 상태 조회 실패');
  }
};

/**
 * 사용자의 감정 분석 히스토리 조회
 * @param {string} userId - 사용자 ID
 * @returns {Promise<Object>} - 감정 분석 히스토리
 */
export const getUserEmotionHistory = async (userId) => {
  try {
    const response = await api.get(`/emotion/history/${userId}`);
    return response.data;  // 감정 히스토리
  } catch (error) {
    console.error('감정 히스토리 조회 실패:', error);
    throw new Error('감정 히스토리 조회 실패');
  }
};

/**
 * 가장 일반적인 감정 조회
 * @returns {Promise<Object>} - 가장 자주 나타나는 감정
 */
export const getMostCommonEmotion = async () => {
  try {
    const response = await api.get('/emotion/most-common');
    return response.data;  // 가장 자주 나타나는 감정
  } catch (error) {
    console.error('가장 일반적인 감정 조회 실패:', error);
    throw new Error('가장 일반적인 감정 조회 실패');
  }
};

/**
 * 감정 통계 조회
 * @returns {Promise<Object>} - 감정 통계
 */
export const getEmotionStatistics = async () => {
  try {
    const response = await api.get('/emotion/statistics');
    return response.data;  // 감정 통계
  } catch (error) {
    console.error('감정 통계 조회 실패:', error);
    throw new Error('감정 통계 조회 실패');
  }
};
