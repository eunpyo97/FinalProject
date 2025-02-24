import React, { useState} from "react";
import ChatList from "./ChatList";
import ChatRoomDetail from "./ChatRoomDetail";
import styled from "styled-components";

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
`;

const Chat = ({ userId }) => {
  const [selectedChatroom, setSelectedChatroom] = useState(null);

  return (
    <ChatContainer>
      {!selectedChatroom ? (
        <ChatList userId={userId} setSelectedChatroom={setSelectedChatroom} />
      ) : (
        <ChatRoomDetail userId={userId} chatroomId={selectedChatroom} setSelectedChatroom={setSelectedChatroom} />
      )}
    </ChatContainer>
  );
};

export default Chat;
