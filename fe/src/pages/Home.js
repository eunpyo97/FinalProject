import React, { useEffect } from 'react';
import useAuthStore from '../store/authStore';
import styled from 'styled-components';
import { useNavigate } from "react-router-dom";
// import Navbar from './../components/Navbar';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;  
  justify-content: center;
  height: 40vh;
`;

const Home = () => {
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  return (
    <Container>
      <h1>홈 화면</h1>
      <p>챗봇, 달력을 Navbar로 옮겨서.....</p>
    </Container>
  );
};

export default Home;