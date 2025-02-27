import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";  
import useAuthStore from "../store/authStore";
import styled from "styled-components";

const Nav = styled.nav`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: #f8f9fa;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
  box-shadow: ${({ scrolled }) => (scrolled ? "0 4px 6px rgba(0, 0, 0, 0.1)" : "none")};
`;

const Logo = styled(Link)`
  font-weight: bold;
  font-size: 20px;
  text-decoration: none;
  color: black;
  margin-right: 40px;
  &:hover {
    color: rgb(148, 201, 253);
    transform: scale(1.2);
  }
`;

const NavContainer = styled.div`
  display: flex;
  align-items: center;
  flex-grow: 1;
`;

const MenuLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 30px;
`;

const MenuRight = styled.div`
  margin-left: auto;
  display: flex;
  gap: 20px;
`;

const StyledLink = styled(Link)`
  text-decoration: none;
  color: black;
  font-size: 16px;
  transition: font-size 0.3s ease, color 0.3s ease;
  &:hover {
    color: rgb(148, 201, 253);
    transform: scale(1.1); 
  }
`;

const StyledButton = styled.button`
  all: unset;
  border: none;
  color: black;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  margin-right: 20px;
  text-decoration: none;
  outline: none;
  transition: font-size 0.3s ease, color 0.3s ease;
  &:hover {
    color: rgb(255, 114, 96);
    background: none;
    transform: scale(1.1);
  }
`;

const SignupLink = styled(Link)`
  margin-right: 20px;
  text-decoration: none;
  color: black;
  font-size: 16px;
  transition: font-size 0.3s ease, color 0.3s ease;
  &:hover {
    color: rgb(148, 201, 253);
    transform: scale(1.1);
  }
`;

const Navbar = () => {
  const { isAuthenticated, logout } = useAuthStore();
  const [scrolled, setScrolled] = useState(false);
  const navigate = useNavigate();  

  // 스크롤 이벤트 핸들러
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 50) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate("/");  
  };

  return (
    <Nav scrolled={scrolled}>
      <NavContainer>
        {/* 왼쪽 로고 */}
        <Logo to={isAuthenticated ? "/home" : "/"}>RobotPet</Logo>
        {/* 로그인 후 메뉴 */}
        {isAuthenticated && (
          <MenuLeft>
            <StyledLink to="/chat">챗봇</StyledLink>
            <StyledLink to="/calendar">캘린더</StyledLink>
          </MenuLeft>
        )}
      </NavContainer>
      {/* 오른쪽 메뉴 */}
      {isAuthenticated ? (
        <MenuRight>
          <StyledButton onClick={handleLogout}>로그아웃</StyledButton>
        </MenuRight>
      ) : (
        <MenuRight>
          <StyledLink to="/login">로그인</StyledLink>
          <SignupLink to="/signup">회원가입</SignupLink>
        </MenuRight>
      )}
    </Nav>
  );
};

export default Navbar;
