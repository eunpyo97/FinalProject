import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api/auth";
import useAuthStore from "../store/authStore";
import styled from "styled-components";
import Spinner from "../components/Spinner";

const Title = styled.h2`
  margin-bottom: 30px;
  font-size: 30px;
  font-weight: bold;
  color: rgb(3, 69, 135);
  text-shadow: 2px 2px 0px rgba(0, 0, 0, 0.2), 4px 4px 0px rgba(0, 0, 0, 0.15);
  letter-spacing: 1px;
`;

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 75vh;
`;

const Input = styled.input`
  width: 280px;
  padding: 12px;
  margin: 8px 0;
  border: 1px solid rgba(199, 229, 248, 0.5);
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease-in-out;
  box-shadow: inset 0px 2px 5px rgba(0, 0, 0, 0.05);

  &:hover {
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.15);
    transform: scale(1.02);
  }

  &:focus {
    outline: none;
    border-color: #3498db;
    background: white;
    box-shadow: 0px 0px 10px rgba(52, 152, 219, 0.5);
    transform: scale(1.03);
  }
`;

const CheckboxContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 15px;
  font-size: 14px;
  color: #555;
  transition: all 0.3s ease-in-out;

  &:hover {
    color: #333;
    transform: scale(1.02);
  }
`;

const ForgotPassword = styled.p`
  margin-top: 10px;
  font-size: 14px;
  color: #3498db;
  cursor: pointer;
  transition: all 0.3s ease-in-out;

  &:hover {
    color: #217dbb;
    text-decoration: underline;
    transform: translateX(2px);
  }
`;

const LoginButtonWrapper = styled.div`
  width: 280px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 15px;
`;

const LoginButton = styled.button`
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 8px;
  background: linear-gradient(to right, #3498db, #2980b9);
  color: white;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
  position: relative;
  overflow: hidden;

  &:hover {
    background: linear-gradient(to right, #2980b9, #217dbb);
    box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.3);
    transform: scale(1.05);
  }

  &:active {
    transform: scale(0.98);
    box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.2);
  }

  &:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
    box-shadow: none;
    opacity: 0.7;
  }

  &::before {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 150%;
    height: 150%;
    background: rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease-in-out;
    transform: translate(-50%, -50%) scale(0);
    border-radius: 50%;
  }

  &:hover::before {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0;
  }
`;

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const { setLogin } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      setIsLoading(true);

      console.log("[DEBUG] 로그인 요청 시작", { email, password, rememberMe });

      const response = await login(email, password, rememberMe);

      console.log("[DEBUG] 로그인 성공, 응답 데이터:", response);

      // Zustand 상태 업데이트 (user_id 포함)
      setLogin(response.user_id, response.access_token, rememberMe);

      alert("로그인 성공! 홈 화면으로 이동합니다.");
      navigate("/home");
    } catch (error) {
      alert("로그인 실패: " + (error.response?.data?.error || "서버 오류"));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container>
      <Title>로그인</Title>
      <Input
        type="email"
        placeholder="이메일"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <Input
        type="password"
        placeholder="비밀번호"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <LoginButtonWrapper>
        <LoginButton onClick={handleLogin} disabled={isLoading}>
          {isLoading ? <Spinner /> : "로그인"}
        </LoginButton>
      </LoginButtonWrapper>
      <CheckboxContainer>
        <input
          type="checkbox"
          checked={rememberMe}
          onChange={(e) => setRememberMe(e.target.checked)}
        />
        <label>로그인 유지</label>
      </CheckboxContainer>

      <ForgotPassword onClick={() => navigate("/forgot-password")}>
        비밀번호를 잊으셨나요?
      </ForgotPassword>
    </Container>
  );
};

export default Login;
