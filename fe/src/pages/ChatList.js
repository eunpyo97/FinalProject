import React, { useState, useEffect } from "react";
import { getUserChatHistory, createChatroom } from "../api/chat";
import styled from "styled-components";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import "dayjs/locale/ko";

dayjs.extend(relativeTime);
dayjs.locale("ko");

const ChatListBox = styled.div`
  width: 100%;
  max-width: 430px;
  border: 2px solid #eeeeee;
  border-radius: 15px;
  background-color: white;
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.22);
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const ChatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: center; 
  background-color: #f4f4f4;
  padding: 10px;
  font-size: 18px;
  border-bottom: 4px solid white;
  width: 100%;
`;

const ChatListContainer = styled.div`
  padding: 20px;
  height: 520px;
  overflow-y: auto;
  scrollbar-width: thin;
  width: 100%;
  &::-webkit-scrollbar {
    display: block;
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
  &:hover {
    background-color: #f1f1f1;
  }
`;

const CreateChatButton = styled.button`
  margin: 10px;
  padding: 10px 15px;
  background-color: #a3c6ed;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  &:hover {
    background-color: rgb(90, 161, 242);
  }
`;

const ChatList = ({ userId, setSelectedChatroom }) => {
  const [chatrooms, setChatrooms] = useState([]);

  useEffect(() => {
    const fetchChatrooms = async () => {
      try {
        const rooms = await getUserChatHistory(userId);
        setChatrooms(rooms);
      } catch (error) {
        console.error("채팅방 목록 불러오기 실패:", error);
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
              <span>😐</span>
              <span style={{ marginLeft: "10px", textAlign: "right" }}>
                {dayjs(room.timestamp).format("YYYY-MM-DD HH:mm")} /{" "}
                {formatLastActive(room.updated_at)}{" "}
                {room.conversation_end ? "종료된 대화" : "진행중인 대화"}
              </span>
            </div>
          </ChatRoomItem>
        ))}
      </ChatListContainer>
    </ChatListBox>
  );
};

export default ChatList;
