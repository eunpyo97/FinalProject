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

const ChatListWrapper = styled.div`
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

const ChatListBox = styled.div`
  width: 100%;
  max-width: 430px;
  border: 2px solid #e0e0e0;
  border-radius: 20px;
  background-color: rgb(255, 255, 255);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1), 0 6px 6px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 650px;
  overflow: hidden;
  box-sizing: border-box;
`;

const ChatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(120deg, rgb(106, 159, 251), rgb(205, 98, 250));
  padding: 15px;
  font-size: 25px;
  font-weight: bold;
  color: rgb(255, 255, 255);
  text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
  border-bottom: 4px solid rgba(255, 255, 255, 0.5);
  border-radius: 15px 15px 0 0;
  width: 100%;
  position: relative;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
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
  justify-content: flex-start;
  align-items: stretch;

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
  margin-bottom: 10px;
  border-radius: 12px;
  cursor: pointer;
  background-color: rgb(216, 242, 251);
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease, transform 0.2s ease,
    box-shadow 0.2s ease;

  &:hover {
    background-color: rgb(113, 197, 254);
    transform: translateY(-5px) rotateX(3deg);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
  }

  &:active {
    transform: scale(0.95);
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
    background-color: rgb(111, 188, 251);
    transition: transform 0.1s ease;
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
  margin: 20px 0 10px 0;
  padding: 12px 20px;
  background-color: rgb(131, 199, 254);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.3s ease, transform 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);

  &:hover {
    background-color: rgb(48, 162, 255);
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.25);
  }

  &:active {
    transform: translateY(3px) scale(0.97);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
    background-color: rgb(38, 140, 220);
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
        setLoading(true);

        // 캐시된 데이터 확인
        const cachedData = localStorage.getItem(`chatrooms-${userId}`);
        if (cachedData) {
          setChatrooms(JSON.parse(cachedData));
        }

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

        updatedRooms.sort(
          (a, b) => new Date(b.updated_at) - new Date(a.updated_at)
        );

        // 상태 업데이트 및 캐싱
        setChatrooms(updatedRooms);
        localStorage.setItem(
          `chatrooms-${userId}`,
          JSON.stringify(updatedRooms)
        );
      } catch (error) {
        console.error("채팅방 목록 불러오기 실패:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchChatrooms();
  }, [userId]); // userId가 변경될 때마다 실행

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

  return (
    <ChatListWrapper>
      <ChatListBox>
        <ChatHeader>대화 목록</ChatHeader>
        <CreateChatButton
          onClick={() => {
            setTimeout(() => {
              handleCreateChatroom();
            }, 300);
          }}
        >
          + 새 대화하기
        </CreateChatButton>

        {/* 로딩 상태일 때만 로딩 스피너와 텍스트 표시 */}
        {loading ? (
          <LoadingContainer>
            <BeatLoader size={50} color="#5f71f5" />
            <LoadingText>채팅 목록을 불러오는 중입니다...</LoadingText>
          </LoadingContainer>
        ) : (
          <ChatListContainer>
            {chatrooms.map((room) => (
              <ChatRoomItem
                key={room.chatroom_id}
                onClick={() => {
                  setTimeout(() => {
                    setSelectedChatroom(room.chatroom_id);
                  }, 300);
                }}
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
                    {room.updated_at
                      ? dayjs(room.updated_at).format("YYYY-MM-DD HH:mm")
                      : "날짜 없음"}{" "}
                    /{room.conversation_end ? "종료된 대화" : "진행중인 대화"}
                  </span>
                </div>
              </ChatRoomItem>
            ))}
          </ChatListContainer>
        )}
      </ChatListBox>
    </ChatListWrapper>
  );
};

export default ChatList;
