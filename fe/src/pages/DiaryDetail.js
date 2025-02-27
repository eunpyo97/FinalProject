import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import styled from "styled-components";
import { getDiaryDetail } from "../api/diary";
import { getEmotionIcon } from "../components/Emoji";
// import { createGlobalStyle } from "styled-components";

// const GlobalStyle = createGlobalStyle`
//   @import url('https://fonts.googleapis.com/css2?family=Dongle&display=swap');
// `;

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 30px;
  background: linear-gradient(to bottom, rgb(222, 237, 252), #ffffff);
  min-height: 100vh;
  width: 100%;
  position: absolute;
  left: 0;
`;

const Card = styled.div`
  background-color: #ffffff;
  padding: 25px;
  border-radius: 20px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  width: 90%;
  max-width: 500px;
  text-align: center;
  transition: all 0.3s ease;
  margin-top: 20px;

  &:hover {
    box-shadow: 0 4px 10px rgb(5, 95, 155);
  }
`;

const HeaderWrapper = styled.div`
  width: 100%;
  display: flex;
  justify-content: space-between; /* 왼쪽(버튼) ↔ 오른쪽(날짜) */
  align-items: center;
`;

const BackButton = styled.button`
  background-color: #ffb6c1;
  color: #ffffff;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.3s ease-in-out;

  &:hover {
    background-color: #ff9aa2;
    transform: scale(1.05);
  }
`;

const Title = styled.h1`
  font-size: 30px;
  font-family: "Dongle", sans-serif;
  color: #ff6b81;/
  margin-top: 40px;
  margin-bottom: 15px;
`;

const DateText = styled.p`
  font-size: 14px;
  color: #777;
  font-weight: bold;
  margin-bottom: 10px;
`;

const Content = styled.p`
  font-size: 20px;
  color: #444;
  line-height: 1.8;
  font-family: "Dongle", sans-serif;
  white-space: pre-line;
  margin: 40px 0;
  padding: 20px;
`;

const EmotionContainer = styled.div`
  font-size: 18px;
  font-weight: bold;
  color: #ff4757;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 15px;
`;

const EmotionIcon = styled.span`
  font-size: 26px;
`;

const DiaryDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [diary, setDiary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDiary = async () => {
      try {
        const data = await getDiaryDetail(id);
        setDiary(data);
      } catch (err) {
        console.error("일기 불러오기 실패:", err);
        setError("일기 정보를 불러오는 데 실패했습니다.");
      } finally {
        setLoading(false);
      }
    };
    fetchDiary();
  }, [id]);

  const handleGoBack = () => {
    navigate(-1);
  };

  return (
    <Container>
      {loading ? (
        <p>불러오는 중...</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <Card>
          <HeaderWrapper>
            <BackButton onClick={handleGoBack}>뒤로 가기</BackButton>
            <DateText>{diary.date}</DateText>
          </HeaderWrapper>

          <Title>{diary.title ? diary.title : "오늘의 일기"}</Title>
          <EmotionContainer>
            <EmotionIcon>{getEmotionIcon(diary.emotion)}</EmotionIcon>
            <span>{diary.emotion}</span>
          </EmotionContainer>
          <Content>{diary.content}</Content>
        </Card>
      )}
    </Container>
  );
};

export default DiaryDetail;
