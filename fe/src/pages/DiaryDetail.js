import React from "react";
import { useParams, useNavigate } from "react-router-dom"; 
import styled from "styled-components";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background-color: #f0f8ff; 
  min-height: 50vh;
`;

const DiaryCard = styled.div`
  background-color: #fff;
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
  text-align: center;
`;

const Title = styled.h1`
  font-size: 32px;
  color:rgb(52, 184, 255); 
  margin-bottom: 20px;
`;

const Content = styled.p`
  font-size: 18px;
  color: #333;
  line-height: 1.6;
  margin-bottom: 20px;
  text-align: left;
`;

const BackButton = styled.button`
  background-color:rgb(189, 226, 255);  
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 20px;
  
  &:hover {
    background-color:rgb(125, 196, 251); 
  }
`;

const DiaryDetail = () => {
  const { id } = useParams(); // URL에서 다이어리 ID 가져오기
  const navigate = useNavigate(); 

  const handleGoBack = () => {
    navigate(-1); 
  };

  return (
    <Container>
      <DiaryCard>
        <Title>다이어리 상세페이지 - {id}</Title>
        <Content>대화 요약한 내용 불러오기</Content>
        <BackButton onClick={handleGoBack}>뒤로 가기</BackButton>
      </DiaryCard>
    </Container>
  );
};

export default DiaryDetail;
