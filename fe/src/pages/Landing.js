import React from 'react';
import styled, { keyframes } from 'styled-components';

// 텍스트가 커지는 애니메이션
const growAnimation = keyframes`
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
`;

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;  
  justify-content: center;
  height: 40vh;
`;

const Heading = styled.h1`
  font-size: 50px; 
  margin-bottom: 20px;
  animation: ${growAnimation} 1.5s ease-out; 
`;

const Text = styled.p`
  font-size: 24px;
  animation: ${growAnimation} 2s ease-out 0.5s; 
`;

const Landing = () => {
  return (
    <Container>
      <Heading>환영합니다!</Heading>
      <Text>로그인하거나 회원가입 해야 홈으로 들어가집니다.</Text>
    </Container>
  );
};

export default Landing;
