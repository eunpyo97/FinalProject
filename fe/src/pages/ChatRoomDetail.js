import React, { useState, useEffect, useRef } from "react";
import {
  sendEmotionChatMessage,
  getChatHistory,
  closeChatroom,
} from "../api/chat";
// import { sendMessageToBot } from "../api/chat";
import useEmotionStore from "../store/emotionStore";
import { predictEmotion } from "../api/emotion";
import styled from "styled-components";
import Webcam from "react-webcam";

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
  border: 2px solid #eeeeee;
  border-radius: 15px;
  background-color: white;
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.22);
  margin-top: 20px;
`;

const ChatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: rgb(244, 244, 244);
  padding: 10px;
  font-size: 18px;
  border-bottom: 4px solid white;
`;

const ChatHistory = styled.div`
  padding: 20px;
  height: 450px;
  overflow-y: auto;
  scrollbar-width: thin;
  &::-webkit-scrollbar {
    display: block;
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
`;

const InputContainer = styled.div`
  display: flex;
  padding: 10px;
  background-color: rgb(241, 241, 241);
`;

const Input = styled.input`
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 5px;
  background-color: ${({ disabled }) => (disabled ? "#f1f1f1" : "white")};
  color: ${({ disabled }) => (disabled ? "#ccc" : "black")};
  cursor: ${({ disabled }) => (disabled ? "not-allowed" : "text")};
`;

const Button = styled.button`
  margin-left: 5px;
  padding: 10px;
  background-color: ${({ disabled }) => (disabled ? "#cccccc" : "#A3C6ED")};
  color: ${({ disabled }) => (disabled ? "#999" : "white")};
  border: none;
  border-radius: 5px;
  cursor: ${({ disabled }) => (disabled ? "not-allowed" : "pointer")};
`;

const EndButton = styled.button`
  margin-left: 5px;
  padding: 10px;
  background-color: ${({ disabled }) => (disabled ? "#cccccc" : "#dc3545")};
  color: ${({ disabled }) => (disabled ? "#999" : "white")};
  border: none;
  border-radius: 5px;
  cursor: ${({ disabled }) => (disabled ? "not-allowed" : "pointer")};
`;

const WebcamContainer = styled.div`
  width: 50%;
  max-width: 430px;
  margin-bottom: 20px;
  border-radius: 15px;
  background-color: black;
  height: 200px; // 웹캠 화면 크기 설정
  display: flex;
  justify-content: center;
  align-items: center;
`;

const ChatRoomDetail = ({ userId, chatroomId, setSelectedChatroom }) => {
  const webcamRef = useRef(null);
  const { emotion, confidence, setEmotion } = useEmotionStore();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [conversationEnd, setConversationEnd] = useState(false);
  const [previousEmotion, setPreviousEmotion] = useState(null);
  const [loading, setLoading] = useState(false);
  const [previousConfidence, setPreviousConfidence] = useState(null);

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
  // useEffect(() => {
  //   const fetchMessages = async () => {
  //     try {
  //       // 채팅 내역 가져오기
  //       const { chats, conversationEnd: endStatus } = await getChatHistory(chatroomId);
  //       console.log("채팅 내역 API 응답:", chats);
  //       setMessages(chats);
  //       setConversationEnd(endStatus);

  //       // 채팅 내역이 비어 있고, 감정 데이터가 있으면 초기 메시지 생성
  //       if (chats.length === 0 && emotion && !conversationEnd) {
  //         let initialMessage = "안녕! 오늘 기분 어때? 나랑 얘기해볼래?";
  //         if (emotion === "sadness") {
  //           initialMessage = "너 요즘 좀 힘든 것 같아... 무슨 일이야? 나한테 얘기해봐.";
  //         } else if (emotion === "angry") {
  //           initialMessage = "뭔가 진짜 화나는 일이 있었던 거 같아. 나한테 얘기해봐, 들어줄게.";
  //         } else if (emotion === "happy") {
  //           initialMessage = "오늘 완전 기분 좋네! 무슨 일이야? 같이 기뻐하고 싶어!";
  //         } else if (emotion === "panic") {
  //           initialMessage = "너 요즘 좀 불안한 것 같아... 내가 도와줄 수 있을까?";
  //         }

  //         // 초기 메시지를 채팅창에 추가
  //         setMessages((prev) => [
  //           ...prev,
  //           { user_message: null, bot_response: initialMessage },
  //         ]);
  //       }
  //     } catch (error) {
  //       console.error("채팅 내역을 가져오는 데 실패했습니다:", error);
  //     }
  //   };
  //   fetchMessages();
  // }, [chatroomId, emotion, confidence, conversationEnd]);

  // 주기적으로 감정 인식 및 감정 변화 반영
  useEffect(() => {
    const interval = setInterval(async () => {
      if (!webcamRef.current || loading) return; // 로딩 중에는 요청 방지
      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) return;

      try {
        setLoading(true);  

        const result = await predictEmotion(imageSrc, userId, chatroomId);
        const { emotion: newEmotion, confidence: newConfidence } = result;

        // 이전 감정과 비교하여 유의미한 변화 감지
        const isSignificantChange =
          newEmotion !== previousEmotion &&
          Math.abs((previousConfidence || 0) - newConfidence) >= 0.2; // 신뢰도 차이 임계값 0.2

        if (isSignificantChange) {
          setEmotion(newEmotion, newConfidence);
          setPreviousEmotion(newEmotion); 
          setPreviousConfidence(newConfidence); 

          // 신뢰도가 0.7 이상일 때만 챗봇 응답을 보내도록
          if (newConfidence >= 0.7) {
            // 감정 변화에 따른 챗봇 응답 요청
            const { botResponse } = await sendEmotionChatMessage(
              chatroomId,
              ""
            );

            // 챗봇 응답을 채팅창에 추가
            setMessages((prev) => [
              ...prev,
              { user_message: null, bot_response: botResponse },
            ]);
          }
        }
      } catch (error) {
        console.error("감정 인식 실패:", error);
      } finally {
        setLoading(false); 
      }
    }, 5000); // 5초마다 감정 인식

    return () => clearInterval(interval);
  }, [
    userId,
    chatroomId,
    emotion,
    setEmotion,
    previousEmotion,
    previousConfidence,
    loading,
  ]);

  const sendMessage = async () => {
    if (!input.trim() || conversationEnd) return; // 대화 종료된 상태에서는 메시지 전송 불가

    const userMessage = {
      user_id: userId,
      user_message: input,
      bot_response: "응답 대기 중...",
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      // 기존의 sendMessageToBot → sendEmotionChatMessage로 변경
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
      console.log("대화 종료 API 응답:", response);
      if (response) {
        setConversationEnd(true);
        alert("대화가 종료되었습니다.");
        setSelectedChatroom(null);
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
            placeholder="메시지를 입력하세요..."
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            disabled={conversationEnd}
          />
          <Button onClick={sendMessage} disabled={conversationEnd}>
            전송
          </Button>
        </InputContainer>
        <InputContainer>
          <EndButton onClick={handleEndConversation} disabled={conversationEnd}>
            대화 종료하기
          </EndButton>
        </InputContainer>
      </ChatBox>

      {/* 웹캠 화면 */}
      <WebcamContainer>
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          videoConstraints={{ facingMode: "user" }}
          // style={{ display: "none" }}
          style={{ display: "block", width: "100%", borderRadius: "10px" }}
        />
      </WebcamContainer>

      {/* 감정 상태 표시 */}
      {emotion && (
        <div>
          <p style={{ fontSize: "18px", fontWeight: "bold" }}>
            현재 감정: {emotion}
          </p>
          <p>신뢰도: {confidence}%</p>
        </div>
      )}
    </div>
  );
};

export default ChatRoomDetail;
