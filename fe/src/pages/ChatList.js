import React, { useState, useEffect } from "react";
import { getUserChatHistory, createChatroom } from "../api/chat";
import { getEmotionResults } from "../api/emotion";
import styled from "styled-components";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import "dayjs/locale/ko";
import { getEmotionIcon } from "../components/Emoji";
import { BeatLoader } from "react-spinners";
dayjs.extend(relativeTime);
dayjs.locale("ko");

const ChatListBox = styled.div`
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
  height: 650px;
`;

const ChatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgb(176, 213, 255);
  padding: 15px;
  font-size: 25px;
  font-weight: bold;
  color: white;
  border-bottom: 4px solid #ffffff;
  border-radius: 15px 15px 0 0;
  width: 100%;
`;

const ChatListContainer = styled.div`
  padding: 20px;
  height: 100%;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #a3c6ed #f0f0f0;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;

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

const ChatRoomItem = styled.div`
  width: 100%;
  padding: 15px;
  border-bottom: 1px solid #ddd;
  cursor: pointer;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  transition: background-color 0.3s ease, transform 0.3s ease;
  &:hover {
    background-color: rgb(171, 215, 253);
    transform: scale(1.02);
  }
  span {
    transition: font-size 0.3s ease, color 0.3s ease;
  }
  &:hover span:first-child {
    font-size: 1.5em;
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: flex-start;
  align-items: center;
  height: 100%;
  width: 100%;
  flex-direction: column;
  padding-top: 60px;
`;

const CreateChatButton = styled.button`
  margin: 10px;
  padding: 12px 20px;
  background-color: rgb(102, 185, 252);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.3s ease, transform 0.3s ease;
  &:hover {
    background-color: rgb(48, 162, 255);
    transform: scale(1.05);
  }
`;

const LoadingText = styled.div`
  margin-top: 20px;
  font-size: 18px;
  color: #666;
  text-align: center;
`;

const ChatList = ({ userId, setSelectedChatroom }) => {
  const [chatrooms, setChatrooms] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const fetchChatrooms = async () => {
      try {
        const rooms = await getUserChatHistory(userId);
        const updatedRooms = await Promise.all(
          rooms.map(async (room) => {
            try {
              const emotionData = await getEmotionResults(room.chatroom_id);
              return {
                ...room,
                emotion: emotionData?.most_common?.emotion || "default",
              };
            } catch (error) {
              console.error(
                `채팅방(${room.chatroom_id}) 감정 데이터 불러오기 실패:`,
                error
              );
              return { ...room, emotion: "default" };
            }
          })
        );
        setChatrooms(updatedRooms);
        setLoading(false);
      } catch (error) {
        console.error("채팅방 목록 불러오기 실패:", error);
        setLoading(false);
      }
    };
    fetchChatrooms();
  }, [userId]);

  const handleCreateChatroom = async () => {
    try {
      const newRoomId = await createChatroom();
      setChatrooms((prev) => [
        ...prev,
        {
          chatroom_id: newRoomId,
          timestamp: dayjs().format("YYYY-MM-DD HH:mm"),
          conversation_end: false,
          emotion: "default",
        },
      ]);
      setSelectedChatroom(newRoomId);
    } catch (error) {
      console.error("채팅방 생성 실패:", error);
    }
  };

  const formatLastActive = (updatedAt) => {
    if (!updatedAt) return "";
    return `최근 대화: ${dayjs(updatedAt).fromNow()}`;
  };

  return (
    <ChatListBox>
      <ChatHeader>대화 목록</ChatHeader>
      <CreateChatButton onClick={handleCreateChatroom}>
        + 새 대화하기
      </CreateChatButton>

      {/* 로딩 상태일 때만 로딩 스피너와 텍스트 표시 */}
      {loading ? (
        <LoadingContainer>
          {/* <ClipLoader size={50} color="#36D7B7" /> */}
          <BeatLoader size={50} color="#5f71f5" />
          <LoadingText>채팅 목록을 불러오는 중입니다...</LoadingText>
        </LoadingContainer>
      ) : (
        <ChatListContainer>
          {chatrooms.map((room) => (
            <ChatRoomItem
              key={room.chatroom_id}
              onClick={() => setSelectedChatroom(room.chatroom_id)}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span>{getEmotionIcon(room.emotion)} </span>
                <span style={{ marginLeft: "10px", textAlign: "right" }}>
                  {dayjs(room.timestamp).format("YYYY-MM-DD HH:mm")} /{" "}
                  {formatLastActive(room.updated_at)}{" "}
                  {room.conversation_end ? "종료된 대화" : "진행중인 대화"}
                </span>
              </div>
            </ChatRoomItem>
          ))}
        </ChatListContainer>
      )}
    </ChatListBox>
  );
};

export default ChatList;
