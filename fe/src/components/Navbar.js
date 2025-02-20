import React from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import Button from './Button';
import styled from 'styled-components';

const NavbarContainer = styled.nav`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: #333;
  color: white;
`;

const Menu = styled.div`
  display: flex;
  gap: 10px;
`;

const Navbar = () => {
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuthStore();

  return (
    <NavbarContainer>
      <h1 onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>RobotPet</h1>
      <Menu>
        {isAuthenticated ? (
          <>
            <Button onClick={() => navigate('/home')}>홈</Button>
            <Button onClick={logout} style={{ backgroundColor: 'red', color: 'white' }}>로그아웃</Button>
          </>
        ) : (
          <>
            <Button onClick={() => navigate('/login')}>로그인</Button>
            <Button onClick={() => navigate('/signup')}>회원가입</Button>
          </>
        )}
      </Menu>
    </NavbarContainer>
  );
};

export default Navbar;
