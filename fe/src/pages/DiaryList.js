import React from "react";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";

const DiaryListWrapper = styled.div`
  margin-top: 50px;
  padding: 15px;
  width: 90%;
  max-width: 500px;
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
  background:rgb(203, 230, 255);
  border: 1px solidrgb(255, 255, 255);
  padding: 12px;
  margin-bottom: 10px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;

  &:hover {
    background-color:rgb(147, 201, 255);
  }

  span {
    font-weight: bold;
    color: rgb(255, 255, 255);
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
            <DiaryItem key={entry.id} onClick={() => handleDiaryClick(entry.id)}>
              {entry.emoji} <span>📆 {entry.timestamp}</span>
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
