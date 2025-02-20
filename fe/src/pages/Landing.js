import React from 'react';
// import { useNavigate } from 'react-router-dom';
// import Button from '../components/Button';
import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;  
  justify-content: center;
  height: 40vh;
`;

const Landing = () => {
  // const navigate = useNavigate();

  return (
    <Container>
      <h1>환영합니다!</h1>
      <p>로그인하거나 회원가입 해야 홈으로 들어가집니다.</p>
      {/* <Button onClick={() => navigate('/login')}>로그인</Button>
      <Button onClick={() => navigate('/signup')} bgColor="green" hoverColor="darkgreen">회원가입</Button> */}
    </Container>
  );
};

export default Landing;
