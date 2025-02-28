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
  background-color: rgb(176, 213, 255);
  padding: 15px;
  font-size: 25px;
  font-weight: bold;
  color: white;
  border-bottom: 4px solid #ffffff;
  border-radius: 15px 15px 0 0;
  width: 100%;
  transition: transform 0.3s ease;
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

const ChatRoomDetail = ({ userId, chatroomId, setSelectedChatroom }) => {
  const webcamRef = useRef(null);
  const { emotion, confidence, setEmotion } = useEmotionStore();
  const { generateSummaryAndSave, loading } = useDiaryStore();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [conversationEnd, setConversationEnd] = useState(false);
  const [previousEmotion, setPreviousEmotion] = useState(null);
  const [previousConfidence, setPreviousConfidence] = useState(null);
  const [lastUserMessageTime, setLastUserMessageTime] = useState(null);

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const { chats, conversationEnd: endStatus } = await getChatHistory(
          chatroomId
        );
        console.log("채팅 내역 API 응답:", chats);
        setMessages(chats);
        setConversationEnd(endStatus);

        // 채팅 내역이 비어 있을 경우 백엔드에 초기 메시지 요청
        if (chats.length === 0 && emotion && !conversationEnd) {
          const { botResponse } = await sendEmotionChatMessage(chatroomId, "");
          setMessages((prev) => [
            ...prev,
            { user_message: null, bot_response: botResponse },
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

        // 감정이 변했거나 신뢰도 차이가 0.2 이상일 경우
        if (
          newEmotion !== previousEmotion ||
          Math.abs(previousConfidence - newConfidence) >= 0.2
        ) {
          setEmotion(newEmotion, newConfidence);
          setPreviousEmotion(newEmotion);
          setPreviousConfidence(newConfidence);

          // 사용자가 마지막으로 응답한 이후 일정 시간이 지났는지 확인 (5초)
          const now = Date.now();
          const userRespondedRecently =
            lastUserMessageTime && now - lastUserMessageTime < 5000;

          // 감정이 변했을 때 챗봇이 말을 걸도록
          // 감정이 변하더라도 신뢰도가 0.7 미만이면 챗봇이 말을 걸지 않음
          // 사용자가 응답하지 않은 경우, 같은 감정이면 챗봇이 말을 걸지 않음
          if (!conversationEnd && newConfidence >= 0.7) {
            if (!userRespondedRecently && newEmotion === previousEmotion)
              return;

            // 챗봇 응답
            const { botResponse } = await sendEmotionChatMessage(
              chatroomId,
              ""
            );
            setMessages((prev) => [
              ...prev,
              { user_message: null, bot_response: botResponse },
            ]);
          }
        }
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
    previousEmotion,
    previousConfidence,
    loading,
    conversationEnd,
    lastUserMessageTime,
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
    <div>
      <ChatBox>
        <ChatHeader>
          <button onClick={() => setSelectedChatroom(null)}>← 뒤로</button>
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
        <div>
          <p style={{ fontSize: "18px", fontWeight: "bold" }}>
            현재 감정: {emotion}
          </p>
          <p>신뢰도: {confidence}%</p>
          {/* <p>신뢰도: {(confidence * 100).toFixed(2)}%</p> */}
        </div>
      )}
    </div>
  );
};

export default ChatRoomDetail;
