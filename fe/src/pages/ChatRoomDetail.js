import React, { useState, useEffect, useRef } from "react";
import {
  sendEmotionChatMessage,
  getChatHistory,
  closeChatroom,
} from "../api/chat";
import useEmotionStore from "../store/emotionStore";
import useDiaryStore from "../store/diaryStore";
import { predictEmotion } from "../api/emotion";
import styled from "styled-components";
import Webcam from "react-webcam";
import { ClockLoader } from "react-spinners";

// 날짜를 원하는 형식으로 변환하는 함수
const formatDate = (date) => {
  const hours = date.getHours().toString().padStart(2, "0");
  const minutes = date.getMinutes().toString().padStart(2, "0");
  const day = date.getDate().toString().padStart(2, "0");
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const year = date.getFullYear();
  return `${year}-${month}-${day} ${hours}:${minutes}`;
};

const ChatRoomWrapper = styled.div`
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  padding-top: 40px;
  background: linear-gradient(to top, rgb(213, 230, 249), #f0f4f8);
  background-size: cover;
  box-sizing: border-box;
  overflow-y: hidden;
`;

const ChatBox = styled.div`
  width: 100%;
  max-width: 430px;
  border: 2px solid #e0e0e0;
  border-radius: 20px;
  background-color: white;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1), 0 6px 6px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const ChatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(120deg, rgb(106, 159, 251), rgb(205, 98, 250));
  padding: 15px;
  font-size: 25px;
  font-weight: bold;
  color: white;
  text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
  border-bottom: 4px solid rgba(255, 255, 255, 0.5);
  border-radius: 15px 15px 0 0;
  width: 100%;
  position: relative;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
`;

const BackButton = styled.button`
  background-color: rgb(212, 223, 248);
  color: rgb(106, 14, 255);
  font-size: 16px;
  font-weight: bold;
  padding: 8px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;

  &:hover {
    background-color: rgba(249, 227, 252, 0.44);
    transform: scale(1.05);
  }

  &:active {
    background-color: rgba(249, 227, 252, 0.67);
    transform: scale(0.95);
  }
`;

const ChatHistory = styled.div`
  padding: 20px;
  height: 450px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #a3c6ed #f0f0f0;
  width: 100%;

  &::-webkit-scrollbar {
    width: 10px;
  }

  &::-webkit-scrollbar-thumb {
    background-color: #a3c6ed;
    border-radius: 10px;
  }

  &::-webkit-scrollbar-track {
    background-color: rgb(104, 197, 251);
  }
`;

const MessageContainer = styled.div`
  display: flex;
  width: 100%;
  justify-content: ${({ isUser }) => (isUser ? "flex-end" : "flex-start")};
  margin-bottom: 10px;
`;

const MessageBubble = styled.div`
  max-width: 70%;
  padding: 10px;
  border-radius: 10px;
  font-size: 14px;
  background: ${({ isUser }) => (isUser ? "#a3cafa" : "#fbe4f5")};
  color: ${({ isUser }) => (isUser ? "white" : "black")};
  word-wrap: break-word;
  text-align: left;
  transition: transform 0.3s ease, box-shadow 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
`;

const InputContainer = styled.div`
  display: flex;
  padding: 10px;
  background-color: rgb(241, 241, 241);
  border-top: 1px solid #e0e0e0;
  width: 100%;
`;

const Input = styled.input`
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 20px;
  background-color: ${({ disabled }) => (disabled ? "#f1f1f1" : "white")};
  color: ${({ disabled }) => (disabled ? "#ccc" : "black")};
  cursor: ${({ disabled }) => (disabled ? "not-allowed" : "text")};
  transition: background-color 0.3s ease;

  &:focus {
    outline: none;
    box-shadow: 0 0 5px rgba(0, 140, 255, 0.5);
  }
`;

const Button = styled.button`
  margin-left: 10px;
  padding: 10px 15px;
  background-color: ${({ disabled }) => (disabled ? "#cccccc" : "#A3C6ED")};
  color: ${({ disabled }) => (disabled ? "#999" : "white")};
  border: none;
  border-radius: 20px;
  cursor: ${({ disabled }) => (disabled ? "not-allowed" : "pointer")};
  transition: background-color 0.3s ease, transform 0.3s ease;

  &:hover:not(:disabled) {
    background-color: ${({ disabled }) => (disabled ? "#cccccc" : "#4a90e2")};
    transform: scale(1.05);
  }

  &:active:not(:disabled) {
    transform: scale(0.95);
  }
`;

const EndButtonContainer = styled.div`
  display: flex;
  justify-content: left;
  padding: 10px;
  background-color: rgb(241, 241, 241);
  border-top: 1px solid #e0e0e0;
  border-radius: 0 0 15px 15px;
  width: 100%;
`;

const EndButton = styled.button`
  margin-left: 15px;
  padding: 10px;
  background-color: ${({ disabled }) => (disabled ? "#cccccc" : "#dc3545")};
  color: ${({ disabled }) => (disabled ? "#999" : "white")};
  border: none;
  border-radius: 5px;
  cursor: ${({ disabled }) => (disabled ? "not-allowed" : "pointer")};
`;

const EndButtonText = styled.span`
  margin-left: 10px;
`;

const WebcamContainer = styled.div`
  width: 100%;
  max-width: 400px;
  margin: 20px auto;
  margin-bottom: 20px;
  border-radius: 15px;
  background-color: black;
  height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;

  &::before {
    content: "감정 인식 중...";
    position: absolute;
    bottom: 10px;
    left: 10px;
    color: white;
    font-size: 14px;
    opacity: 0.8;
  }
`;

const EmotionStatusContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  width: fit-content;
  margin-bottom: 50px;
`;

const LoadingOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5); 
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; 
  visibility: ${({ visible }) => (visible ? "visible" : "hidden")};
  opacity: ${({ visible }) => (visible ? 1 : 0)};
  transition: visibility 0.3s ease, opacity 0.3s ease;
`;

const LoadingSpinnerContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
  font-size: 18px;
  font-weight: bold;
`;


const ChatRoomDetail = ({ userId, chatroomId, setSelectedChatroom }) => {
  const webcamRef = useRef(null);
  const { emotion, confidence, setEmotion } = useEmotionStore();
  const { generateSummaryAndSave, loading } = useDiaryStore();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [conversationEnd, setConversationEnd] = useState(false);
  const [lastUserMessageTime, setLastUserMessageTime] = useState(null);

  const prevEmotionRef = useRef(null);
  const prevConfidenceRef = useRef(null);

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const { chats, conversationEnd: endStatus } = await getChatHistory(
          chatroomId
        );
        console.log("채팅 내역 API 응답:", chats);
        setMessages(chats);
        setConversationEnd(endStatus);

        // 채팅 내역이 비어 있을 경우, 첫 메시지를 전송 (첫 메시지는 감정 반영할 수도, 아닐 수도 있음)
        if (chats.length === 0 && !conversationEnd) {
          const { botResponse, isEmotionApplied } =
            await sendEmotionChatMessage(chatroomId, "");
          setMessages((prev) => [
            ...prev,
            {
              user_message: null,
              bot_response: botResponse,
              emotionApplied: isEmotionApplied,
            },
          ]);
        }
      } catch (error) {
        console.error("채팅 내역을 가져오는 데 실패했습니다:", error);
      }
    };
    fetchMessages();
  }, [chatroomId, emotion, confidence, conversationEnd]);

  // 주기적으로 감정 인식 및 감정 변화 반영
  useEffect(() => {
    const interval = setInterval(async () => {
      if (!webcamRef.current || loading || conversationEnd) return;
      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) return;
      try {
        const result = await predictEmotion(imageSrc, userId, chatroomId);
        const { emotion: newEmotion, confidence: newConfidence } = result;

        // 화면에는 5초마다 감정 분석 결과(감정, 신뢰도)를 그대로 표시 (neutral이라도 표시)
        setEmotion(newEmotion, newConfidence);

        // 감정 변화 판단
        // - 신뢰도 0.7 이상일 때만 감정 변화 고려
        // - 기본 메시지(감정 인식 없음) 이후 첫 감정 인식에서는 prevEmotionRef가 null이므로 무조건 메시지 전송
        // - 그 외, 다른 감정이면 메시지 전송, 같은 감정이면 이전 신뢰도 대비 0.2 이상 상승했을 때만 메시지 전송
        let emotionChanged = false;
        if (newConfidence >= 0.7) {
          if (prevEmotionRef.current === null) {
            // 기본 메시지 이후 첫 감정 인식: 무조건 메시지 전송
            emotionChanged = true;
          } else if (newEmotion !== prevEmotionRef.current) {
            emotionChanged = true;
          } else if (
            newEmotion === prevEmotionRef.current &&
            prevConfidenceRef.current !== null &&
            newConfidence > prevConfidenceRef.current + 0.2
          ) {
            emotionChanged = true;
          }
        }

        // 메시지 전송 로직
        // 추가 메시지는 신뢰도 0.7 이상이며 감정 변화가 감지된 경우에만 전송됨
        if (newConfidence >= 0.7 && emotionChanged) {
          const response = await sendEmotionChatMessage(chatroomId, "");
          const botMessage = response.emotionResponse;
          setMessages((prev) => [
            ...prev,
            {
              user_message: null,
              bot_response: botMessage,
              emotionApplied: true,
            },
          ]);
        }

        // 이전 감정 및 신뢰도 업데이트
        prevEmotionRef.current = newEmotion;
        prevConfidenceRef.current = newConfidence;
      } catch (error) {
        console.error("감정 인식 실패:", error);
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [
    userId,
    chatroomId,
    emotion,
    setEmotion,
    loading,
    conversationEnd,
    lastUserMessageTime,
    messages,
  ]);

  // 사용자 메시지 전송 함수
  const sendMessage = async () => {
    if (!input.trim() || conversationEnd) return;
    setLastUserMessageTime(Date.now());

    const userMessage = {
      user_id: userId,
      user_message: input,
      bot_response: "응답 대기 중...",
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    try {
      const { botResponse, emotion, confidence } = await sendEmotionChatMessage(
        chatroomId,
        input
      );
      setMessages((prev) =>
        prev.map((msg, index) =>
          index === prev.length - 1
            ? { ...msg, bot_response: botResponse }
            : msg
        )
      );
      setEmotion(emotion, confidence);
    } catch (error) {
      console.error("메시지 전송 실패:", error);
    }
  };

  // 대화 종료 처리
  const handleEndConversation = async () => {
    try {
      const response = await closeChatroom(chatroomId);
      if (response) {
        setConversationEnd(true);

        await generateSummaryAndSave(chatroomId);

        // 웹캠 스트림 종료
        if (webcamRef.current && webcamRef.current.video.srcObject) {
          const stream = webcamRef.current.video.srcObject;
          stream.getTracks().forEach((track) => track.stop());
          webcamRef.current.video.srcObject = null;
        }

        alert("대화가 종료되었습니다. 요약이 저장되었습니다.");
      }
    } catch (error) {
      console.error("대화 종료 실패:", error);
    }
  };

  // 날짜를 가져오기 위해 chatroomId 대신 Date를 사용하여 포맷
  const chatroomDate = new Date();
  const formattedDate = formatDate(chatroomDate);

  return (
    <>
      {/* 로딩 중일 때 어두운 오버레이 */}
      <LoadingOverlay visible={loading}>
        <LoadingSpinnerContainer>
          <ClockLoader color="#ffffff" size={50} />
          <div style={{ marginTop: "20px" }}>저장 중...</div>
        </LoadingSpinnerContainer>
      </LoadingOverlay>
  
      <ChatRoomWrapper>
        <ChatBox>
          <ChatHeader>
            <BackButton onClick={() => setSelectedChatroom(null)}>
              ← 뒤로
            </BackButton>
            <span style={{ marginLeft: "55px" }}>내 친구</span>
            <span style={{ fontSize: "15px" }}>{formattedDate}</span>
          </ChatHeader>
          <ChatHistory>
            {messages.length > 0 ? (
              messages.map((msg, index) => (
                <React.Fragment key={index}>
                  {msg.user_message && (
                    <MessageContainer isUser={true}>
                      <MessageBubble isUser={true}>
                        {msg.user_message}
                      </MessageBubble>
                    </MessageContainer>
                  )}
                  {msg.bot_response && (
                    <MessageContainer isUser={false}>
                      <MessageBubble isUser={false}>
                        {msg.bot_response}
                      </MessageBubble>
                    </MessageContainer>
                  )}
                </React.Fragment>
              ))
            ) : (
              <p>채팅 내역이 없습니다.</p>
            )}
          </ChatHistory>
          <InputContainer>
            <Input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                conversationEnd
                  ? "대화가 종료되었습니다"
                  : "메시지를 입력하세요..."
              }
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              disabled={conversationEnd}
            />
            <Button onClick={sendMessage} disabled={conversationEnd}>
              전송
            </Button>
          </InputContainer>
          {/* 대화 종료하기 버튼 */}
          <EndButtonContainer>
            <EndButton
              onClick={handleEndConversation}
              disabled={conversationEnd || loading}
            >
              {/* 로딩 중일 때 스피너와 텍스트 함께 표시 */}
              {loading ? (
                <>
                  <ClockLoader color="#ffffff" size={20} />
                  <EndButtonText>저장 중...</EndButtonText>
                </>
              ) : (
                "대화 종료하기"
              )}
            </EndButton>
          </EndButtonContainer>
        </ChatBox>
      </ChatRoomWrapper>
  
      {/* 웹캠 화면 */}
      {!conversationEnd && (
        <WebcamContainer>
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            videoConstraints={{ facingMode: "user" }}
            style={{
              display: "block",
              width: "100%",
              borderRadius: "10px",
            }}
          />
        </WebcamContainer>
      )}
  
      {/* 감정 상태 표시 */}
      {emotion && !conversationEnd && (
        <EmotionStatusContainer>
          <p style={{ fontSize: "18px", fontWeight: "bold" }}>
            현재 감정: {emotion}
          </p>
          <p>신뢰도: {confidence}%</p>
        </EmotionStatusContainer>
      )}
    </>
  );
  };
  
  export default ChatRoomDetail;