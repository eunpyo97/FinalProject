import { predictEmotion } from "../api/emotion";

/**
 * 웹캠에서 이미지 캡처 후 감정 인식 API 호출
 * @param {object} webcamRef - react-webcam의 ref 객체
 * @param {string} userId - 사용자 ID
 * @param {string} chatroomId - 채팅방 ID
 * @returns {Promise<{emotion: string, confidence: number}>} - 감정 인식 결과
 */
export const captureAndPredictEmotion = async (webcamRef, userId, chatroomId) => {
    if (!webcamRef || !webcamRef.current) {
      console.error("웹캠이 초기화되지 않았습니다.");
      return null;
    }
  
    // 웹캠 이미지 캡처
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) {
      console.error("이미지 캡처 실패");
      return null;
    }
  
    try {
      // 감정 인식 API 호출
      const result = await predictEmotion(imageSrc.split(",")[1], userId, chatroomId);  // Base64 데이터에서 앞부분 제외
      return {
        emotion: result.emotion,
        confidence: result.confidence,
      };
    } catch (error) {
      console.error("감정 인식 실패:", error);
      return null;
    }
  };
  