import React from "react";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";

const DiaryEmoji = styled.span`
  font-size: 15px;
  transition: transform 0.3s ease-in-out;

  &:active {
    transform: scale(1.4);
  }

  @keyframes shake {
    0% {
      transform: rotate(-10deg);
    }
    100% {
      transform: rotate(10deg);
    }
  }
`;

const DiaryListWrapper = styled.div`
  margin-top: 40px;
  padding: 15px;
  width: 90%;
  min-width: 430px;
  max-width: 800px;
  background: white;
  border-radius: 10px;
  box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.1);
  text-align: center;

  h3 {
    color: #333;
    margin-bottom: 10px;
  }
`;

const DiaryList = styled.ul`
  padding: 0;
  list-style: none;
`;

const DiaryItem = styled.li`
  background: rgb(203, 230, 255);
  border: 1px solid rgb(224, 227, 248);
  padding: 12px;
  margin-bottom: 10px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.1),
    -5px -5px 15px rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease-in-out;

  &:hover {
    background: rgb(147, 201, 255);
    transform: translateY(-5px);
    box-shadow: 8px 8px 20px rgba(0, 0, 0, 0.15),
      -8px -8px 20px rgba(255, 255, 255, 0.8);
  }

  &:hover ${DiaryEmoji} {
    transform: scale(1.5);
    animation: shake 0.4s ease-in-out infinite alternate;
  }
`;

const DiaryListPage = ({ selectedDate, diaryEntries }) => {
  const navigate = useNavigate();

  const handleDiaryClick = (entryId) => {
    navigate(`/diary/${entryId}`);
  };

  return (
    <DiaryListWrapper>
      <h3>{selectedDate}의 일기 목록</h3>
      <DiaryList>
        {diaryEntries.length > 0 ? (
          diaryEntries.map((entry) => (
            <DiaryItem
              key={entry.id}
              onClick={() => handleDiaryClick(entry.id)}
            >
              <DiaryEmoji>{entry.emoji}</DiaryEmoji>
              <span>📆 {entry.timestamp}</span>
            </DiaryItem>
          ))
        ) : (
          <p>작성된 일기가 없습니다.</p>
        )}
      </DiaryList>
    </DiaryListWrapper>
  );
};

export default DiaryListPage;
