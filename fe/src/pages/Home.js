import React, { useEffect } from 'react';
import useAuthStore from '../store/authStore';
// import { logout } from '../api/auth';
import styled from 'styled-components';
// import Button from '../components/Button';
import { useNavigate} from "react-router-dom";
// import { useNavigate, Link } from "react-router-dom";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;  
  justify-content: center;
  height: 40vh;
`;

// const Button = styled.button`
//   margin-top: 10px;
//   padding: 10px 20px;
//   font-size: 16px;
//   cursor: pointer;
//   border: none;
//   border-radius: 5px;
//   background-color: #007bff;
//   color: white;
//   transition: background 0.3s;

//   &:hover {
//     background-color: #0056b3;
//   }
// `;

const Home = () => {
  const { isAuthenticated} = useAuthStore();
  // const { isAuthenticated, logout: setLogout } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // const handleLogout = async () => {
  //   try {
  //     await logout();
  //     setLogout(); // Zustand 상태 변경
  //     navigate('/login');
  //   } catch (error) {
  //     alert('로그아웃 실패: ' + (error.response?.data?.error || '서버 오류'));
  //   }
  // };

  return (
    <Container>
      <h1>홈 화면</h1>
      <p>채팅, 달력(다이어리), 설정</p>

      {/* 챗봇 페이지로 이동하는 버튼 */}
      {/* <Link to="/chat">
        <Button>챗봇 시작</Button>
      </Link> */}
    </Container>
  );
};

export default Home;